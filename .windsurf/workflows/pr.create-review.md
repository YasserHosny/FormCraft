<<<<<<< C:/MyData/Other/MyProjects/FormCraft/.windsurf/workflows/pr.create-review.md
---
description: Create a pull request with review request using Template 3 workflow
tools: ['github/github-mcp-server']
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Parse Parameters**: Extract the following from user input or prompt for missing values:
   - TARGET_BRANCH: Destination branch for PR (required parameter)
   - BRANCH_NAME: Feature branch name (auto-generated if not provided)
   - FEATURE_DESCRIPTION: Brief description of changes (auto-generated if not provided)

2. **Execute Review Workflow**:
   - Run @[/review] on current changes to identify potential bugs and improvements
   - Address any critical issues found during review

3. **Execute Git Workflow**:
   - Commit changes with suitable description on the feature branch
   - Push changes to remote (branch created once via GitHub API in step 6)

4. **Create Pull Request**:
   - Create PR from current source branch to specified TARGET_BRANCH
   - Include "@codex" in the PR description (no separate comment step)

5. **Generate Tasks**: Create the following task structure:

```markdown
- [ ] T001 Run @[/review] on current changes
- [ ] T002 Address any critical issues found during review
- [ ] T003 Commit changes with suitable description
- [ ] T004 Push changes to remote (branch is created once via API in step 6)
- [ ] T005 Create PR to merge [BRANCH_NAME] → [TARGET_BRANCH]
- [ ] T006 Include "@codex" in PR description
```

6. **Execute GitHub Operations**:
   - Use review workflow to analyze changes
   - Use `mcp3_create_branch` to create the feature branch (single creation point; do not recreate after pushing)
   - Use `mcp3_create_pull_request` to create the PR
   - Ensure PR body contains "@codex" mention; no separate PR comment is required

7. **Report**: Output:
   - Review results and any issues addressed
   - Created branch name
   - Commit message used
   - PR URL and number
   - Added comment confirmation

## Usage Examples

**Basic usage**:
```
/pr.create-review develop
```

**With custom branch name**:
```
/pr.create-review develop "feature-ui-updates"
```

**With description**:
```
/pr.create-review main "feature-auth-flow" "Add user authentication with JWT tokens"
```

**Natural language**:
```
Create a PR from current changes to main branch with review and @codex mention in description
```

## Auto-generation Rules

If not specified:
- **BRANCH_NAME**: Auto-generated from changes (e.g., "fix-auth-validation", "feature-ui-update")
- **FEATURE_DESCRIPTION**: Auto-generated from git diff summary
- **TARGET_BRANCH**: Required parameter (must be provided)

## Branch Naming Convention

Auto-generated branch names follow these patterns:
- `fix-[issue]` for bug fixes
- `feature-[feature]` for new features  
- `update-[component]` for component updates
- `refactor-[area]` for refactoring

## Commit Message Generation

Auto-generated commit messages follow:
- `fix: [description]` for bug fixes
- `feat: [description]` for features
- `update: [description]` for updates
- `refactor: [description]` for refactoring

## Notes

- Workflow starts with @[/review] to ensure code quality
- Branch is created from current source branch (not always main)
- PR targets the specified TARGET_BRANCH parameter
- PR description includes "@codex" mention (no additional comment)
- Critical review issues are addressed before commit
- All GitHub operations are performed using the MCP GitHub server
=======
---
description: Create a pull request with review request using Template 3 workflow
tools: ['github/github-mcp-server']
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Parse Parameters**: Extract the following from user input or prompt for missing values:
   - TARGET_BRANCH: Destination branch for PR (required parameter)
   - BRANCH_NAME: Feature branch name (auto-generated if not provided)
   - FEATURE_DESCRIPTION: Brief description of changes (auto-generated if not provided)

2. **Execute Review Workflow**:
   - Run @[/review] on current changes to identify potential bugs and improvements
   - Address any critical issues found during review
   - Capture test/review status to include in PR body (e.g., "Tests: not run" or summary of executed checks)

3. **Execute Git Workflow**:
   - Commit changes with suitable description on the feature branch
   - Push changes to remote (branch created once via GitHub API in step 6)

4. **Create Pull Request**:
   - Create PR from current source branch to specified TARGET_BRANCH
   - Include "@codex" in the PR description (no separate comment step)

5. **Generate Tasks**: Create the following task structure:

```markdown
- [ ] T001 Run @[/review] on current changes
- [ ] T002 Address any critical issues found during review
- [ ] T003 Record test/review status note for PR (e.g., "Tests: not run" or executed suite)
- [ ] T004 Commit changes with suitable description
- [ ] T005 Push changes to remote (branch is created once via API in step 6)
- [ ] T006 Create PR to merge [BRANCH_NAME] → [TARGET_BRANCH]
- [ ] T007 Include "@codex" and test/review status in PR description
```

6. **Execute GitHub Operations**:
   - Use review workflow to analyze changes
   - Use `mcp3_create_branch` to create the feature branch (single creation point; do not recreate after pushing)
   - Use `mcp3_create_pull_request` to create the PR
   - Ensure PR body contains "@codex" mention and a test/review status note; no separate PR comment is required

7. **Report**: Output:
   - Review results and any issues addressed
   - Created branch name
   - Commit message used
   - PR URL and number
   - Added comment confirmation

## Usage Examples

**Basic usage**:
```
/pr.create-review develop
```

**With custom branch name**:
```
/pr.create-review develop "feature-ui-updates"
```

**With description**:
```
/pr.create-review main "feature-auth-flow" "Add user authentication with JWT tokens"
```

**Natural language**:
```
Create a PR from current changes to main branch with review and @codex mention in description
```

## Auto-generation Rules

If not specified:
- **BRANCH_NAME**: Auto-generated from changes (e.g., "fix-auth-validation", "feature-ui-update")
- **FEATURE_DESCRIPTION**: Auto-generated from git diff summary
- **TARGET_BRANCH**: Required parameter (must be provided)

## Branch Naming Convention

Auto-generated branch names follow these patterns:
- `fix-[issue]` for bug fixes
- `feature-[feature]` for new features  
- `update-[component]` for component updates
- `refactor-[area]` for refactoring

## Commit Message Generation

Auto-generated commit messages follow:
- `fix: [description]` for bug fixes
- `feat: [description]` for features
- `update: [description]` for updates
- `refactor: [description]` for refactoring

## Notes

- Workflow starts with @[/review] to ensure code quality
- Branch is created from current source branch (not always main)
- PR targets the specified TARGET_BRANCH parameter
- PR description includes "@codex" mention (no additional comment)
- Critical review issues are addressed before commit
- All GitHub operations are performed using the MCP GitHub server
>>>>>>> C:/Users/136687/.windsurf/worktrees/FormCraft/FormCraft-fe9d327b/.windsurf/workflows/pr.create-review.md
