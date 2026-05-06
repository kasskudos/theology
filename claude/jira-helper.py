#!/usr/bin/env python3
"""
Jira Helper Script for Claude Code
Reads credentials from environment variables (JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN, etc.)
Supports ADF (Atlassian Document Format) with v3 API (preferred) and v2 fallback
"""

import sys
import json
import re
import os
from urllib.parse import quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from base64 import b64encode


def read_jira_config():
    """Read Jira configuration from environment variables"""
    url = os.environ.get('JIRA_BASE_URL')
    email = os.environ.get('JIRA_EMAIL')
    token = os.environ.get('JIRA_TOKEN')

    if not all([url, email, token]):
        print(json.dumps({"error": "Jira credentials not found. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_TOKEN in ~/.claude/environment"}))
        sys.exit(1)

    config = {
        'url': url,
        'email': email,
        'token': token,
        'default_project': os.environ.get('JIRA_DEFAULT_PROJECT', ''),
        'default_issue_type': os.environ.get('JIRA_DEFAULT_ISSUE_TYPE', 'Task'),
        'epic_field_id': os.environ.get('JIRA_EPIC_FIELD', 'parent'),
        'sprint_field_id': os.environ.get('JIRA_SPRINT_FIELD', ''),
        'story_points_field_id': os.environ.get('JIRA_STORY_POINTS_FIELD', ''),
        'acceptance_criteria_field': os.environ.get('JIRA_ACCEPTANCE_CRITERIA_FIELD', 'customfield_22442'),
    }

    return config


def make_jira_request(config, endpoint, method='GET', data=None):
    """Make a request to Jira API"""
    url = f"{config['url']}{endpoint}"

    credentials = f"{config['email']}:{config['token']}"
    encoded_credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Accept': 'application/json',
    }

    if data:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(data).encode('utf-8')

    request = Request(url, data=data, headers=headers, method=method)

    try:
        with urlopen(request) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data) if response_data else {}
    except HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            error_msg = error_json.get('errorMessages', [])
            if error_msg:
                print(json.dumps({"error": f"Jira API error: {', '.join(error_msg)}"}))
            else:
                print(json.dumps({"error": f"Jira API error: {error_json}"}))
        except Exception:
            print(json.dumps({"error": f"HTTP {e.code}: {error_body}"}))
        sys.exit(1)
    except URLError as e:
        print(json.dumps({"error": f"Connection error: {e.reason}"}))
        sys.exit(1)


def text_to_minimal_adf(text):
    """Convert plain text to minimal ADF document structure."""
    if not text or not text.strip():
        return {"version": 1, "type": "doc", "content": [{"type": "paragraph", "content": []}]}

    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

    adf_content = []
    for para_text in paragraphs:
        adf_content.append({
            "type": "paragraph",
            "content": [
                {"type": "text", "text": para_text}
            ]
        })

    return {
        "version": 1,
        "type": "doc",
        "content": adf_content
    }


def read_adf_from_file(filepath):
    """Read ADF JSON from a file."""
    try:
        with open(filepath, 'r') as f:
            adf = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"Failed to read ADF file {filepath}: {str(e)}"}))
        sys.exit(1)
    for key in ('version', 'type', 'content'):
        if key not in adf:
            print(json.dumps({"error": f"Invalid ADF: missing '{key}' field in {filepath}"}))
            sys.exit(1)
    if adf.get('type') != 'doc':
        print(json.dumps({"error": f"Invalid ADF: type must be 'doc', got '{adf.get('type')}' in {filepath}"}))
        sys.exit(1)
    return adf


def adf_to_plain_text(adf_doc):
    """Extract plain text from an ADF document for v2 fallback."""
    texts = []

    def walk(node):
        if isinstance(node, dict):
            if node.get('type') == 'text':
                texts.append(node.get('text', ''))
            for child in node.get('content', []):
                walk(child)

    walk(adf_doc)
    return '\n\n'.join(texts) if texts else '[No text content]'


