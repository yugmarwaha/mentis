# tests

Run: `cd backend && uv run pytest -q`

## Files
- `test_policy_architecture.py`: guards for the policy. Purity, signatures, field names, frozen types, rules over all inputs.
- `test_policy_scenarios.py`: the conversations in `docs/scenarios.md` and pinned decisions.
- `test_evaluator.py`: guards for the evaluator. Purity, reply check, retry, `FALLBACK`, prompt content.
- `test_llm.py`: guards for the Haiku client. Request shape, error handling, schema, and the secret scan.
- `test_eval_script.py`: guards for the scenario eval. The label file, exit codes, and fallback scoring.
- `conftest.py`: shared helpers.

## Know before you change
- A test guards a design decision. Do not add a test that only repeats the code.
- A failing architecture test means a decision changed. Ask the developer before you edit the test.
- Use `ScriptedModel`. Do not call the Haiku client with a real key in a unit test.
