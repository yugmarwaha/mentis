from __future__ import annotations

from app.policy.types import Attempt, Stuck

# JSON schema for the seven Assessment fields. `parse_reply` stays the real check.
ASSESSMENT_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "attempt": {"type": "string", "enum": [a.value for a in Attempt]},
        "stuck": {"type": "string", "enum": [s.value for s in Stuck]},
        "misconception": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "valid_alternative": {"type": "boolean"},
        "asks_for_solution": {"type": "boolean"},
        "ambiguous_question": {"type": "boolean"},
        "uncertain": {"type": "boolean"},
    },
    "required": [
        "attempt",
        "stuck",
        "misconception",
        "valid_alternative",
        "asks_for_solution",
        "ambiguous_question",
        "uncertain",
    ],
    "additionalProperties": False,
}