def make_jira_request_v3_with_v2_fallback(config, v3_endpoint, v2_endpoint, method, data_v3, data_v2):
    """Make a request to Jira, trying v3 API first (with ADF) then falling back to v2 (with plain text)."""
    url_v3 = f"{config['url']}{v3_endpoint}"
    url_v2 = f"{config['url']}{v2_endpoint}"

    credentials = f"{config['email']}:{config['token']}"
    encoded_credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    # Try v3 first with ADF
    try:
        data_json = json.dumps(data_v3).encode('utf-8')
        request = Request(url_v3, data=data_json, headers=headers, method=method)
        with urlopen(request) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data) if response_data else {}
    except HTTPError as e:
        # v3 failed, try v2 fallback with plain text
        print(f"[jira-helper] v3 API failed ({e.code}), trying v2 fallback...", file=sys.stderr)
        try:
            data_json = json.dumps(data_v2).encode('utf-8')
            request = Request(url_v2, data=data_json, headers=headers, method=method)
            with urlopen(request) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else {}
        except HTTPError as e_v2:
            error_body = e_v2.read().decode('utf-8')
            try:
                error_json = json.loads(error_body)
                error_msg = error_json.get('errorMessages', [])
                if error_msg:
                    print(json.dumps({"error": f"Jira API error: {', '.join(error_msg)}"}))
                else:
                    print(json.dumps({"error": f"Jira API error: {error_json}"}))
            except Exception:
                print(json.dumps({"error": f"HTTP {e_v2.code}: {error_body}"}))
            sys.exit(1)
        except URLError as e_v2:
            print(json.dumps({"error": f"Connection error: {e_v2.reason}"}))
            sys.exit(1)
    except URLError as e:
        print(json.dumps({"error": f"Connection error: {e.reason}"}))
        sys.exit(1)


def get_current_user_accountid(config):
    """Get the authenticated user's accountId"""
    try:
        result = make_jira_request(config, '/rest/api/2/myself')
        return result.get('accountId')
    except Exception:
        return None


def get_user_accountid(config, email_or_name):
    """Get user accountId from email or display name"""
    try:
        from urllib.parse import quote
        query = quote(email_or_name)
        result = make_jira_request(config, f'/rest/api/2/user/search?query={query}')

        if result and len(result) > 0:
            return result[0].get('accountId')
    except Exception:
        pass

    return email_or_name


