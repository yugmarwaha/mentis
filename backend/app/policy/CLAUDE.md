# policy

The tutor policy. A pure function that picks the next action. Rules: `docs/state-machine.md`, `docs/adr/0002-policy-as-rules.md`.

## Files
- `decide.py`: `decide(...)` and `required_attempts(...)`. The rules, in order.
- `types.py`: enums (state, action, reveal, and the assessment values), `Assessment`, `History`, `Decision`.
- `config.py`: `PolicyConfig` and `DEFAULT_CONFIG`. The thresholds. All are untested placeholders.

## Know before you change
- Use the standard library only. Add no I/O, clock, randomness, or model call. Add no time or frustration input. Tests enforce this.
- Do not import `app.evaluator`.
- Put a threshold in `config.py`, not in a rule.
- A change to a rule needs a matching change in `docs/state-machine.md` and in the tests. Run the `verify-change` skill.
- The caller keeps the history counts. See `backend/CLAUDE.md`.
