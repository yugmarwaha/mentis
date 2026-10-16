# Mentis

A web-based AI tutor that keeps productive struggle. It has Learn Mode and Exam Mode.

## Read first
- `docs/PROJECT_BRIEF.md` is the source of project context. Read it before you start work.
- The brief is not a final specification. Challenge its assumptions.

## Folders
- `backend/`: FastAPI app.
- `frontend/`: React and TypeScript UI.
- `evals/`: scenarios, rubrics, baselines, comparison scripts.
- `docs/`: brief, ADRs, research notes.

Each folder has its own `CLAUDE.md`.

## Rules
- `.claude/rules/writing-style.md`: write in ASD-STE100.
- `.claude/rules/commits.md`: write short, specific commits. Get approval before implementation decisions and design documents.
- `.claude/rules/git-workflow.md`: use short-lived branches. Ask before you create a branch, push, merge, or delete.
- `.claude/rules/keep-docs-current.md`: update all affected documents after each change.

## Skills
- `.claude/skills/clear-writing/`: write or revise technical text in Simplified Technical English.
- `.claude/skills/mean-review/`: review finished code to find problems, not to confirm it works.

## Stack (proposed)
Python, FastAPI, React, TypeScript, PostgreSQL, LLM API.
