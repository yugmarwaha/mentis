# evaluator

Turns one learner message into an `Assessment` for the policy. Spec: `docs/adr/0003-evaluator-interface.md`, `docs/assessment.md`.

## Files
- `evaluate.py`: `evaluate(...)`. Calls the model, retries once after an error or an invalid reply, returns `FALLBACK` after a second failure. Rejects an async model with `TypeError`. A reply that is awaitable counts as a failed call. Raises `ValueError` or `TypeError` for a bad text. The caller caps and cleans input first. `turns` holds earlier turns only.
- `prompt.py`: `build_prompt(...)`. A pure function. Instructions come first. Then an optional retry note, a marker line, and the data. Each text in the data is JSON-encoded. The line-break characters U+2028, U+2029, and U+0085 are escaped, so learner text cannot add a prompt line.
- `parse.py`: `parse_reply(...)` and `ReplyError`. Rejects each invalid reply, including a non-`str` reply, duplicate keys, and a bad `misconception`.
- `types.py`: `Turn`, `Problem` (with `expected_approach`), `Speaker`, the `Model` interface, `FALLBACK`, `is_fallback`, and `MAX_TEXT_CHARS`. Text checks reject a `str` subclass, a blank text, a text over the cap, and a control character other than newline, return, and tab.
- `fake.py`: `ScriptedModel`. The fake model that tests use. It rejects a reply that is not a `str` or an `Exception`.

## Know before you change
- Use the standard library and `app.policy.types` only. `app.policy` must not import this package. Tests enforce this.
- Never put raw learner text outside a JSON string in the prompt. This keeps the marker line safe from forgery.
- Do not put the checker result, the state, or the history counts in the prompt.
- Do not use message length as a signal.
- A change to a field meaning needs a matching change in `docs/assessment.md` and in the prompt.
- When `is_fallback(assessment)` is true, the caller does not call the policy, shows a fixed message, and changes no history counts and no state.
- There is no real model client yet. Add it behind the `Model` interface.
