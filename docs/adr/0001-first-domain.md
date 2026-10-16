# ADR 0001: First domain is introductory programming

**Status:** Accepted

## Context
The brief leaves the first subject open (section 12, question 1). Tutoring on broad topics makes evaluation very hard.

The developer plans to move to physics or astronomy later. The developer also wants to test Mentis in an astronomy class.

## Options

| Option | For | Against |
|---|---|---|
| 1. Introductory programming | The tutor can run the learner's code to check an attempt. "Meaningful attempt" and "premature disclosure" are easier to define. | It does not match the developer's classes. Running learner code needs a safe, isolated environment. |
| 2. Introductory physics (numeric problems) | It matches the developer's classes. A numeric answer is easy to check. | The reasoning steps are harder to check than program output. Units and assumptions add cases. |
| 3. Astronomy (concept questions) | It matches the developer's class. | No automatic check exists. This is the "oxygen" case from the brief. The evaluator must judge everything. This option is the hardest to evaluate. |

## Decision
Use option 1 for the first version. Prove the intervention policy on programming first.

Keep the subject separate from the policy:
- The policy does not depend on running code.
- One part, the **answer checker**, knows the subject.
- The programming checker runs the learner's code.
- A later checker can use a numeric check or the model's judgment.

## Not decided here
- How to run learner code safely. This needs its own ADR.
- The thresholds in the policy.
- The state machine.

## Evidence to revisit
Reconsider this decision if:
- The policy works on programming scenarios, and a second checker can plug in without changes to the policy. Then move to physics or astronomy.
- Programming scenarios do not show the behavior we want to test. Then choose another domain.
