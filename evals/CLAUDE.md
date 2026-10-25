# evals

Scenarios, grading rubrics, baseline prompts, and comparison scripts. Status: one eval exists, the scenario label eval. The rest of the design is proposed. See `docs/PROJECT_BRIEF.md`, section 8.

## Scenario label eval
- `scenario_labels.json`: one case for each learner message in the five conversations of `docs/scenarios.md`. Each case has the problem, the earlier turns, the message, and the expected labels. The labels follow the label guide in `docs/assessment.md`.
- `run_scenarios.py`: sends each case to the Haiku client through `app.evaluator.evaluate`. It prints the fallback count and the failure kinds first. Then it prints expected and got values for each field, and the agreement for each field. The scores leave out fallback cases.

## Run it
1. Set `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` in your shell. The SDK reads it from the environment.
2. Run `cd backend && uv run python ../evals/run_scenarios.py`.
3. Add `--model-id ID`, `--effort LEVEL`, or `--max-tokens N` to try other settings. `LEVEL` is low, medium, high, xhigh, or max.

The script makes real API calls. It costs a little money. The developer runs it by hand.

Exit codes:
- 0: done.
- 2: no key, a bad option, or an argument error. A blank `--model-id` is a bad option.
- 3: every case fell back. The script prints `All calls failed.`
- 4: setup error. Check the key and the model ID.
- 1: unexpected error. Python prints a traceback.

## Known issue
For s4-m2, the label `misconception_present` is false on purpose. A `true` label makes the policy explain where scenario 4 asks a question. Decide later.

## Know before you change
- The labels are a first draft by one person. Review them before you trust a low agreement score.
- A change to the label guide needs a matching change in `scenario_labels.json`.
