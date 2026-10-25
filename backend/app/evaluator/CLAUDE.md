# evaluator

Turns one learner message into an `Assessment` for the policy. Spec: `docs/adr/0003-evaluator-interface.md`, `docs/assessment.md`.

## Files
- `evaluate.py`: `evaluate(...)`. Calls the model. It retries once after an error or an invalid reply. It returns `FALLBACK` after a second failure.
  - `ModelRefusal` gives `FALLBACK` with no retry.
  - `ModelSetupError` is raised again with no retry. An error from `on_failure` on this path is ignored, so the caller always gets `ModelSetupError`.
  - The optional `on_failure(kind, detail)` callback gets each failed try and a final `("fallback", "")`. It never gets reply text, prompt text, or an error message. On all other paths, a callback error propagates.
  - An async model raises `TypeError`. A reply that is awaitable counts as a failed call.
  - A bad text raises `ValueError` or `TypeError`. The caller caps and cleans input first.
  - `turns` holds earlier turns only.
- `prompt.py`: `build_prompt(...)`. A pure function. Instructions come first. Then an optional retry note, a marker line, and the data. Each text in the data is JSON-encoded. The line-break characters U+2028, U+2029, and U+0085 are escaped, so learner text cannot add a prompt line.
- `parse.py`: `parse_reply(...)` and `ReplyError`. Accepts `attempt` and `stuck` in any ASCII letter case. Rejects each invalid reply, including a non-`str` reply, duplicate keys, and a bad `misconception`.
- `types.py`: `Turn`, `Problem` (with `expected_approach`), `Speaker`, `ModelSetupError`, `ModelRefusal`, the `Model` interface, `FALLBACK`, `is_fallback`, and `MAX_TEXT_CHARS`. Text checks reject a `str` subclass, a blank text, a text over the cap, and a control character other than newline, return, and tab.
- `fake.py`: `ScriptedModel`. The fake model that tests use. It rejects a reply that is not a `str` or an `Exception`.

## Know before you change
- Use the standard library and `app.policy.types` only. `app.policy` must not import this package. Tests enforce this.
- Never put raw learner text outside a JSON string in the prompt. This keeps the marker line safe from forgery.
- Do not put the checker result, the state, or the history counts in the prompt.
- Do not use message length as a signal.
- A change to a field meaning needs a matching change in `docs/assessment.md` and in the prompt.
- When `is_fallback(assessment)` is true, the caller does not call the policy, shows a fixed message, and changes no history counts and no state.
- The Haiku client is in `app/llm/`. It implements the `Model` interface.