def cmd_create_issue(config, args):
    """Create a new Jira issue.

    Usage (plain text description):
        create-issue <project> <summary> <description> <epic_key> [issue_type] [story_points]

    Usage (ADF description):
        create-issue <project> <summary> --adf-file /tmp/adf.json <epic_key> [issue_type] [story_points]

    Optional flags (anywhere after required args):
        --ac-file /tmp/ac.json      ADF file for acceptance criteria (customfield_22442)
        --duedate YYYY-MM-DD        Due date
        --priority <name>           Priority (Highest, High, Medium, Low, Lowest)
    """
    if len(args) < 4:
        print(json.dumps({"error": "Usage: create-issue <project> <summary> <description_or_--adf-file> <epic_key> [issue_type] [story_points]"}))
        sys.exit(1)

    project_key = args[0]
    summary = args[1]

    # Extract optional flags first
    ac_file = None
    duedate = None
    priority = None
    filtered_args = []
    i = 2
    while i < len(args):
        if args[i] == '--ac-file' and i + 1 < len(args):
            ac_file = args[i + 1]
            i += 2
        elif args[i] == '--duedate' and i + 1 < len(args):
            duedate = args[i + 1]
            i += 2
        elif args[i] == '--priority' and i + 1 < len(args):
            priority = args[i + 1]
            i += 2
        else:
            filtered_args.append(args[i])
            i += 1

    args = filtered_args

    # Parse description or ADF file
    description_arg = args[0] if len(args) > 0 else ''
    if description_arg == '--adf-file' and len(args) > 1:
        adf_file = args[1]
        adf_doc = read_adf_from_file(adf_file)
        description_plain = adf_to_plain_text(adf_doc)
        epic_key = args[2] if len(args) > 2 else None
        issue_type = args[3] if len(args) > 3 else config.get('default_issue_type', 'Task')
        story_points = float(args[4]) if len(args) > 4 else None
    else:
        description_plain = description_arg
        adf_doc = text_to_minimal_adf(description_plain)
        epic_key = args[1] if len(args) > 1 else None
        issue_type = args[2] if len(args) > 2 else config.get('default_issue_type', 'Task')
        story_points = float(args[3]) if len(args) > 3 else None

    if not epic_key:
        print(json.dumps({"error": "Epic key is required"}))
        sys.exit(1)

    # Validate epic exists
    try:
        epic_result = make_jira_request(config, f'/rest/api/2/issue/{epic_key}')
        epic_type = epic_result.get('fields', {}).get('issuetype', {}).get('name', '')
        if epic_type.lower() != 'epic':
            print(json.dumps({"error": f"{epic_key} is not an Epic (type: {epic_type})"}))
            sys.exit(1)
    except Exception:
        print(json.dumps({"error": f"Epic {epic_key} not found or inaccessible"}))
        sys.exit(1)

    # Determine which epic field to use
    epic_field = config.get('epic_field_id', 'parent')

    # Base fields
    base_fields = {
        "project": {"key": project_key},
        "summary": summary,
        "issuetype": {"name": issue_type}
    }

    # Add epic based on field type
    if epic_field == 'parent':
        base_fields["parent"] = {"key": epic_key}
    elif epic_field.startswith('customfield_'):
        base_fields[epic_field] = epic_key

    # Add story points if provided and field configured
    if story_points is not None:
        story_points_field = config.get('story_points_field_id')
        if story_points_field:
            base_fields[story_points_field] = story_points

    # Add due date if provided
    if duedate:
        base_fields["duedate"] = duedate

    # Add priority if provided
    if priority:
        base_fields["priority"] = {"name": priority}

    # Add acceptance criteria (customfield_22442) if provided
    ac_adf = None
    ac_plain = None
    if ac_file:
        ac_adf = read_adf_from_file(ac_file)
        ac_plain = adf_to_plain_text(ac_adf)

    # v3 data uses ADF for description
    data_v3 = {"fields": base_fields.copy()}
    data_v3["fields"]["description"] = adf_doc
    if ac_adf:
        data_v3["fields"][config['acceptance_criteria_field']] = ac_adf

    # v2 data uses plain text for description
    data_v2 = {"fields": base_fields.copy()}
    data_v2["fields"]["description"] = description_plain
    if ac_plain:
        data_v2["fields"][config['acceptance_criteria_field']] = ac_plain

    result = make_jira_request_v3_with_v2_fallback(
        config,
        '/rest/api/3/issue',
        '/rest/api/2/issue',
        'POST',
        data_v3,
        data_v2
    )

    print(json.dumps({
        "success": True,
        "issue_key": result.get('key'),
        "issue_id": result.get('id'),
        "url": f"{config['url']}/browse/{result.get('key')}"
    }))


def cmd_get_issue(config, args):
    """Get issue details"""
    if len(args) < 1:
        print(json.dumps({"error": "Usage: get-issue <issue_key>"}))
        sys.exit(1)

    issue_key = args[0]
    result = make_jira_request(config, f'/rest/api/2/issue/{issue_key}')

    fields = result.get('fields', {})

    print(json.dumps({
        "success": True,
        "key": result.get('key'),
        "summary": fields.get('summary'),
        "description": fields.get('description'),
        "status": fields.get('status', {}).get('name'),
        "assignee": fields.get('assignee', {}).get('displayName') if fields.get('assignee') else "Unassigned",
        "reporter": fields.get('reporter', {}).get('displayName'),
        "created": fields.get('created'),
        "updated": fields.get('updated'),
        "priority": fields.get('priority', {}).get('name') if fields.get('priority') else None,
        "issue_type": fields.get('issuetype', {}).get('name'),
        "url": f"{config['url']}/browse/{result.get('key')}"
    }))


