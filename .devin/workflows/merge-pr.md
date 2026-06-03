---
description: Revisit open PRs, address @codex feedback, and merge when conditions are satisfied.
---

## User Input

```text
$ARGUMENTS
```

## Goal

Systematically review open PRs, resolve any outstanding feedback from @codex, and merge once all concerns are closed or no new feedback arrives within the configured wait window.

## Usage

```bash
/merge-pr
/merge-pr --pr 21
/merge-pr --wait-minutes 10
```

## Parameters

- **pr**: Optional pull request number. If omitted, process all open PRs authored by the current user.
- **wait_minutes**: Minutes to wait for new feedback after posting updates (default: `10`).

## Execution Steps

### 1. Determine Target PRs

1. Parse `$ARGUMENTS` for `--pr` and `--wait-minutes` flags.
2. If `--pr` supplied, target that PR only. Otherwise run:
   ```bash
   gh pr list --author @me --state open --json number,title,url
   ```
3. Abort if no open PRs match.

### 2. Fetch Current Feedback

For each target PR:
1. Pull latest metadata, reviews, and creation time:
   ```bash
   gh pr view <number> --comments --json number,title,body,reviews,reviewDecision,createdAt
   ```
2. Check for Codex usage-limit responses:
   ```bash
   gh pr view <number> --json comments --jq '.comments[]? | select(.author.login=="chatgpt-codex-connector") | .body'
   ```
   - If the response contains "You have reached your Codex usage limits", treat it as reviewer feedback indicating no further comments will arrive. Add a note for transparency:
     ```bash
     gh pr comment <number> --body "Codex reviewer hit usage limits; proceeding after quiet window unless new feedback appears."
     ```
3. Filter for any reviews by `@codex` with state `COMMENTED` or `CHANGES_REQUESTED`.
4. Extract actionable items (file path, line, summary). Document them in a temporary checklist.

### 3. Apply Fixes & Recommendations

For every feedback item:
1. Reproduce or inspect the referenced code via the files in question.
2. Implement the fix (use existing repo guidance: PEP8, blueprints, services, etc.).
3. Add focused tests/logging if required by the comment.
4. Stage only relevant files:
   ```bash
   git add <paths>
   ```
5. Use conventional commits referencing the PR/area, e.g. `fix: address codex feedback on alerts doc link`.
6. Push the branch:
   ```bash
   git push
   ```
7. Respond to each @codex comment explaining the resolution (link to commit if helpful).

### 4. Re-run CI / Validation (if applicable)

1. Trigger project CI if not automatic.
2. Confirm all checks pass: `gh pr checks <number>`.

### 5. Verify Feedback Closure

1. Request @codex to review (or re-review) via comment or `gh pr review` as appropriate.
2. Determine elapsed time since PR creation using the `createdAt` timestamp fetched earlier:
   - Convert `createdAt` to epoch seconds; compute `elapsed_minutes = (now - createdAt)/60`.
   - If `elapsed_minutes < wait_minutes`, sleep for the remaining minutes (or loop with `sleep 60` + recheck) unless new feedback arrives sooner.
3. Once `elapsed_minutes >= wait_minutes`, poll `gh pr view <number> --json reviews` to ensure there are still no @codex comments. If comments exist, go back to Step 3.
4. If @codex explicitly approves at any point, you may bypass the timer and proceed immediately.

### 6. Merge PR

1. Confirm base branch is up to date (use `gh pr merge --auto` or `git pull --rebase origin <base>` if needed).
2. Merge with preferred method (default `squash`):
   ```bash
   gh pr merge <number> --squash --delete-branch --subject "{final commit msg}" --body "Merged after codex feedback resolved"
   ```
3. If merge fails (conflicts, required checks), resolve issues and repeat Steps 3–5.

## Error Handling

- Missing gh authentication: run `gh auth login` and retry.
- Unresolved conflicts: abort merge, notify user, and resolve manually before rerunning Step 6.
- CI failures: halt merge and address failing tests before continuing.

## Output

Report for each PR:
- PR number & title
- Outstanding @codex items found/resolved
- Commits pushed
- Merge status (merged / waiting for feedback / blocked)

## Context

$ARGUMENTS
