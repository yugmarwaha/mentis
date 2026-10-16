# ADR 0002: The policy is rules in code

**Status:** Proposed

## Decision
- The backend policy is plain code, not the model.
- It is a pure function. It makes no model calls.
- Inputs: current state, assessment form, checker result, session history, problem difficulty, learner familiarity.
- Outputs: next action, next state, what the response generator may reveal.
- Put thresholds in config. Mark each one untested.
- The model only writes the message for the chosen action.

## Options considered
- Rules in code: chosen. Testable and enforceable. A person writes every rule, so cases can be missed.
- The model picks the action: flexible. The backend cannot enforce limits, and it is hard to test.
- A trained classifier: may find patterns people miss. It needs reliable labels, which we lack.

## Why
Code enforces limits and can be tested with fixed inputs. A prompt cannot enforce them.

## Baseline
Keep "the model picks the action" as a comparison in `evals/`.

## Revisit when
- The failure log shows the rules miss many cases.
- Reliable labels exist, and a classifier beats the rules on held-out examples.