def cmd_add_comment(config, args):
    """Add a comment to an issue.

    Usage (plain text comment):
        add-comment <issue_key> <comment_text>

    Usage (ADF comment):
        add-comment <issue_key> --adf-file /tmp/adf.json
    """
    if len(args) < 2:
        print(json.dumps({"error": "Usage: add-comment <issue_key> <comment_text_or_--adf-file>"}))
        sys.exit(1)

    issue_key = args[0]
    comment_arg = args[1]

    if comment_arg == '--adf-file' and len(args) > 2:
        adf_file = args[2]
        adf_doc = read_adf_from_file(adf_file)
        comment_plain = adf_to_plain_text(adf_doc)
    else:
        comment_plain = comment_arg
        adf_doc = text_to_minimal_adf(comment_plain)

    data_v3 = {"body": adf_doc}
    data_v2 = {"body": comment_plain}

    result = make_jira_request_v3_with_v2_fallback(
        config,
        f'/rest/api/3/issue/{issue_key}/comment',
        f'/rest/api/2/issue/{issue_key}/comment',
        'POST',
        data_v3,
        data_v2
    )

    print(json.dumps({
        "success": True,
        "comment_id": result.get('id'),
        "author": result.get('author', {}).get('displayName'),
        "created": result.get('created')
    }))


def cmd_transition_issue(config, args):
    """Transition an issue to a new status"""
    if len(args) < 2:
        print(json.dumps({"error": "Usage: transition-issue <issue_key> <status_name>"}))
        sys.exit(1)

    issue_key = args[0]
    target_status = args[1]

    transitions = make_jira_request(config, f'/rest/api/2/issue/{issue_key}/transitions')

    transition_id = None
    available_transitions = []

    for transition in transitions.get('transitions', []):
        available_transitions.append(transition['name'])
        if transition['name'].lower() == target_status.lower():
            transition_id = transition['id']
            break

    if not transition_id:
        print(json.dumps({
            "error": f"Status '{target_status}' not found. Available transitions: {', '.join(available_transitions)}"
        }))
        sys.exit(1)

    data = {"transition": {"id": transition_id}}
    make_jira_request(config, f'/rest/api/2/issue/{issue_key}/transitions', method='POST', data=data)

    print(json.dumps({
        "success": True,
        "issue_key": issue_key,
        "new_status": target_status
    }))


def cmd_list_transitions(config, args):
    """List available transitions for an issue"""
    if len(args) < 1:
        print(json.dumps({"error": "Usage: list-transitions <issue_key>"}))
        sys.exit(1)

    issue_key = args[0]
    result = make_jira_request(config, f'/rest/api/2/issue/{issue_key}/transitions')

    transitions = [
        {"id": t['id'], "name": t['name']}
        for t in result.get('transitions', [])
    ]

    print(json.dumps({
        "success": True,
        "issue_key": issue_key,
        "transitions": transitions
    }))


def cmd_search(config, args):
    """Search issues using JQL (Jira Query Language)"""
    if len(args) < 1:
        print(json.dumps({"error": "Usage: search <jql_query> [max_results]"}))
        sys.exit(1)

    jql_query = args[0]
    max_results = int(args[1]) if len(args) > 1 else 50

    from urllib.parse import quote
    encoded_jql = quote(jql_query)
    fields = "summary,status,assignee,priority,issuetype,created,updated"
    endpoint = f'/rest/api/3/search/jql?jql={encoded_jql}&maxResults={max_results}&fields={fields}'

    temp_config = config.copy()
    result = make_jira_request(temp_config, endpoint)

    issues = []
    for issue in result.get('issues', []):
        fields = issue.get('fields', {})
        issues.append({
            "key": issue.get('key'),
            "summary": fields.get('summary'),
            "status": fields.get('status', {}).get('name'),
            "assignee": fields.get('assignee', {}).get('displayName') if fields.get('assignee') else "Unassigned",
            "priority": fields.get('priority', {}).get('name') if fields.get('priority') else None,
            "issue_type": fields.get('issuetype', {}).get('name'),
            "created": fields.get('created'),
            "updated": fields.get('updated'),
            "url": f"{config['url']}/browse/{issue.get('key')}"
        })

    print(json.dumps({
        "success": True,
        "total": result.get('total', 0),
        "max_results": max_results,
        "jql": jql_query,
        "issues": issues
    }))


