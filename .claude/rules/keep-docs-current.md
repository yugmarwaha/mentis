# Keep documents current

- After each change, update all documents that the change affects. This includes bug fixes and new features.
- Do this in the same commit as the change.
- Check these documents:
  - The `CLAUDE.md` in the changed folder, and in each parent folder.
  - `PROJECT_BRIEF.md`, if scope, status, or decisions change.
  - ADRs, READMEs, and other docs that describe the changed code.
- Each folder-level `CLAUDE.md` states what the folder contains, how its parts connect, and what to know before you change it. Keep it short.
- Create a `CLAUDE.md` for a new folder that has several files.
- Remove text that is no longer true. Do not leave old text.
- Follow `.claude/rules/writing-style.md`.
