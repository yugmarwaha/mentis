from __future__ import annotations

import inspect

from app.policy.types import Assessment

from .parse import ReplyError, parse_reply
from .prompt import NOTE_CALL_FAILED, NOTE_INVALID_REPLY, build_prompt
from .types import FALLBACK, Problem, Turn, check_text


def _try(model, prompt: str) -> tuple[Assessment | None, str | None]:
    """Call the model once. Return (assessment, None) or (None, note for a retry)."""
    try:
        reply = model.complete(prompt)
    except Exception:
        return None, NOTE_CALL_FAILED
    if inspect.isawaitable(reply):
        close = getattr(reply, "close", None)
        if callable(close):
            close()
        return None, NOTE_CALL_FAILED
    try:
        return parse_reply(reply), None
    except ReplyError:
        return None, NOTE_INVALID_REPLY


def evaluate(
    problem: Problem,
    turns: list[Turn] | tuple[Turn, ...],
    message: str,
    model,
    max_recent_turns: int = 6,
) -> Assessment:
    """Assess the latest learner message.

    `turns` holds EARLIER turns only. The latest learner message is `message`.
    Raise TypeError or ValueError for a blank, oversized, control-character, or
    wrong-typed text. The caller caps and cleans input first.
    """
    if not isinstance(problem, Problem):
        raise TypeError("problem must be a Problem")
    if not isinstance(turns, (list, tuple)) or not all(isinstance(t, Turn) for t in turns):
        raise TypeError("turns must be a list or tuple of Turn")
    check_text(message, "message")
    if type(max_recent_turns) is not int:
        raise TypeError("max_recent_turns must be an int")
    if max_recent_turns < 1:
        raise ValueError("max_recent_turns must be at least 1")
    complete = getattr(model, "complete", None)
    if not callable(complete):
        raise TypeError("model must have a complete method")
    if inspect.iscoroutinefunction(complete) or inspect.iscoroutinefunction(
        getattr(complete, "__call__", None)
    ):
        raise TypeError("async models are not supported")

    recent = list(turns)[-max_recent_turns:]
    # Build the prompts outside the model try. A prompt bug must raise.
    first_prompt = build_prompt(problem, recent, message)
    result, note = _try(model, first_prompt)
    if result is not None:
        return result
    result, _ = _try(model, build_prompt(problem, recent, message, note))
    return result if result is not None else FALLBACK