def cmd_update_issue(config, args):
    """Update an issue's fields.

    Usage (plain text):
        update-issue <issue_key> <field> <value> [field2] [value2] ...

    Usage (ADF description):
        update-issue <issue_key> description --adf-file:/tmp/adf.json
    """
    if len(args) < 3:
        print(json.dumps({"error": "Usage: update-issue <issue_key> <field> <value> [field2] [value2] ..."}))
        sys.exit(1)

    issue_key = args[0]

    if len(args[1:]) % 2 != 0:
        print(json.dumps({"error": "Fields and values must be provided in pairs"}))
        sys.exit(1)

    fields_v3 = {}
    fields_v2 = {}
    i = 1
    has_description = False

    while i < len(args):
        field_name = args[i]
        field_value = args[i + 1]

        if field_name == 'description' and field_value.startswith('--adf-file:'):
            has_description = True
            adf_filepath = field_value[len('--adf-file:'):]
            adf_doc = read_adf_from_file(adf_filepath)
            fields_v3['description'] = adf_doc
            fields_v2['description'] = adf_to_plain_text(adf_doc)
        elif field_name in ['summary', 'description']:
            fields_v3[field_name] = field_value
            fields_v2[field_name] = field_value
        elif field_name == 'priority':
            fields_v3['priority'] = {"name": field_value}
            fields_v2['priority'] = {"name": field_value}
        elif field_name == 'assignee':
            if field_value.lower() in ['unassigned', 'none', '']:
                fields_v3['assignee'] = None
                fields_v2['assignee'] = None
            else:
                account_id = get_user_accountid(config, field_value)
                fields_v3['assignee'] = {"accountId": account_id}
                fields_v2['assignee'] = {"accountId": account_id}
        elif field_name == 'labels':
            label_list = field_value.split(',') if ',' in field_value else [field_value]
            fields_v3['labels'] = label_list
            fields_v2['labels'] = label_list
        elif field_name == 'duedate':
            fields_v3['duedate'] = field_value
            fields_v2['duedate'] = field_value
        elif field_name in ['issuetype', 'type']:
            fields_v3['issuetype'] = {"name": field_value}
            fields_v2['issuetype'] = {"name": field_value}
        elif field_name in ['storypoints', 'story_points', 'points']:
            story_points_field = config.get('story_points_field_id')
            if story_points_field:
                fields_v3[story_points_field] = float(field_value)
                fields_v2[story_points_field] = float(field_value)
            else:
                print(json.dumps({"error": "Story Points field not configured. Set JIRA_STORY_POINTS_FIELD in ~/.claude/environment"}))
                sys.exit(1)
        else:
            fields_v3[field_name] = field_value
            fields_v2[field_name] = field_value

        i += 2

    data_v3 = {"fields": fields_v3}
    data_v2 = {"fields": fields_v2}

    if has_description:
        make_jira_request_v3_with_v2_fallback(
            config,
            f'/rest/api/3/issue/{issue_key}',
            f'/rest/api/2/issue/{issue_key}',
            'PUT',
            data_v3,
            data_v2
        )
    else:
        make_jira_request(config, f'/rest/api/2/issue/{issue_key}', method='PUT', data=data_v2)

    print(json.dumps({
        "success": True,
        "issue_key": issue_key,
        "updated_fields": list(fields_v2.keys())
    }))


def cmd_get_sprint_field(config, args):
    """Discover the sprint custom field ID from an issue in a sprint"""
    if len(args) < 1:
        print(json.dumps({"error": "Usage: get-sprint-field <issue_key>"}))
        sys.exit(1)

    issue_key = args[0]
    result = make_jira_request(config, f'/rest/api/2/issue/{issue_key}')

    fields = result.get('fields', {})
    sprint_fields = []

    for field_id, field_value in fields.items():
        if field_id.startswith('customfield_') and field_value:
            if isinstance(field_value, list) and len(field_value) > 0:
                if isinstance(field_value[0], dict) and 'id' in field_value[0] and 'name' in field_value[0]:
                    sprint_fields.append({
                        "field_id": field_id,
                        "value": field_value
                    })

    if not sprint_fields:
        print(json.dumps({
            "error": "No sprint custom fields found in this issue. Try an issue that's currently in a sprint."
        }))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "issue_key": issue_key,
        "sprint_fields": sprint_fields
    }))


