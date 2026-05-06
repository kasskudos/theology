#!/bin/bash
# Claude Code MCP Interaction Logger
CLAUDE_CONFIG="$HOME/.claude.json"

# Mount version - set by sensor/mount.sh during deployment; default when run standalone
readonly MOUNT_VERSION="1.2.0"

# Versioning: bump when changing Claude hooks only (mount_claude.sh / mount_claude_sdd.sh)
readonly HOOK_VERSION="1.1.0"
readonly HOOK_VERSION_FIELD="hook_version"

# Portable current time in milliseconds (for hook_execution_time_ms)
get_time_ms() { perl -e 'use Time::HiRes qw(time); print int(time()*1000)' 2>/dev/null || echo $(( $(date +%s) * 1000 )); }

# Get project name
get_project_name() {
    local project_name=""

    if [[ -n "$CLAUDE_PROJECT_DIR" ]]; then
        local git_config="${CLAUDE_PROJECT_DIR}/.git/config"

        if [[ -f "$git_config" ]]; then
            # Extract URL from git config (e.g., git@github.com-emu:melisource/fury_genai-tracker-hooks.git)
            local git_url=$(grep -E "^\s*url\s*=" "$git_config" | head -1 | sed -E 's/.*url[[:space:]]*=[[:space:]]*//')

            # Extract project name: everything after the last '/' and before '.git'
            # Works for: git@github.com-emu:melisource/fury_genai-tracker-hooks.git
            # Works for: https://github.com/melisource/fury_genai-tracker-hooks.git
            project_name=$(echo "$git_url" | sed -E 's|.*/([^/]+)\.git.*|\1|')
        fi
    fi

    echo "$project_name" | sed 's/[^a-zA-Z0-9_-]/_/g'
}

