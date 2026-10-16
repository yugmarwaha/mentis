# Git workflow

Keep the workflow light. One developer works in this repository. Do not use pull requests.

## Branches
- Use a short-lived branch for a substantial change: `feat/`, `fix/`, or `refactor/`.
- Work directly on `main` for small changes: README, `.gitignore`, config, documents, and small fixes.
- Before you start work, check the current branch. Say if a branch is better, and suggest a name.
- Never create or switch a branch without the developer's approval. Wait for the answer.

## Design documents
- Write a design document (ADR, plan, spec) and leave it uncommitted. The developer reads it first.
- Commit it only after the developer approves. Follow `.claude/rules/commits.md`.

## Commits
- Make small commits with specific messages. Follow `.claude/rules/commits.md`.

## Merge and push
- Ask before you push, merge, or delete a branch.
- Merge a branch into `main` with a fast-forward or a rebase. Do not create merge commits.
- Merge only when the relevant tests pass. If no tests exist yet, say so when you ask.
- Delete the branch after the merge.
- Keep `main` stable.

## Remote
- The remote is `origin` on GitHub: `yugmarwaha/mentis`.
