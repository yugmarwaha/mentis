# Git workflow

One developer works in this repository. The developer decides when a change needs a branch and a pull request (PR).

## Branches
- Create a branch only when the developer says so. Do not create a branch on your own.
- Without that instruction, commit to the current branch. Check the current branch before you start work.
- Before a large change, say that a branch may be better. Suggest a name. Wait for the answer.
- Name the branch `type/short-name`. Use lowercase and hyphens: `fix/scroll-jump`.
- Use one of these types:
  - `feat`: a new feature.
  - `fix`: a bug fix.
  - `docs`: documents only.
  - `refactor`: change the code structure, not the behavior.
  - `test`: add or change tests only.
  - `chore`: config, dependencies, tooling.
- Start each branch from an up-to-date `main`.

## Design documents
- Write a design document (ADR, plan, spec) and leave it uncommitted. The developer reads it first.
- Commit it only after the developer approves. Follow `.claude/rules/commits.md`.

## Commits
- Make small commits with specific messages. Follow `.claude/rules/commits.md`.

## Pull requests
Open a PR only for a branch the developer asked for.
1. Make sure the relevant tests pass. If no tests exist yet, say so.
2. Ask the developer before you push the branch.
3. Push the branch. Open a PR to `main`.
4. Write the PR title like a commit subject. In the body, say what changed, why, and how you tested it. Keep it short.
5. The developer reviews the PR and merges it on GitHub.

- Do not merge a PR yourself.
- Ask before you push to `main`.
- After the merge, update local `main`. Ask before you delete the old branch.
- Keep `main` stable.

## Remote
- The remote is `origin` on GitHub: `yugmarwaha/mentis`.
