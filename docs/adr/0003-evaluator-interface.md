# ADR 0003: The evaluator sits behind a model interface

**Status:** Accepted

## Decision
- The evaluator is `evaluate(problem, turns, message, model, max_recent_turns=6, on_failure=None)`. It returns an `Assessment`.
- `Problem` has a statement and an optional `expected_approach`. The evaluator uses it to judge `valid_alternative`.
- `model` is a small interface: it takes a prompt and returns text that should be JSON.
- Version 1 ran on a fake model. ADR 0004 adds the Haiku client.
- Code checks the reply. The model does not check itself.
- The model sees the problem, the last `max_recent_turns` earlier turns (6 by default), and the latest learner message.
- `turns` holds earlier turns only. The latest learner message is the `message` argument.
- The model does not see the checker result, the state, or the history counts.
- `evaluate` raises `ValueError` or `TypeError` for a text that is blank, too long, has a control character, or has the wrong type. The caller caps and cleans input first.
- `evaluate` rejects an async model with `TypeError`.

## Reply check
1. Parse the reply as JSON.
2. Map each field to the `Assessment` types. Reject unknown values. `attempt` and `stuck` are accepted in any ASCII letter case.
3. If the model call fails or the reply is invalid, the evaluator calls the model again once.
4. If the second try also fails, return the fallback form.
5. If the model raises `ModelRefusal`, make no second call. Return the fallback form.
6. If the model raises `ModelSetupError`, do not retry. Raise it again. A setup error is a wrong key, no permission, an unknown model, or a bad request.

## Failure callback
`on_failure(kind, detail)` is optional. The evaluator calls it once for each failed try. The kinds are `call_failed`, `invalid_reply`, `refusal`, and `setup_error`. The detail is a class name. The evaluator calls it with `("fallback", "")` before it returns the fallback form. It never passes reply text, prompt text, or an error message. The caller owns the callback. If the model raises `ModelSetupError`, an error from the callback is ignored and the caller gets `ModelSetupError`. On all other paths, a callback error propagates.

## Fallback form
`attempt` none, `stuck` unclear, `misconception` `None`, `valid_alternative`, `asks_for_solution`, and `ambiguous_question` false, and `uncertain` true.

The fallback form claims nothing about the learner. The policy never gives credit, an explanation, or a solution when `uncertain` is true.

Rule for the caller: when `ModelSetupError` is raised, report a setup error. Do not ask the learner to send the message again. When `is_fallback(assessment)` is true, the caller does these things:
1. Do not call `decide`.
2. Show a fixed message: "I could not read that. Please send it again."
3. Change no history counts and no state.
4. Do not store the form as a learner attempt.

Limit: a model reply that equals the fallback form gets the same treatment.

## Options considered
- Fake model first: chosen. Tests are free and run offline. Prompt quality stays unproven.
- Real API now: proves the prompt early. It needs a key and costs money for each test run.

## Why
The policy depends on the form. A wrong form gives a wrong action. The reply check keeps a bad reply from reaching the policy.

## Revisit when
- The Haiku client changes. Measure each field against labeled examples in `evals/`.
- The fallback form shows up often in real sessions. The caller logs each fallback, so the rate is known.