def cmd_get_issue_sprints(config, args):
    """Get sprints for an issue"""
    if len(args) < 2:
        print(json.dumps({"error": "Usage: get-issue-sprints <issue_key> <sprint_field_id>"}))
        sys.exit(1)

    issue_key = args[0]
    sprint_field_id = args[1]

    result = make_jira_request(config, f'/rest/api/2/issue/{issue_key}')
    sprint_data = result.get('fields', {}).get(sprint_field_id)

    if not sprint_data:
        print(json.dumps({"success": True, "issue_key": issue_key, "sprints": []}))
        return

    sprints = []
    if isinstance(sprint_data, list):
        for sprint in sprint_data:
            if isinstance(sprint, dict):
                sprints.append({
                    "id": sprint.get('id'),
                    "name": sprint.get('name'),
                    "state": sprint.get('state'),
                    "board_id": sprint.get('boardId')
                })

    print(json.dumps({
        "success": True,
        "issue_key": issue_key,
        "sprint_field_id": sprint_field_id,
        "sprints": sprints
    }))


def cmd_add_to_sprint(config, args):
    """Add an issue to a sprint"""
    if len(args) < 3:
        print(json.dumps({"error": "Usage: add-to-sprint <issue_key> <sprint_field_id> <sprint_id>"}))
        sys.exit(1)

    issue_key = args[0]
    sprint_field_id = args[1]
    sprint_id = int(args[2])

    data = {"fields": {sprint_field_id: sprint_id}}
    make_jira_request(config, f'/rest/api/2/issue/{issue_key}', method='PUT', data=data)

    print(json.dumps({
        "success": True,
        "issue_key": issue_key,
        "sprint_id": sprint_id,
        "message": f"Issue {issue_key} added to sprint {sprint_id}"
    }))


def cmd_remove_from_sprint(config, args):
    """Remove an issue from sprint"""
    if len(args) < 2:
        print(json.dumps({"error": "Usage: remove-from-sprint <issue_key> <sprint_field_id>"}))
        sys.exit(1)

    issue_key = args[0]
    sprint_field_id = args[1]

    data = {"fields": {sprint_field_id: None}}
    make_jira_request(config, f'/rest/api/2/issue/{issue_key}', method='PUT', data=data)

    print(json.dumps({
        "success": True,
        "issue_key": issue_key,
        "message": f"Issue {issue_key} removed from sprint"
    }))


def cmd_list_open_sprints(config, args):
    """List open sprints in a project"""
    if len(args) < 2:
        print(json.dumps({"error": "Usage: list-open-sprints <project_key> <sprint_field_id>"}))
        sys.exit(1)

    project_key = args[0]
    sprint_field_id = args[1]

    from urllib.parse import quote
    jql = f"project={project_key} AND sprint in openSprints()"
    result = make_jira_request(config, f'/rest/api/3/search/jql?jql={quote(jql)}&fields={sprint_field_id}&maxResults=100')

    sprints = {}
    for issue in result.get('issues', []):
        field_value = issue.get('fields', {}).get(sprint_field_id)
        if field_value and isinstance(field_value, list):
            for sprint in field_value:
                if isinstance(sprint, dict) and sprint.get('state') in ['active', 'future']:
                    sprint_id = sprint.get('id')
                    if sprint_id not in sprints:
                        sprints[sprint_id] = {
                            "id": sprint_id,
                            "name": sprint.get('name'),
                            "state": sprint.get('state'),
                            "board_id": sprint.get('boardId')
                        }

    print(json.dumps({
        "success": True,
        "project": project_key,
        "sprint_field_id": sprint_field_id,
        "total_issues_in_sprints": result.get('total', 0),
        "open_sprints": list(sprints.values())
    }))


