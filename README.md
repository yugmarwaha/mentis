# Mentis

A web-based AI tutor that keeps productive struggle. It asks the learner to try first. Then it gives help in steps.

**Status:** Early. The team wrote and tested the tutor policy (`backend/app/policy/`). The evaluator uses a fake model (`backend/app/evaluator/`). There is no real model, web server, or UI yet.

## Modes
- **Learn Mode:** the learner tries first. The tutor gives help in steps.
- **Exam Mode:** direct explanations and practice under time pressure.

## Folders
- `backend/`: Python backend. The policy and the evaluator exist. The web server is planned.
- `frontend/`: React and TypeScript UI.
- `evals/`: scenarios, rubrics, baselines, comparison scripts.
- `docs/`: project brief, research notes, ADRs.

## Stack (proposed)
Python, FastAPI, React, TypeScript, PostgreSQL, LLM API.

## Read more
- [Project brief](docs/PROJECT_BRIEF.md)
- [Research](docs/research.md)
