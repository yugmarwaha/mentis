# Glossary (draft)

## Meaningful attempt
A learner message that shows the learner's own reasoning (how or why). A wrong attempt counts. A bare guess ("maybe a loop?") does not. Length does not count. Form values: `partial` and `full`.

## History counts
The three counts that the caller keeps: `helped_attempts`, `low_effort_streak`, and `help_streak`. The policy does not track them. See `backend/CLAUDE.md`.

## Fallback form
The assessment the evaluator returns when it cannot get a valid reply. `attempt` is none, `stuck` is unclear, and `uncertain` is true. When `is_fallback(assessment)` is true, the caller does not call the policy. It shows a fixed message and changes no history counts and no state. See `adr/0003-evaluator-interface.md`.

## Reply check
The code that checks a model reply before the policy sees it. It rejects each invalid reply. See `assessment.md`.

## Premature disclosure
A tutor message that gives working code or the key step when the policy did not allow a solution.
- Disclosure: "Start `total` at 0 and add each item in a loop."
- Allowed: name a concept or ask a question, such as "What do you need to remember between steps?"

## Good intervention
Check two parts. These are checks on tutor behavior, not proof of learning.

**Message quality.** All five must hold:
1. The message matches the action the policy chose.
2. It refers to something specific in the learner's message.
3. It has no premature disclosure.
4. What it says about the code is correct.
5. It leaves the next step to the learner. A question with one obvious answer fails.

**Action quality.** The chosen action fits this learner at this point. Judge it against labeled examples.

## Open
- Who labels the examples?
- Which checks run automatically, and which need a human?
