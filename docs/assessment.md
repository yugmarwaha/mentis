# Assessment form (draft)

The evaluator (the model) fills in this form for each learner message. The policy reads it with the current state. See `state-machine.md`.

| Field | Values | Meaning |
|---|---|---|
| `attempt` | none, guess, partial, full | `none`: no idea. `guess`: a technique or answer with no reasoning. `partial`: some reasoning or incomplete code. `full`: a complete try, right or wrong. `partial` and `full` are meaningful (see `glossary.md`). |
| `stuck` | yes, no, unclear | The learner cannot make progress. The policy treats `unclear` as `no`. |
| `misconception` | none, or a short label | A wrong belief in the message. Pass `None` when there is none. The string "none" counts as a misconception. |
| `valid_alternative` | yes, no | The approach differs from the expected one but works. |
| `asks_for_solution` | yes, no | The learner asks for the answer or code. |
| `ambiguous_question` | yes, no | The latest learner message is a question with more than one good answer. |
| `uncertain` | yes, no | The evaluator is not sure of its own judgment. |

Checker input (not from the model): `passes`, `fails`, `cannot_run` (the code has an error that stops it running; the rules treat it as `fails`), `not_checked` (no result).

Pass real booleans for the yes/no flags and `None` for no misconception. The policy rejects other types.

Label guide:
- A suggestion with a stated reason is `partial`. A bare technique or answer with no reason is `guess` ("maybe a loop?").
- A reply to the tutor's own question that adds reasoning is `partial`. A bare reply is `guess`.
- A bug report with no stated belief is `partial`. Put the wrong assumption behind it, if any, in `misconception`.

Never use message length as a field.

## Open
- Judge `stuck` from one message, or from repeated no-progress in the history?
- Is `misconception` a free label or a fixed list for each problem?
- Measure each field against labeled examples before the policy relies on it.