# Branch name of the repo where the log was collected from
get_repo_branch() {
    local branch=""
    if [[ -n "$CLAUDE_PROJECT_DIR" && -d "${CLAUDE_PROJECT_DIR}/.git" ]]; then
        branch=$(git -C "$CLAUDE_PROJECT_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null)
    fi
    echo "$branch"
}

# Path to the root of the repository the log was collected from
get_repo_root() {
    local root=""
    if [[ -n "$CLAUDE_PROJECT_DIR" && -d "${CLAUDE_PROJECT_DIR}/.git" ]]; then
        root=$(git -C "$CLAUDE_PROJECT_DIR" rev-parse --show-toplevel 2>/dev/null)
    fi
    [[ -z "$root" && -n "$CLAUDE_PROJECT_DIR" ]] && root="$CLAUDE_PROJECT_DIR"
    echo "$root"
}

# Relative path of CLAUDE_PROJECT_DIR (or cwd) from repo root; empty if not in a repo or at root.
# Top-level file_relative_path, aligns with mount_cursor.sh.
get_file_relative_path_claude() {
    local repo_root
    repo_root=$(get_repo_root)
    [[ -z "$repo_root" ]] && echo "" && return 0
    local base="${CLAUDE_PROJECT_DIR:-$(pwd)}"
    repo_root="${repo_root%/}"
    if [[ "$base" != "$repo_root" && "$base" == "$repo_root"/* ]]; then
        echo "${base#$repo_root/}"
    else
        echo ""
    fi
}

# Extract JSON string value from a substring; allows optional space around colon (Cursor-style).
# Usage: extract_json_string_from "{\"file_path\": \"/a/b\"}" "file_path"
extract_json_string_from() {
    local input="$1"
    local key="$2"
    local default="${3:-}"
    local value
    value=$(echo "$input" | grep -o "\"$key\"[[:space:]]*:[[:space:]]*\"[^\"\\\\]*\"" | sed -n "s/.*\"$key\"[[:space:]]*:[[:space:]]*\"\\([^\"\\\\]*\\)\".*/\1/p" | head -1)
    if [[ -z "$value" ]]; then
        echo "$default"
    else
        echo "$value"
    fi
}

is_a_valid_path() {
    [[ -n "$1" && ( -f "$1" || -d "$1" ) ]]
}

get_file_path_from_fallback() {
    local raw="$1"
    local project_dir="${2:-}"
    local cwd_hook="${3:-}"
    local r="${raw#./}"
    if [[ "$raw" == /* ]]; then
        echo "$raw"
        return 0
    fi
    if [[ -n "$project_dir" && ( -f "$project_dir/$r" || -d "$project_dir/$r" ) ]]; then
        echo "$project_dir/$r"
        return 0
    fi
    if [[ -n "$cwd_hook" && "$project_dir" != "$cwd_hook" && ( -f "$cwd_hook/$r" || -d "$cwd_hook/$r" ) ]]; then
        echo "$cwd_hook/$r"
        return 0
    fi
    echo "$raw"
}

# Find git repository root by traversing up from a file path (from mount_cursor.sh).
# Returns: repo_name|branch|repo_root|relative_path|is_repository
find_git_repo_from_file() {
    local file_path="$1"
    if [[ -z "$file_path" ]]; then
        echo "null|null|$(pwd)|null|false"
        return 0
    fi
    local abs_path="" dir=""
    if [[ -f "$file_path" ]]; then
        abs_path=$(cd "$(dirname "$file_path")" && pwd)/$(basename "$file_path")
        dir=$(dirname "$abs_path")
    elif [[ -d "$file_path" ]]; then
        abs_path=$(cd "$file_path" && pwd)
        dir="$abs_path"
    else
        echo "null|null|$(pwd)|$file_path|false"
        return 0
    fi
    while [[ "$dir" != "/" && "$dir" != "." ]]; do
        if [[ -d "$dir/.git" ]]; then
            local repo_root="$dir"
            local branch=$(cd "$repo_root" && git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
            local git_config="$repo_root/.git/config"
            local repo_name="unknown"
            if [[ -f "$git_config" ]]; then
                local git_url=$(grep -E "^\s*url\s*=" "$git_config" | head -1 | sed -E 's/.*url[[:space:]]*=[[:space:]]*//')
                repo_name=$(echo "$git_url" | sed -E 's|.*/([^/]+)\.git.*|\1|')
            fi
            repo_name=$(echo "$repo_name" | sed 's/[^a-zA-Z0-9_-]/_/g')
            local relative_path="${abs_path#$repo_root/}"
            echo "${repo_name}|${branch}|${repo_root}|${relative_path}|true"
            return 0
        fi
        dir=$(dirname "$dir")
    done
    if [[ -f "$abs_path" ]]; then
        dir=$(dirname "$abs_path")
    else
        dir="$abs_path"
    fi
    while [[ "$dir" != "/" && "$dir" != "." ]]; do
        if [[ -f "$dir/.fury" ]]; then
            local fury_app=$(grep -E "^\s*application_name\s*=" "$dir/.fury" | head -1 | sed -E 's/.*application_name[[:space:]]*=[[:space:]]*//' | tr -d '"' | tr -d "'")
            if [[ -n "$fury_app" ]]; then
                fury_app=$(echo "$fury_app" | sed 's/[^a-zA-Z0-9_-]/_/g')
                local relative_path="${abs_path#$dir/}"
                echo "${fury_app}|null|${dir}|${relative_path}|false"
                return 0
            fi
        fi
        dir=$(dirname "$dir")
    done
    echo "null|null|$(pwd)|$abs_path|false"
    return 0
}

# Escape string for JSON (backslash, double-quote, newline)
json_escape_value() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    echo "$s"
}

# Output agent_version for JSON: version number only from "claude --version" (e.g. 2.1.38), or null if unavailable
get_agent_version_json() {
    local raw
    raw=$(claude --version 2>/dev/null | head -1)
    local version
    version=$(echo "$raw" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
    if [[ -z "$version" ]]; then
        echo "null"
    else
        local escaped
        escaped=$(json_escape_value "$version")
        echo "\"${escaped}\""
    fi
}

save_data() {
    local input_data="$1"
    local file_name="$2"
    local dir_path=$(dirname "$file_name")
    mkdir -p "$dir_path" 2>/dev/null
    echo "$input_data" >> "$file_name" 2>/dev/null
}


# Check if MCP server is HTTP type
# Returns 0 (true) if HTTP, 1 (false) otherwise
is_http_mcp() {
    local mcp_block="$1"

    # First check if type is explicitly set to "http"
    local server_type=$(echo "$mcp_block" | grep -m 1 '"type"' | sed -n 's/.*"type"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    if [[ "$server_type" == "http" ]]; then
        return 0
    fi

    # If type is not available, check if it has "url" attribute
    if [[ -z "$server_type" ]]; then
        local url=$(echo "$mcp_block" | grep -m 1 '"url"' | sed -n 's/.*"url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
        if [[ -n "$url" ]]; then
            return 0
        fi
    fi

    return 1
}


# Check if MCP server is stdio type
# Returns 0 (true) if stdio, 1 (false) otherwise
is_stdio_mcp() {
    local mcp_block="$1"

    # First check if type is explicitly set to "stdio"
    local server_type=$(echo "$mcp_block" | grep -m 1 '"type"' | sed -n 's/.*"type"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    if [[ "$server_type" == "stdio" ]]; then
        return 0
    fi

    # If type is not available, check if it has "args" attribute
    if [[ -z "$server_type" ]]; then
        local args=$(echo "$mcp_block" | grep -m 1 '"args"' | sed -n 's/.*"args"[[:space:]]*:[[:space:]]*\[.*/\0/p')
        if [[ -n "$args" ]]; then
            return 0
        fi
    fi

    return 1
}

get_mcp_url() {
    local mcp_block="$1"

    if [ -z "$mcp_block" ]; then
        echo "null"
        return 1
    fi

    local url=""

    # Extract URL based on type using robust detection functions
    if is_http_mcp "$mcp_block"; then
        url=$(echo "$mcp_block" | grep -m 1 '"url"' | sed -n 's/.*"url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    elif is_stdio_mcp "$mcp_block"; then
        url=$(echo "$mcp_block" | grep -A 5 '"args"' | grep -o 'https\?://[^"]*' | head -1)
    fi

    if [ -z "$url" ]; then
        echo "null"
    else
        echo "$url"
    fi
}


get_mcp_block_from_local_scope() {
    local config_file="$HOME/.claude.json"
    local project_path="$1"
    local mcp_name="$2"

    # Get the project block using awk
    local project_block=$(awk -v search="\"$project_path\":" '
        BEGIN { found=0; depth=0; start_depth=-1 }
        {
            if (!found && index($0, search) > 0) {
                found = 1
                start_depth = depth
            }

            if (found) {
                print $0

                # Count braces in the line
                for (i=1; i<=length($0); i++) {
                    char = substr($0, i, 1)
                    if (char == "{") depth++
                    else if (char == "}") depth--
                }

                # Exit when we return to the starting depth (project block closed)
                if (depth <= start_depth && start_depth >= 0 && NR > 1) {
                    exit
                }
            }
        }
    ' "$config_file" 2>/dev/null)

    if [ -z "$project_block" ]; then
        echo ""
        return 1
    fi

    # Find the specific MCP within the project's mcpServers using awk
    local mcp_block=$(echo "$project_block" | awk -v search="\"$mcp_name\":" '
        BEGIN { found=0; depth=0 }
        {
            if (!found && index($0, search) > 0) {
                found = 1
                depth = 0
            }

            if (found) {
                print $0

                # Count braces
                for (i=1; i<=length($0); i++) {
                    char = substr($0, i, 1)
                    if (char == "{") depth++
                    else if (char == "}") depth--
                }

                # Exit when the MCP block closes
                if (depth <= 0 && NR > 1) {
                    exit
                }
            }
        }
    ')

    echo "$mcp_block"
}

get_mcp_block_from_user_scope() {
    local config_file="$HOME/.claude.json"
    local mcp_name="$1"

    # Get the global mcpServers block (at root level, not inside projects)
    local global_mcp_section=$(awk '
        /"mcpServers"[[:space:]]*:[[:space:]]*{/ {
            found_line = NR
            depth = 0
            delete block
            block_idx = 0
        }
        found_line > 0 && NR >= found_line {
            block[block_idx++] = $0

            # Count braces in the line
            for (i=1; i<=length($0); i++) {
                char = substr($0, i, 1)
                if (char == "{") depth++
                else if (char == "}") depth--
            }

            # When we close the mcpServers block, save it
            if (depth == 0 && NR > found_line) {
                # Store this block as the latest (global is typically last)
                for (i=0; i<block_idx; i++) {
                    saved_block[i] = block[i]
                }
                saved_block_size = block_idx
                found_line = 0
            }
        }
        END {
            # Print the last mcpServers block found (global)
            for (i=0; i<saved_block_size; i++) {
                print saved_block[i]
            }
        }
    ' "$config_file" 2>/dev/null)

    if [ -z "$global_mcp_section" ]; then
        echo ""
        return 1
    fi

    # Find the specific MCP within global mcpServers
    local mcp_block=$(echo "$global_mcp_section" | awk -v search="\"$mcp_name\":" '
        BEGIN { found=0; depth=0 }
        {
            if (!found && index($0, search) > 0) {
                found = 1
                depth = 0
            }

            if (found) {
                print $0

                # Count braces
                for (i=1; i<=length($0); i++) {
                    char = substr($0, i, 1)
                    if (char == "{") depth++
                    else if (char == "}") depth--
                }

                # Exit when the MCP block closes
                if (depth <= 0 && NR > 1) {
                    exit
                }
            }
        }
    ')

    echo "$mcp_block"
}


get_mcp_block_from_project_scope() {
    local mcp_name="$1"
    local config_file="$CLAUDE_PROJECT_DIR/.mcp.json"

    # Check if .mcp.json exists in the project
    if [ ! -f "$config_file" ]; then
        echo ""
        return 1
    fi

    # Extract the mcpServers block and find the specific MCP
    local mcp_block=$(awk -v search="\"$mcp_name\":" '
        BEGIN { found=0; depth=0 }
        {
            if (!found && index($0, search) > 0) {
                found = 1
                depth = 0
            }

            if (found) {
                print $0

                # Count braces
                for (i=1; i<=length($0); i++) {
                    char = substr($0, i, 1)
                    if (char == "{") depth++
                    else if (char == "}") depth--
                }

                # Exit when the MCP block closes
                if (depth <= 0 && NR > 1) {
                    exit
                }
            }
        }
    ' "$config_file" 2>/dev/null)

    echo "$mcp_block"
}


get_mcp_block_with_priority() {
    local mcp_name="$1"
    local project_path="$CLAUDE_PROJECT_DIR"

    local mcp_block=""

    # 1. Try local scope (project config in ~/.claude.json)
    if [ -n "$project_path" ]; then
        mcp_block=$(get_mcp_block_from_local_scope "$project_path" "$mcp_name")
    fi

    # 2. Try project scope first (.mcp.json in project directory)
    if [ -z "$mcp_block" ] && [ -n "$project_path" ]; then
        mcp_block=$(get_mcp_block_from_project_scope "$mcp_name")
    fi

    # 3. Try user scope (global config in ~/.claude.json)
    if [ -z "$mcp_block" ] && [ -n "$project_path" ]; then
        mcp_block=$(get_mcp_block_from_user_scope "$mcp_name")
    fi

    echo "$mcp_block"
}


get_mcp_command() {
    local mcp_block="$1"

    if [ -z "$mcp_block" ]; then
        echo "null"
        return 1
    fi

    # Check if it's a stdio MCP
    if is_stdio_mcp "$mcp_block"; then
        # Extract command field
        local command=$(echo "$mcp_block" | grep -m 1 '"command"' | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
        if [ -z "$command" ]; then
            echo "null"
        else
            echo "$command"
        fi
    else
        echo "null"
    fi
}


generate_unique_id() {
    local timestamp=$(date +%s%N)
    local random_part=$RANDOM
    echo "${timestamp}_${random_part}"
}


validate_and_set_null_if_needed() {
    local value="$1"

    if [ "$value" != "null" ]; then
        echo "\"${value}\""
    else
        echo "null"
    fi
}


add_metada_and_save() {
    local input_data="$1"
    local start_ms=$(get_time_ms)

    # Extract MCP name from tool_name (e.g., mcp__fury__search_sdk_docs -> fury; mcp__Fury_Dev__search_sdk_docs -> Fury_Dev)
    local tool_name_raw mcp_name
    tool_name_raw=$(echo "$input_data" | sed -n 's/.*"tool_name":"\([^"]*\)".*/\1/p')
    if [[ "$tool_name_raw" == mcp__* ]]; then
        local rest="${tool_name_raw#mcp__}"
        local mcp_name="${rest%%__*}"
    else
        local mcp_name=""
    fi

    # Get MCP block once with priority: project config first, then global config
    local mcp_block=$(get_mcp_block_with_priority "$mcp_name")

    # Extract URL and command from the block
    local mcp_url=$(get_mcp_url "$mcp_block")
    local mcp_command=$(get_mcp_command "$mcp_block")

    # Get other metadata via find_git_repo_from_file (same as Cursor)
    local workspace_dir="${CLAUDE_PROJECT_DIR:-$(pwd)}"
    local git_info repo_name branch_raw is_repository
    git_info=$(find_git_repo_from_file "$workspace_dir")
    IFS='|' read -r repo_name branch_raw _ _ is_repository <<< "$git_info"

    local repo_escaped fury_app_escaped branch_json
    if [[ "$repo_name" != "null" && -n "$repo_name" ]]; then
        repo_escaped=$(json_escape_value "$repo_name")
    else
        repo_escaped=$(json_escape_value "$workspace_dir")
    fi
    fury_app_escaped="$repo_escaped"
    if [[ "$branch_raw" != "null" && -n "$branch_raw" ]]; then
        local branch_escaped
        branch_escaped=$(json_escape_value "$branch_raw")
        branch_json="\"${branch_escaped}\""
    else
        branch_json="null"
    fi

    # file_relative_path: Edit/Write — path from tool_input; resolve to existing path then single-arg find_git_repo_from_file (field 4)
    local file_relative_path_json="null"
    if [[ "$tool_name_raw" == "Edit" || "$tool_name_raw" == "Write" ]]; then
        local input_one_line tool_input_section file_path_raw cwd_from_hook path_for_git k
        input_one_line=$(echo "$input_data" | tr -d '\n')
        tool_input_section="${input_one_line#*\"tool_input\":}"
        tool_input_section="${tool_input_section%%\"tool_response\":*}"
        cwd_from_hook=$(extract_json_string_from "$input_one_line" "cwd" "")
        file_path_raw=""
        for k in filePath file_path path file target_file; do
            file_path_raw=$(extract_json_string_from "$tool_input_section" "$k" "")
            [[ -n "$file_path_raw" ]] && break
        done
        if [[ -n "$file_path_raw" ]]; then
            local file_git_info file_repo_name file_branch_raw file_rel file_is_repo
            path_for_git="$file_path_raw"
            if ! is_a_valid_path "$path_for_git"; then
                path_for_git=$(get_file_path_from_fallback "$file_path_raw" "${CLAUDE_PROJECT_DIR:-}" "$cwd_from_hook")
            fi
            file_git_info=$(find_git_repo_from_file "$path_for_git")
            IFS='|' read -r file_repo_name file_branch_raw _ file_rel file_is_repo <<< "$file_git_info"
            # Override repo/branch/is_repository with values derived from the edited file
            if [[ "$file_repo_name" != "null" && -n "$file_repo_name" ]]; then
                repo_escaped=$(json_escape_value "$file_repo_name")
                fury_app_escaped="$repo_escaped"
            fi
            if [[ "$file_branch_raw" != "null" && -n "$file_branch_raw" ]]; then
                local file_branch_escaped
                file_branch_escaped=$(json_escape_value "$file_branch_raw")
                branch_json="\"${file_branch_escaped}\""
            fi
            is_repository="$file_is_repo"
            if [[ -n "$file_rel" && "$file_is_repo" == "true" ]]; then
                local rel_escaped
                rel_escaped=$(json_escape_value "$file_rel")
                file_relative_path_json="\"${rel_escaped}\""
            fi
        fi
    fi

    local utc_timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local session_id=$(generate_unique_id "$input_data")
    local user_id=$(whoami | base64)

    # Build the final JSON with metadata (always include mcp_command, can be null)
    # repo and fury_app are the same (fury_app deprecated later); repo_branch = branch of repo hook was called on
    local mcp_url_json=$(validate_and_set_null_if_needed "$mcp_url")
    local mcp_command_json=$(validate_and_set_null_if_needed "$mcp_command")

    local end_ms=$(get_time_ms)
    local execution_ms=$(( end_ms - start_ms ))
    local elapsed_time=$execution_ms
    local agent_version_json=$(get_agent_version_json)

    # Top-level fields: fury_app + repo, repo_branch, file_relative_path (Edit/Write when path resolves), etc.
    local modified_json="{\"fury_app\":\"${fury_app_escaped}\",\"repo\":\"${repo_escaped}\",\"repo_branch\":${branch_json},\"file_relative_path\":${file_relative_path_json},\"is_repository\":${is_repository},\"${HOOK_VERSION_FIELD}\":\"${HOOK_VERSION}\",\"mount_version\":\"${MOUNT_VERSION}\",\"agent_version\":${agent_version_json},\"elapsed_time\":${elapsed_time},\"hook_type\":\"post-tool-use\",\"mcp_url\":${mcp_url_json},\"mcp_command\":${mcp_command_json},\"utc_time\":\"${utc_timestamp}\",\"id\": \"$user_id\", \"crude_data\":$input_data}"

    # Save to file
    save_data "$modified_json" "$HOME/.claude/logs/${session_id}_logs.json"
}

# Main processing function
process_mcp_hook() {
    local input_data=$(cat)

    # Test input data. You can uncomment the one you want to test to check the flow.
    # mcp http
    # local input_data='{"session_id":"7929176f-f924-4f35-8da3-4d6c1e2b1f7c","transcript_path":"/Users/julianestehe/.claude/projects/-Users-julianestehe-apps-tooling-genai-fury-mcp-prompt-reviewer/7929176f-f924-4f35-8da3-4d6c1e2b1f7c.jsonl","cwd":"/Users/julianestehe/apps/tooling-genai/fury_mcp-prompt-reviewer","permission_mode":"default","hook_event_name":"PostToolUse","tool_name":"mcp__fury__search_sdk_docs","tool_input":{"query":"workqueue SDK complete documentation setup configuration operations client","language":"java","service":"workqueue"}}'
    # mcp stdio
    # local input_data='{"session_id":"c548bfeb-964a-4137-ac59-e4d451ab75ce","transcript_path":"/Users/julianestehe/.claude/projects/-Users-julianestehe-apps-tooling-genai-fury-mcp-prompt-reviewer/c548bfeb-964a-4137-ac59-e4d451ab75ce.jsonl","cwd":"/Users/julianestehe/apps/tooling-genai/fury_mcp-prompt-reviewer","permission_mode":"default","hook_event_name":"PostToolUse","tool_name":"mcp__revisor__changes_review","tool_input":{"repository_path":"/Users/julianestehe/apps/tooling-genai/fury_mcp-prompt-reviewer","application_name":"mcp-prompt-reviewer","base_branch":"master","language":"python"},"tool_response":[{"type":"text","text":"test response"}]}'
    # print everythin to debug
    # echo "$input_data" >> "$HOME/.claude/logs/logs.json" 2>/dev/null

    local event_name=$(echo "$input_data" | grep -o '"hook_event_name":"[^"]*"' | sed 's/.*:"\([^"]*\)".*/\1/')
    case "$event_name" in
        "PostToolUse")
            add_metada_and_save "$input_data"
            ;;
    esac
}

# Main execution
process_mcp_hook