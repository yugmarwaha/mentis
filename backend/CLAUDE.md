# backend

Python backend. Status: the policy and the evaluator exist. There is no web server and no real model yet.

Each of `app/policy/`, `app/evaluator/`, and `tests/` has its own `CLAUDE.md`.

## Policy (`app/policy/`)
- `decide(...)` is a pure function. It returns the next action, the next state, and what the response generator may reveal.
- Rules and their order: `docs/state-machine.md` and `docs/adr/0002-policy-as-rules.md`.
- The package uses the standard library only. Do not add I/O, a clock, randomness, or a model call. Do not add time or frustration inputs. Tests enforce this.
- Config values in `config.py` are placeholders, untested.
- Wrong-typed inputs raise `TypeError`. Pass `None` for no misconception, and real booleans for flags.

## Evaluator (`app/evaluator/`)
- `evaluate(problem, turns, message, model, max_recent_turns=6)` builds a prompt, calls `model.complete`, and returns an `Assessment`.
- `Problem` has an optional `expected_approach`. The model uses it to judge `valid_alternative`.
- `parse_reply` checks the reply. It raises `ReplyError` for each invalid reply.
- If a call fails or the reply is invalid, the evaluator calls the model once more. If the second try fails, it returns `FALLBACK`. `is_fallback(assessment)` detects it.
- `evaluate` raises `ValueError` or `TypeError` for a text that is blank, too long, has a control character, or has the wrong type. The caller caps and cleans input first.
- `turns` holds earlier turns only. The latest learner message is `message`.
- The prompt has the problem, the last few turns, and the latest message. Each text is JSON-encoded in a data section. It has no checker result, state, or history count.
- `model.complete` must be a normal function. The evaluator rejects an async model with `TypeError`. A reply that is awaitable counts as a failed call.
- Only the fake model `ScriptedModel` exists. Add the real model client later.
- The package uses the standard library and `app.policy.types` only. `app.policy` must not import it. Tests enforce this.
- Interface and reply check: `docs/adr/0003-evaluator-interface.md`.

## Caller contract (the policy does not track these)
- When `is_fallback(assessment)` is true, do not call `decide`. Show the fixed message "I could not read that. Please send it again." Change no history counts and no state. Do not store the form as a learner attempt.
- A real model reply that equals the fallback form gets the same treatment.
- Log each fallback, so the fallback rate is known.
- `History.helped_attempts`: meaningful attempts before this message that got a tutor reply, for each problem. Excludes the current message.
- `History.low_effort_streak`: consecutive earlier learner messages with attempt `none` or `guess`. Do not count a question (`ambiguous_question`) as low effort. Reset after any other message.
- `History.help_streak`: consecutive earlier tutor hints or explanations, for the current problem. Reset after any other action.

## Tests
`cd backend && uv run pytest -q`

## Planned
Session and learning-state manager, real model client for the evaluator, response generator.
