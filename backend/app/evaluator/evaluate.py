from __future__ import annotations

import inspect

from app.policy.types import Assessment

from .parse import ReplyError, parse_reply
from .prompt import NOTE_CALL_FAILED, NOTE_INVALID_REPLY, build_prompt
from .types import FALLBACK, ModelRefusal, ModelSetupError, Problem, Turn, check_text


def _report(on_failure, kind: str, detail: str) -> None:
    if on_failure is not None:
        on_failure(kind, detail)


def _try(model, prompt: str, on_failure) -> tuple[Assessment | None, str | None]:
    """Call the model once. Return (assessment, None) or (None, note for a retry).

    Return (None, None) when a retry cannot help (a refusal).
    """
    try:
        reply = model.complete(prompt)
    except ModelSetupError as error:
        try:
            _report(on_failure, "setup_error", type(error).__name__)
        except Exception:
            pass  # A failing callback must not hide the setup error.
        raise
    except ModelRefusal:
        _report(on_failure, "refusal", "ModelRefusal")
        return None, None
    except Exception as error:
        _report(on_failure, "call_failed", type(error).__name__)
        return None, NOTE_CALL_FAILED
    if inspect.isawaitable(reply):
        close = getattr(reply, "close", None)
        if callable(close):
            close()
        _report(on_failure, "call_failed", type(reply).__name__)
        return None, NOTE_CALL_FAILED
    try:
        return parse_reply(reply), None
    except ReplyError:
        _report(on_failure, "invalid_reply", "ReplyError")
        return None, NOTE_INVALID_REPLY


def evaluate(
    problem: Problem,
    turns: list[Turn] | tuple[Turn, ...],
    message: str,
    model,
    max_recent_turns: int = 6,
    on_failure=None,
) -> Assessment:
    """Assess the latest learner message.

    `turns` holds EARLIER turns only. The latest learner message is `message`.
    Raise TypeError or ValueError for a blank, oversized, control-character, or
    wrong-typed text. The caller caps and cleans input first.

    `on_failure(kind, detail)` is called once for each failed try, and once with
    ("fallback", "") before FALLBACK is returned. `detail` is a class name or "".
    It never holds reply text, prompt text, or an exception message.
    Raise ModelSetupError when the model reports one. On this path an error from
    `on_failure` is ignored, so the caller always gets ModelSetupError. A refusal gives FALLBACK
    with no retry.
    """
    if not isinstance(problem, Problem):
        raise TypeError("problem must be a Problem")
    if not isinstance(turns, (list, tuple)) or not all(isinstance(t, Turn) for t in turns):
        raise TypeError("turns must be a list or tuple of Turn")
    check_text(message, "message")
    if on_failure is not None and not callable(on_failure):
        raise TypeError("on_failure must be None or a callable")
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
    result, note = _try(model, first_prompt, on_failure)
    if result is not None:
        return result
    if note is not None:
        result, _ = _try(model, build_prompt(problem, recent, message, note), on_failure)
        if result is not None:
            return result
    _report(on_failure, "fallback", "")
    return FALLBACK
