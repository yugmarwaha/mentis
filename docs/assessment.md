# Assessment form (draft)

Status: draft, not reviewed. Domain: introductory Python.

The evaluator (the model) reads the last learner message and fills in this form. The policy reads the form and the current state. See `state-machine.md`.

The answer checker adds one more input. In programming, it runs the learner's code. See ADR 0001.

## Fields

| Field | Values | Meaning |
|---|---|---|
| `attempt` | none, partial, full | `none`: no idea offered. `partial`: an idea or incomplete code. `full`: a complete try, right or wrong. |
| `stuck` | yes, no, unclear | The learner cannot make progress. |
| `misconception` | none, or a short label | A wrong belief in the message. |
| `valid_alternative` | yes, no | The approach differs from the expected one but works. |
| `asks_for_solution` | yes, no | The learner asks for the answer or code. |
| `ambiguous_question` | yes, no | The question has more than one good answer. |
| `uncertain` | yes, no | The evaluator is not sure about its own judgment. |

Checker input: `passes`, `fails`, `cannot_run`, or `not_checked`.

Length is not a field. A long message is not proof of effort.

## Examples

| Conversation, learner message | attempt | stuck | misconception | valid_alternative | asks_for_solution | ambiguous_question | checker |
|---|---|---|---|---|---|---|---|
| 1. `return sorted(xs)[-1]` | full | no | none | yes | no | no | passes |
| 2. "I don't know where to start." | none | yes | none | no | no | no | not_checked |
| 2. "I add 2 and 4, then add 6." | partial | no | none | no | no | no | not_checked |
| 3. "`range(5)` prints 1 to 5." | full | no | `range(n)` starts at 1 | no | no | no | fails |
| 4. "Just give me the code." | none | unclear | none | no | yes | no | not_checked |
| 4. Product code that always returns 0 | full | yes | start with 0 for a product | no | no | no | fails |
| 5. "What is the best way to loop over a list?" | none | no | none | no | no | yes | not_checked |

## Open decisions
1. Can the evaluator judge `stuck` from one message? Repeated lack of progress may be a better signal. It would come from the history.
2. Is the misconception a free label or a fixed list for each problem?
3. Which fields are reliable enough to drive the policy? Measure each field against labeled examples before we trust it.
4. What should the policy do when `uncertain` is yes?
