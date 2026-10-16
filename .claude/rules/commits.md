# Commits

- Make one logical change in each commit. Keep commits small.
- Write the subject in the imperative: "Fix scroll jump in chat window".
- Name the specific change and where it applies. Say what the code does now, not which area you worked on.
- Keep the subject to 50 characters or fewer. No period at the end.
- Add a body only when the reason is not clear from the subject. Keep it to 3 lines or fewer.
- Do not use vague subjects: "frontend implemented", "updates", "fix bug", "WIP", "misc changes".
- Do not mix unrelated changes. Split them into separate commits.
- Do not commit code that fails its tests.
- Follow `.claude/rules/writing-style.md`.

## Examples

| Bad | Good |
|---|---|
| frontend implemented | Add attempt input form to Learn Mode |
| fix bug | Fix scroll jump when a new message arrives |
| policy changes | Select a hint when the learner is stuck after an attempt |
| update tests | Test that "just tell me" gets a hint, not a solution |
| db stuff | Store each intervention with its attempt ID |
