---
name: meli-genai.custom-rules-installer
description: Install language-specific agentic rules for Claude. Auto-detects technology, installs rules in .claude/rules/, updates .gitignore, and reports installation status to the user.
model: opus
---

## Purpose

Install custom agentic rules for **Claude** by auto-detecting the project technology and fetching the appropriate rules from the centralized rules service.

This workflow performs the following actions:
1. **Detects** the application name and technology from the repository
2. **Downloads and installs** language-specific rules in `.claude/rules/{technology}/`
3. **Downloads and installs** common rules in `.claude/rules/common/`
4. **Generates** a `SKILL.md` index file in each skills folder (`.claude/skills/{technology}/` and `.claude/skills/common/`) with a Quick Reference guide and How to Use section based on the rules in the `rules/` subdirectory
5. **Analyzes and updates** the `.gitignore` file to exclude the `.claude/` directory
6. **Reports to the user** with a detailed message indicating:
   - Whether rules were created (new installation) or updated (version upgrade)
   - The technology detected and versions installed
   - Any errors encountered, with support channel information

---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The user may provide a specific repository path or additional context.

---

## Prerequisites

- `curl` installed
- `jq` installed

---

## Workflow: Install Agentic Rules for Claude (Runbook)

Follow this workflow strictly, in order. Do not skip steps.

### Workflow Inputs
- **Repository path** (required): absolute path to the project/repository where rules will be installed.
- **Agent name** (required): the name of the AI agent executing this workflow. For this workflow, it must be `"claude"`.

### Workflow Output (end result)
- Agentic rules installed in `.claude/rules/{technology}/` and `.claude/rules/common/` directories.
- `.gitignore` updated to exclude `.claude/` directory.
- Summary report of detected app name, technology, and installation status.

### Workflow Steps (authoritative)

1) **Get repository path**
   - Get the absolute path of the current working directory.
   - This is the repository where the rules will be installed.
   - Store the path in a variable for use in subsequent steps.

   ```bash
   REPOSITORY_PATH=$(pwd)
   echo "Repository path: $REPOSITORY_PATH"
   ```

2) **Execute the installer script**
   - The script is available globally as `custom-rules-installer`.
   - Execute it with the repository path and IA tool name as arguments.
   - **CRITICAL**: Do NOT interrupt the script execution. Wait until you see the **second** `[REPORT] ----------------------------------------` line in the terminal output before proceeding to the next step.

   ```bash
   custom-rules-installer "$REPOSITORY_PATH" "claude"
   ```

3) **Parse and report results to user**

   The script outputs logs with the format `[custom-rules-installer] [HH:MM:SS] [LEVEL] message`.

   The structured report is output with `[REPORT]` level, between two `----------------------------------------` separator lines. Parse the following fields from lines containing `[REPORT]`:

   | Field | Description |
   |-------|-------------|
   | `result` | SUCCESS or FAIL |
   | `commandFlowId` | Unique execution ID for traceability |
   | `appName` | Detected application name |
   | `technology` | Detected technology (go, java, python, etc.) |
   | `techPackage.oldVersion` | Previous technology rules version (or "none") |
   | `techPackage.newVersion` | New technology rules version (empty if SKIP) |
   | `techPackage.action` | CREATE, UPDATE, or SKIP |
   | `techPackage.rulesCount` | Number of technology rules installed |
   | `commonPackage.oldVersion` | Previous common rules version (or "none") |
   | `commonPackage.newVersion` | New common rules version (empty if SKIP) |
   | `commonPackage.action` | CREATE, UPDATE, or SKIP |
   | `commonPackage.rulesCount` | Number of common rules installed |
   | `failedAt` | (only if FAIL) Step where error occurred |
   | `errorMessage` | (only if FAIL) Error description |

   **If result=SUCCESS AND techPackage.action=SKIP AND commonPackage.action=SKIP**, show:

   ⚠️ **No rules installed for {appName}**

   There are no rules available for **{technology}** projects yet.

   For questions or to request rules for this technology, contact the team on Slack channel **#ai-coding-tool**

   ---

   **If result=SUCCESS** (and at least one package has action CREATE or UPDATE), show:

   ✅ **Rules installed successfully for {appName}**

   - **Technology:** {technology}
   - **Tech rules:** {techPackage.action} ({techPackage.rulesCount} rules) - v{techPackage.newVersion}
     - If `techPackage.action` is SKIP: show "No tech rules available for {technology}" instead
   - **Common rules:** {commonPackage.action} ({commonPackage.rulesCount} rules) - v{commonPackage.newVersion}
     - If `commonPackage.action` is SKIP: show "No common rules available" instead

   Rules installed in `.claude/rules/`

   ---

   **If result=FAIL**, show a message like:

   ❌ **Failed to install rules**

   Error: {errorMessage}

   For help, contact the team on Slack channel **#ai-coding-tool**

