# backend

Python backend. Status: only the policy exists. There is no web server yet.

## Policy (`app/policy/`)
- `decide(...)` is a pure function. It returns the next action, the next state, and what the response generator may reveal.
- Rules and their order: `docs/state-machine.md` and `docs/adr/0002-policy-as-rules.md`.
- The package uses the standard library only. Do not add I/O, a clock, randomness, or a model call. Do not add time or frustration inputs. Tests enforce this.
- Config values in `config.py` are placeholders, untested.
- Wrong-typed inputs raise `TypeError`. Pass `None` for no misconception, and real booleans for flags.

## Caller contract (the policy does not track these)
- `History.helped_attempts`: meaningful attempts before this message that got a tutor reply, for each problem. Excludes the current message.
- `History.low_effort_streak`: consecutive earlier learner messages with attempt `none` or `guess`. Do not count a question (`ambiguous_question`) as low effort. Reset after any other message.
- `History.help_streak`: consecutive earlier tutor hints or explanations, for the current problem. Reset after any other action.

## Tests
`cd backend && uv run pytest -q`

## Planned
Session and learning-state manager, reasoning evaluator, response generator.
