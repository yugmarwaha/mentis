# Git workflow

Keep the workflow light. One developer works in this repository.

## Branches
- Use a short-lived branch for each substantial change: `feat/`, `fix/`, `refactor/`, or `docs/`.
- Before you start substantial work, check the current branch. If a branch is better, suggest a name.
- Never create or switch a branch without the developer's approval. Wait for the answer.
- Commit small changes directly to `main`: README, `.gitignore`, config, and edits that only keep documents current.
- Put design documents (ADR, plan, spec) on a `docs/` branch. The developer reviews them in a pull request.

## Commits
- Make small commits with specific messages. Follow `.claude/rules/commits.md`.

## Push and merge
- Ask before you push. Ask before you merge. Ask before you delete a branch.
- Push a feature branch to GitHub and open a pull request. The developer reviews the pull request.
- Merge with rebase-and-merge. Do not create merge commits.
- Merge only when the relevant tests pass. If no tests exist yet, say so when you ask.
- Delete the branch after the merge.
- Keep `main` stable.

## Remote
- The remote is `origin` on GitHub: `yugmarwaha/mentis`.
