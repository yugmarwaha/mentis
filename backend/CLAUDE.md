# backend

Python backend. Status: the policy, the evaluator, and the Haiku client exist. There is no web server yet.

Each of `app/policy/`, `app/evaluator/`, `app/llm/`, and `tests/` has its own `CLAUDE.md`.

## Policy (`app/policy/`)
- `decide(...)` is a pure function. It returns the next action, the next state, and what the response generator may reveal.
- Rules and their order: `docs/state-machine.md` and `docs/adr/0002-policy-as-rules.md`.
- The package uses the standard library only. Do not add I/O, a clock, randomness, or a model call. Do not add time or frustration inputs. Tests enforce this.
- Config values in `config.py` are placeholders, untested.
- Wrong-typed inputs raise `TypeError`. Pass `None` for no misconception, and real booleans for flags.

## Evaluator (`app/evaluator/`)
- `evaluate(problem, turns, message, model, max_recent_turns=6, on_failure=None)` builds a prompt, calls `model.complete`, and returns an `Assessment`.
- `Problem` has an optional `expected_approach`. The model uses it to judge `valid_alternative`.
- `parse_reply` checks the reply. It raises `ReplyError` for each invalid reply.
- If a call fails or the reply is invalid, the evaluator makes one retry. If the retry fails, it returns `FALLBACK`. `is_fallback(assessment)` detects it.
- `ModelRefusal` gives `FALLBACK` with no retry. `ModelSetupError` is raised again with no retry. If `on_failure` fails on that path, the caller still gets `ModelSetupError`.
- `on_failure(kind, detail)` reports each failed try. The kinds are `call_failed`, `invalid_reply`, `refusal`, `setup_error`, and a final `fallback`. The detail is a class name. It never holds reply text, prompt text, or an error message.
- `evaluate` raises `ValueError` or `TypeError` for a text that is blank, too long, has a control character, or has the wrong type. The caller caps and cleans input first.
- `turns` holds earlier turns only. The latest learner message is `message`.
- The prompt has the problem, the last few turns, and the latest message. Each text is JSON-encoded in a data section. It has no checker result, state, or history count.
- `model.complete` must be a normal function. The evaluator rejects an async model with `TypeError`. A reply that is awaitable counts as a failed call.
- `ScriptedModel` is the fake model for tests. `HaikuModel` is the Haiku client (see below).
- The package uses the standard library and `app.policy.types` only. `app.policy` must not import it. Tests enforce this.
- Interface and reply check: `docs/adr/0003-evaluator-interface.md`.

## Haiku client (`app/llm/`)
- `HaikuModel` implements the `Model` interface with the Anthropic SDK. It calls a large language model (LLM). The default model is `claude-haiku-5-5` at `low` effort.
- The SDK reads `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` from the environment. Never store the key in the repository.
- The call has a 30-second timeout and no SDK retries. The evaluator retries once.
- Only `stop_reason` `end_turn` returns text. `refusal` raises `ModelRefusal`. Any other value, or no text block, raises `ModelCallError`.
- A missing key, a wrong key, no permission, an unknown model, or a bad request raises `ModelSetupError`.
- Details and rules: `app/llm/CLAUDE.md` and `docs/adr/0004-haiku-evaluator-model.md`.
- The scenario eval runs the five scenarios. It costs a little money and needs the key. Run it with `cd backend && uv run python ../evals/run_scenarios.py`.

## Caller contract (the policy does not track these)
- When `is_fallback(assessment)` is true, do not call `decide`. Show the fixed message "I could not read that. Please send it again." Change no history counts and no state. Do not store the form as a learner attempt.
- A model reply that equals the fallback form gets the same treatment.
- Log the `on_failure` kinds and the fallback count.
- Catch `ModelSetupError`. Report a setup error. Do not tell the learner to send the message again.
- Log each fallback, so the fallback rate is known.
- `History.helped_attempts`: meaningful attempts before this message that got a tutor reply, for each problem. Excludes the current message.
- `History.low_effort_streak`: consecutive earlier learner messages with attempt `none` or `guess`. Do not count a question (`ambiguous_question`) as low effort. Reset after any other message.
- `History.help_streak`: consecutive earlier tutor hints or explanations, for the current problem. Reset after any other action.

## Tests
`cd backend && uv run pytest -q`

## Planned
Session and learning-state manager, response generator.