def cmd_get_epic_field(config, args):
    """Discover the epic field from an issue with an epic"""
    if len(args) < 1:
        print(json.dumps({"error": "Usage: get-epic-field <issue_key>"}))
        sys.exit(1)

    issue_key = args[0]
    result = make_jira_request(config, f'/rest/api/2/issue/{issue_key}')

    fields = result.get('fields', {})
    epic_info = {}

    if 'parent' in fields and fields['parent']:
        parent = fields['parent']
        epic_info['field'] = 'parent'
        epic_info['epic_key'] = parent.get('key')
        epic_info['epic_summary'] = parent.get('fields', {}).get('summary')
        epic_info['epic_type'] = parent.get('fields', {}).get('issuetype', {}).get('name')

    for key, value in fields.items():
        if key.startswith('customfield_') and value:
            if isinstance(value, str) and '-' in value:
                if not epic_info or epic_info.get('field') == 'parent':
                    epic_info['epic_link_field'] = key
                    epic_info['epic_link_value'] = value

    if not epic_info:
        print(json.dumps({"error": "No epic field found. Try an issue that belongs to an epic."}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "issue_key": issue_key,
        "epic_info": epic_info
    }))


def cmd_get_issue_epic(config, args):
    """Get the epic for an issue"""
    if len(args) < 1:
        print(json.dumps({"error": "Usage: get-issue-epic <issue_key>"}))
        sys.exit(1)

    issue_key = args[0]
    epic_field = config.get('epic_field_id', 'parent')

    result = make_jira_request(config, f'/rest/api/2/issue/{issue_key}')
    fields = result.get('fields', {})

    epic_data = None
    if epic_field == 'parent' and 'parent' in fields:
        parent = fields['parent']
        epic_data = {
            "key": parent.get('key'),
            "summary": parent.get('fields', {}).get('summary'),
            "type": parent.get('fields', {}).get('issuetype', {}).get('name')
        }
    elif epic_field.startswith('customfield_'):
        epic_key = fields.get(epic_field)
        if epic_key:
            epic_result = make_jira_request(config, f'/rest/api/2/issue/{epic_key}')
            epic_data = {
                "key": epic_key,
                "summary": epic_result.get('fields', {}).get('summary'),
                "type": epic_result.get('fields', {}).get('issuetype', {}).get('name')
            }

    print(json.dumps({
        "success": True,
        "issue_key": issue_key,
        "epic": epic_data
    }))


def cmd_get_story_points_field(config, args):
    """Discover the story points custom field"""
    if len(args) < 1:
        print(json.dumps({"error": "Usage: get-story-points-field <issue_key>"}))
        sys.exit(1)

    issue_key = args[0]
    result = make_jira_request(config, f'/rest/api/2/issue/{issue_key}/editmeta')

    fields = result.get('fields', {})
    story_points_candidates = []

    for field_id, field_data in fields.items():
        field_name = field_data.get('name', '').lower()
        field_type = field_data.get('schema', {}).get('type')

        if 'story' in field_name and 'point' in field_name and field_type == 'number':
            story_points_candidates.append({
                "field_id": field_id,
                "name": field_data.get('name'),
                "type": field_type,
                "required": field_data.get('required', False)
            })

    if not story_points_candidates:
        print(json.dumps({"error": "No story points field found. Try an issue that has story points enabled."}))
        sys.exit(1)

    print(json.dumps({
        "success": True,
        "issue_key": issue_key,
        "story_points_fields": story_points_candidates
    }))


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: jira-helper.py <command> [args...]"}))
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    config = read_jira_config()

    commands = {
        'create-issue': cmd_create_issue,
        'get-issue': cmd_get_issue,
        'add-comment': cmd_add_comment,
        'transition-issue': cmd_transition_issue,
        'list-transitions': cmd_list_transitions,
        'search': cmd_search,
        'update-issue': cmd_update_issue,
        'get-sprint-field': cmd_get_sprint_field,
        'get-issue-sprints': cmd_get_issue_sprints,
        'add-to-sprint': cmd_add_to_sprint,
        'remove-from-sprint': cmd_remove_from_sprint,
        'list-open-sprints': cmd_list_open_sprints,
        'get-epic-field': cmd_get_epic_field,
        'get-issue-epic': cmd_get_issue_epic,
        'get-story-points-field': cmd_get_story_points_field,
    }

    if command not in commands:
        print(json.dumps({"error": f"Unknown command: {command}. Available: {', '.join(commands.keys())}"}))
        sys.exit(1)

    commands[command](config, args)


if __name__ == '__main__':
    main()
