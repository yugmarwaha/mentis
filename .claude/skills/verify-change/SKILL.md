---
name: verify-change
description: Verify a change to the policy code or to a design document with three independent read-only reviewers. Use after implementing or changing rules, not for typos.
---

# Verify a change

Cost: three Opus agents. Use it for policy, state machine, or ADR changes only.

1. Run `cd backend && uv run pytest -q`. Stop if tests fail.
2. Start three Opus subagents in parallel. They are read-only. They must not edit the repo or run state-changing git commands. They probe from the scratchpad.
   - **Code review:** read `backend/app/policy/` and the docs. Enumerate inputs. Hunt for decision breaches, unreachable rules, states with no exit, and wrong-typed inputs that get through. Separate bugs from design problems.
   - **Docs versus code:** walk every conversation in `docs/scenarios.md` turn by turn through `decide`. Compare with the tutor tags. Check each row of `docs/state-machine.md` against the code. Report stale or unclear text.
   - **Mutation check:** copy `backend/` to the scratchpad. Apply about 25 mistakes an agent might make (clock import, new time field, hardcoded threshold, rule order swap, wrong reveal level, removed validation). Run the tests on each. Report caught or missed. Name trivial tests and at most 3 tests to add.
3. Give each agent the decisions to honor (read them from `docs/state-machine.md`). Ask for at most 10 findings, most severe first, with a concrete input.
4. Report to the developer in plain words: bugs, decisions that need an answer, and fixes you will make. Change nothing until the developer approves.
