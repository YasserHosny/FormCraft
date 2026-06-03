---
description: Create branch, commit changes, and create PR with reviewer mention.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Create a new branch, commit pending changes with descriptive message, and create a pull request to a specified target branch with reviewer mention.

## Usage

```bash
/create-pr target-branch
/create-pr target-branch --branch custom-branch-name
/create-pr target-branch --reviewer @someone --message "docs: clarify onboarding"
```

## Parameters

- **target_branch**: The target branch for the PR (required)
- **branch_name**: Optional custom branch name. If omitted, derive a slug from the primary change area (e.g., `feature/api-alerts-20260401-2257`).
- **reviewer**: Optional GitHub handle to mention in the PR body. Defaults to `@codex`.
- **message**: Optional commit message override. If not provided, auto-generate using the conventional commit rubric below.

## Execution Steps

### 1. Parse Input Parameters

Extract the target branch from `$ARGUMENTS` plus any optional flags:
- `/create-pr target-branch-name`
- `/create-pr target-branch-name --branch custom-branch-name`
- `/create-pr target-branch-name --reviewer @handle`
- `/create-pr target-branch-name --message "feat: add profile photo support"`

If no target branch specified, abort with error message.

### 2. Check Git Status

Run `git status --porcelain` to check for pending changes:
- If no changes: Abort with message "No pending changes to commit"
- If changes exist: Continue with branch creation

### 3. Create Branch

Generate branch name if not provided:
- Inspect the paths from `git status --porcelain` and extract up to two dominant areas (e.g., `api-alerts`, `docs-workflows`).
- Combine inferred change type (see Step 4) with those area keywords to build a slug like `fix/api-alerts-docs`.
- If multiple commits with similar names already exist, append a short sequence suffix (`-v2`, `-hotfix`) rather than a timestamp.
- Use provided custom branch name if specified.

Create and switch to new branch:
```bash
git checkout -b {branch_name}
```

### 4. Analyze Changes for Commit Message

Analyze staged/unstaged changes to generate descriptive commit message (unless `--message` supplied):
- Determine change type with this rubric:
  - `feat`: new endpoints, services, workflows, configs enabling new capability
  - `fix`: bug or regression fixes, hotfixes, refactors that resolve defects
  - `docs`: documentation-only updates (Markdown, diagrams, workflows)
- Combine change type with concise subject referencing main component.
- If user provided `--message`, skip auto generation and reuse supplied value (still validate it follows conventional commit style if possible).

### 5. Stage and Commit Changes

Stage all changes:
```bash
git add .
```

Preview staged snapshot (safety check without user prompt) so the workflow log shows what will be committed:
```bash
git status --short
```

Commit with generated (or provided) message:
```bash
git commit -m "{commit_message}"
```

### 6. Push Branch

Push new branch to remote:
```bash
git push -u origin {branch_name}
```

### 7. Create Pull Request

Generate PR description:
- Summary of changes based on commit analysis
- List of major files/components modified
- Any breaking changes or migration notes
- Include reviewer mention using parsed `--reviewer` flag (default `@codex`)

Before running `gh pr create`, ensure `gh` CLI is installed and authenticated. If `gh auth status` fails, exit with actionable guidance.

Create PR using GitHub CLI:
```bash
gh pr create --title "{pr_title}" --body "{pr_description}" --base {target_branch} --head {branch_name}
```

Verify PR targets the correct base branch:
```bash
gh pr view --json baseRefName,number,url
```
- If `baseRefName != target_branch`, close the mistaken PR (or edit it) and recreate with the correct base.
### 8. Report Results

Output:
- Branch name created
- Commit message used
- PR URL created
- Confirmation of reviewer mention

## Error Handling

- If git operations fail: Provide clear error message and suggested resolution
- If target branch doesn't exist: Ask user to verify branch name
- If PR creation fails: Provide manual PR creation instructions

## Example Usage

```bash
/create-pr develop
/create-pr main --branch fix-auth-bug
```

## Context

$ARGUMENTS
