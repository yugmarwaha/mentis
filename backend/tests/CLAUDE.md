# tests

Run: `cd backend && uv run pytest -q`

## Files
- `test_policy_architecture.py`: guards for the policy. Purity, signatures, field names, frozen types, rules over all inputs.
- `test_policy_scenarios.py`: the conversations in `docs/scenarios.md` and pinned decisions.
- `test_evaluator.py`: guards for the evaluator. Purity, reply check, retry, `FALLBACK`, prompt content.
- `conftest.py`: shared helpers.

## Know before you change
- A test guards a design decision. Do not add a test that only repeats the code.
- A failing architecture test means a decision changed. Ask the developer before you edit the test.
- Use `ScriptedModel`. Do not call a real model in a unit test.
