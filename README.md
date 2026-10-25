# Mentis

A web-based AI tutor that keeps productive struggle. It asks the learner to try first. Then it gives help in steps.

**Status:** Early. The team wrote and tested the tutor policy (`backend/app/policy/`). The evaluator has a Haiku client (`backend/app/llm/`). The scenario eval (`evals/run_scenarios.py`) runs by hand. There is no web server or UI yet.

## Modes
- **Learn Mode:** the learner tries first. The tutor gives help in steps.
- **Exam Mode:** direct explanations and practice under time pressure.

## Folders
- `backend/`: Python backend. The policy, the evaluator, and the Haiku client exist. The web server is planned.
- `frontend/`: React and TypeScript UI.
- `evals/`: scenarios, rubrics, baselines, comparison scripts.
- `docs/`: project brief, research notes, ADRs.

## Stack (proposed)
Python, FastAPI (planned), React, TypeScript, PostgreSQL, Anthropic API (Claude Haiku 5.5).

## Run the tests
```bash
cd backend && uv run pytest -q
```

## Run the scenario eval
The eval calls the Haiku client. It costs a little money. It needs `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` in your environment.

```bash
cd backend && uv run python ../evals/run_scenarios.py
```

## Contribute
Large changes use a branch: `feat/`, `fix/`, `docs/`, `refactor/`, `test/`, or `chore/`. A pull request merges the branch into `main`. See `.claude/rules/git-workflow.md`.

## Read more
- [Project brief](docs/PROJECT_BRIEF.md)
- [Research](docs/research.md)
