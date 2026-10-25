# Git workflow

One developer works in this repository. Every change goes through a branch and a pull request (PR).

## Branches
- Create a new branch for every change. This includes documents, config, and small fixes.
- Name the branch `type/short-name`. Use lowercase and hyphens: `fix/scroll-jump`.
- Use one of these types:
  - `feat`: a new feature.
  - `fix`: a bug fix.
  - `docs`: documents only.
  - `refactor`: change the code structure, not the behavior.
  - `test`: add or change tests only.
  - `chore`: config, dependencies, tooling.
- Start each branch from an up-to-date `main`.
- Check the current branch before you start work. Never commit to `main`.
- You may create the branch for a task the developer asked for. Tell the developer the branch name.

## Design documents
- Write a design document (ADR, plan, spec) and leave it uncommitted. The developer reads it first.
- Commit it only after the developer approves. Follow `.claude/rules/commits.md`.

## Commits
- Make small commits with specific messages. Follow `.claude/rules/commits.md`.

## Pull requests
1. Make sure the relevant tests pass. If no tests exist yet, say so.
2. Ask the developer before you push the branch.
3. Push the branch. Open a PR to `main`.
4. Write the PR title like a commit subject. In the body, say what changed, why, and how you tested it. Keep it short.
5. The developer reviews the PR and merges it on GitHub.

- Do not merge a PR yourself. Do not push to `main`.
- After the merge, update local `main`. Ask before you delete the old branch.
- Keep `main` stable.

## Remote
- The remote is `origin` on GitHub: `yugmarwaha/mentis`.