4) **Generate SKILL.md index for installed rules**

   **Step 4a — Run the scaffold script** to create a deterministic SKILL.md skeleton in each skills directory.

   Execute the following script **exactly as-is**. It scans `.claude/skills/{technology}/rules/` and `.claude/skills/common/rules/`, and generates a `SKILL.md` in the parent folder (`.claude/skills/{technology}/`) with a structure that includes frontmatter, an About section, a Quick Reference with one entry per rule file, and a How to Use section listing all rule files.

   ```bash
   for SKILLS_DIR in "$REPOSITORY_PATH"/.claude/skills/*/; do
     [ -d "$SKILLS_DIR" ] || continue

     FOLDER_NAME=$(basename "$SKILLS_DIR")
     RULES_DIR="${SKILLS_DIR}rules"

     # Skip if rules subdirectory doesn't exist
     [ -d "$RULES_DIR" ] || continue

     # Collect .md files from rules/ subdirectory, excluding README.md and SKILL.md
     MD_FILES=()
     for f in "$RULES_DIR"/*.md; do
       [ -f "$f" ] || continue
       BASENAME=$(basename "$f")
       if [ "$BASENAME" != "README.md" ] && [ "$BASENAME" != "SKILL.md" ]; then
         MD_FILES+=("$BASENAME")
       fi
     done

     # Skip if no .md files found
     [ ${#MD_FILES[@]} -eq 0 ] && continue

     SKILL_FILE="$SKILLS_DIR/SKILL.md"

     # Skip if SKILL.md already exists (no need to regenerate when rules haven't changed)
     [ -f "$SKILL_FILE" ] && continue

     # Write frontmatter, heading, about section, and quick reference header
     cat > "$SKILL_FILE" <<SKILL_EOF
   ---
   name: ${FOLDER_NAME}-best-practices
   description: TODO_DESCRIPTION
   ---

   # ${FOLDER_NAME} Best Practices Skill

   ## About the skill

   TODO_ABOUT

   ---

   ## Quick Reference
   SKILL_EOF

     # Append one Quick Reference section per rule file
     SECTION_NUM=1
     for MD_FILE in "${MD_FILES[@]}"; do
       cat >> "$SKILL_FILE" <<SECTION_EOF

   ### ${SECTION_NUM}. TODO_SECTION_NAME (TODO_PRIORITY)

   - read \`rules/${MD_FILE}\` when TODO_WHEN_TO_READ
   SECTION_EOF
       SECTION_NUM=$((SECTION_NUM + 1))
     done

     # Write How to Use section
     TICK='`'
     {
       echo ""
       echo "---"
       echo ""
       echo "## How to Use"
       echo ""
       echo "Read individual rule files for detailed explanations and code examples:"
       echo ""
       echo "${TICK}${TICK}${TICK}"
       for MD_FILE in "${MD_FILES[@]}"; do
         echo "rules/${MD_FILE}"
       done
       echo "${TICK}${TICK}${TICK}"
       echo ""
       echo "Each rule file contains:"
       echo ""
       echo "- Specific guidelines and constraints for the topic"
       echo "- Correct and incorrect code examples with explanations"
       echo "- Best practices, anti-patterns, and cross-references to related rules"
       echo "- Version information and applicability context"
     } >> "$SKILL_FILE"

     echo "Generated SKILL.md skeleton in $SKILLS_DIR"
   done
   ```

   **Step 4b — Complete the TODO placeholders.** For each `SKILL.md` generated above:
   1. Read every `.md` rule file located in the `rules/` subdirectory of the same skills folder.
   2. Replace `TODO_DESCRIPTION` in the frontmatter with a 1-2 sentence description of the skill, covering the main topics of all rule files and when to use this skill.
   3. Replace `TODO_ABOUT` with a concise paragraph summarizing what this skill covers and its purpose in the development workflow.
   4. For each Quick Reference section:
      a. Replace `TODO_SECTION_NAME` with a short descriptive topic name (e.g., "Logging", "Performance Optimization", "Architecture").
      b. Replace `TODO_PRIORITY` with the appropriate level: `CRITICAL`, `HIGH`, or `MODERATE`.
      c. Replace `TODO_WHEN_TO_READ` with a concrete scenario describing when the developer should read that rule file.
      d. Add additional `- read \`rules/{file}\` when ...` bullet points if the rule file covers multiple distinct use cases (aim for 2-4 bullets per section).
   5. **Do NOT** modify the frontmatter structure, the `## How to Use` section, or any content below it — only replace the `TODO_*` placeholders and add bullets in Quick Reference.
   6. Save the updated `SKILL.md`.

   If no `SKILL.md` was generated (no directories or no rule files), skip this step entirely.

5) **Update .gitignore**
   - Check if `.gitignore` exists in the repository root.
   - If `.claude/` is already present in `.gitignore`, inform the user and skip this step.
   - If `.claude/` is **not** present (or `.gitignore` does not exist), **ask the user** whether they want to add it:

   > "Would you like to add `.claude/` to your `.gitignore` to avoid accidentally committing the installed rules?"

   - Only proceed with the update **if the user confirms**. If the user declines, skip this step and inform them that `.claude/` will not be ignored by git.

   ```bash
   # Run only if the user confirmed they want to update .gitignore
   GITIGNORE_PATH="$REPOSITORY_PATH/.gitignore"

   if [ -f "$GITIGNORE_PATH" ]; then
     if ! grep -q "^\.claude/$" "$GITIGNORE_PATH"; then
       echo ".claude/" >> "$GITIGNORE_PATH"
       echo "Added .claude/ to .gitignore"
     else
       echo ".claude/ already exists in .gitignore"
     fi
   else
     echo ".claude/" > "$GITIGNORE_PATH"
     echo "Created .gitignore with .claude/ entry"
   fi
   ```
---

## Error Handling

- If `curl` or `jq` are not installed, report the missing dependency and stop.
- If the repository path is invalid, report the error.
- If `.gitignore` cannot be modified (and the user confirmed the update), report the permission error.
- **For any error**, always include the Slack channel **#ai-coding-tool** for support.

---

## Non-negotiable Requirements (MUST)

- **MUST** execute steps in order; do not skip any step.
- **MUST** wait for the second `[REPORT] ----------------------------------------` line before parsing the script output.
- **MUST** use "claude" as the IA tool argument.
- **MUST** ask the user before adding `.claude/` to `.gitignore`; only update if the user confirms.
- **MUST** show a user-friendly message based on the script result (SUCCESS or FAIL).
- **MUST** include Slack channel **#ai-coding-tool** in error messages.

---
