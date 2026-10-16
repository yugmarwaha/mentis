# ADR 0001: First domain is introductory programming

**Status:** Accepted

## Decision
- Build for introductory Python first.
- Keep the subject out of the policy. Only the answer checker knows the subject. For programming, the checker runs the learner's code.
- For physics or astronomy later, add a new checker. Do not change the policy.

## Options considered
- Introductory programming: chosen. Code can run, so checks are easy.
- Introductory physics with numeric problems: matches the developer's class. Reasoning steps are harder to check.
- Astronomy concept questions: matches the developer's class. No automatic check, so it is the hardest to evaluate.

## Why
Code can run, so attempts and answer leaks are easy to check. Concept questions in astronomy have no automatic check.

## Not decided
How to run learner code safely. Write an ADR before you run any learner code.

## Revisit when
- A second checker plugs in with no policy change. Then move to physics or astronomy.
- Programming scenarios stop showing the behavior we test.
