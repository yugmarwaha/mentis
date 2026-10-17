# Assessment form (draft)

The evaluator (the model) fills in this form for each learner message. The policy reads it with the current state. See `state-machine.md`.

| Field | Values | Meaning |
|---|---|---|
| `attempt` | none, guess, partial, full | See the label guide. `partial` and `full` are meaningful (see `glossary.md`). |
| `stuck` | yes, no, unclear | `yes`: the learner says or shows they cannot go on. `no`: they make progress. `unclear`: the message and the recent turns show neither. The policy treats `unclear` as `no`. |
| `misconception` | null, or a short label | A wrong belief in the message. `null` when there is none. A label has 80 characters or fewer, on one line. It does not copy the learner's words or any solution. |
| `valid_alternative` | `true`, `false` | The answer differs from the expected approach but works. It is `true` only with `attempt` partial or full. If no expected approach is given, the model judges from the problem. |
| `asks_for_solution` | `true`, `false` | The learner asks for the answer or code. |
| `ambiguous_question` | `true`, `false` | The latest learner message is a question with more than one good answer. |
| `uncertain` | `true`, `false` | The evaluator is not sure of its own judgment. |

Checker input does not come from the model. It has four values:
- `passes`
- `fails`
- `cannot_run`: the code has an error that stops it running. The rules treat it as `fails`.
- `not_checked`: no result.

Pass real booleans for the flags and `None` for no misconception. The policy rejects other types.

Label guide (the prompt uses the same words):
- `attempt` none: no idea, or no answer to the problem in the message. Examples: a request such as "just tell me", a bare "ok" or "yes", or a question. Also none: a reply to a tutor question about the goal that adds no attempt.
- `attempt` guess: a bare technique or answer idea with no code and no stated reason. Example: "maybe a loop?".
- `attempt` partial: a stated reason, even with "maybe"; a reasoned reply to a tutor question; a worked step in reply to a tutor question; or incomplete code. A bug report with no code is partial.
- `attempt` full: complete code or a complete answer, with or without a reason, right or wrong. Complete code with a bug report is full. Example: `return sorted(xs)[-1]` is full.
- `stuck` yes: the learner says or shows they cannot go on. `stuck` no: the learner makes progress. `stuck` unclear: the message and the recent turns show neither.
- `misconception`: null when there is none. Never write "none". Otherwise a short label of 80 characters or fewer on one line. Do not copy the learner's words or any solution.
- `valid_alternative`: true only with `attempt` partial or full, and only when the answer differs from the expected approach but works. If no expected approach is given, judge from the problem.
- `uncertain`: true when the message fits two labels for `attempt`, or you cannot tell what the learner means. Otherwise false.

Never use message length as a signal.

The prompt tells the model not to copy the learner's words or any solution. No code checks this.

## Reply check
Code checks each model reply (`parse_reply`):
- The reply is one JSON object. One Markdown code fence around it is allowed. The tag `json` is optional and can have any case. Text outside the fence is invalid.
- A duplicate key, `NaN`, or `Infinity` is invalid.
- The object has exactly the seven fields. A missing or extra field is invalid.
- `attempt` and `stuck` are exact lowercase values from the table.
- `misconception` is null, or a string. The string must not be blank. It must be one printable line of 80 characters or fewer. It must contain a letter.
- The model must write `null` for no misconception. The parser also turns `none`, `N/A`, and similar words into `None`.
- The check ignores case, accents, Unicode form, and trailing punctuation. The words are none, null, n/a, na, nil, nothing, no, none found, no misconception(s), no wrong belief(s), and not applicable.
- The reply must be a plain `str`. Any other type is invalid.
- The four flags are JSON booleans. The numbers 0 and 1 and the words "yes" and "no" are invalid.
- `valid_alternative` is invalid when `true` with `attempt` none or guess.

The evaluator calls the model again once, after an invalid reply or a failed call. A second failure gives the fallback form (see ADR 0003).

## Open
- The model judges `stuck` from the last few turns. Measure how well this works.
- `misconception` is a free label. Decide later if a fixed list for each problem is better.
- Measure each field against labeled examples before the policy relies on it.
- How often does the fallback form appear in real sessions?
