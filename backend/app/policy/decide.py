from __future__ import annotations

from .config import DEFAULT_CONFIG, PolicyConfig
from .types import (
    Action,
    Assessment,
    Attempt,
    Checker,
    Decision,
    Difficulty,
    Familiarity,
    History,
    Reveal,
    State,
    Stuck,
)


def _check(
    state: State,
    assessment: Assessment,
    checker: Checker,
    history: History,
    difficulty: Difficulty,
    familiarity: Familiarity,
    config: PolicyConfig,
) -> None:
    for value, expected in (
        (state, State),
        (checker, Checker),
        (difficulty, Difficulty),
        (familiarity, Familiarity),
    ):
        if not isinstance(value, expected):
            raise TypeError(f"expected {expected.__name__}, got {type(value).__name__}")
    for value, expected in (
        (assessment, Assessment),
        (history, History),
        (config, PolicyConfig),
    ):
        if type(value) is not expected:
            raise TypeError(f"expected {expected.__name__}, got {type(value).__name__}")


def required_attempts(
    difficulty: Difficulty,
    familiarity: Familiarity,
    config: PolicyConfig = DEFAULT_CONFIG,
) -> int:
    for value, expected in ((difficulty, Difficulty), (familiarity, Familiarity)):
        if not isinstance(value, expected):
            raise TypeError(f"expected {expected.__name__}, got {type(value).__name__}")
    if type(config) is not PolicyConfig:
        raise TypeError(f"expected PolicyConfig, got {type(config).__name__}")
    return max(
        config.min_required_attempts,
        config.base_required_attempts
        + config.difficulty_offset[difficulty]
        + config.familiarity_offset[familiarity],
    )


def _ask() -> Decision:
    return Decision(Action.ASK, State.ATTEMPTING, Reveal.NOTHING)


def _low_effort(attempt: Attempt, streak: int, next_state: State) -> Decision:
    if streak == 0:
        action = Action.INVITE if attempt is Attempt.NONE else Action.ASK
        return Decision(action, next_state, Reveal.NOTHING)
    if streak == 1:
        hint_state = State.HELPING if next_state is State.ATTEMPTING else next_state
        return Decision(Action.HINT, hint_state, Reveal.HINT)
    return Decision(Action.NUDGE, next_state, Reveal.NOTHING)


def decide(
    state: State,
    assessment: Assessment,
    checker: Checker,
    history: History,
    difficulty: Difficulty,
    familiarity: Familiarity,
    config: PolicyConfig = DEFAULT_CONFIG,
) -> Decision:
    _check(state, assessment, checker, history, difficulty, familiarity, config)
    a = assessment
    helped = history.helped_attempts
    if checker is Checker.CANNOT_RUN:
        checker = Checker.FAILS
    low_effort = a.attempt in (Attempt.NONE, Attempt.GUESS)
    solution = Decision(Action.SOLUTION, State.SOLUTION_SHOWN, Reveal.FULL_SOLUTION)

    if state is State.SOLUTION_SHOWN:
        return Decision(Action.TRANSFER_PROBLEM, State.TRANSFER, Reveal.NOTHING)
    if state is State.DONE:
        return Decision(Action.END, State.DONE, Reveal.NOTHING)

    if state is State.TRANSFER:
        if (
            checker is Checker.PASSES
            and a.attempt is Attempt.FULL
            and not a.uncertain
            and a.misconception is None
        ):
            return Decision(Action.END, State.DONE, Reveal.NOTHING)
        if (
            a.stuck is Stuck.YES
            and history.help_streak >= config.transfer_helps_before_solution
            and not a.uncertain
            and checker is not Checker.PASSES
            and history.low_effort_streak == 0
        ):
            return solution
        if a.misconception is not None:
            if a.uncertain or (helped == 0 and history.low_effort_streak == 0):
                return Decision(Action.ASK, State.TRANSFER, Reveal.NOTHING)
            return Decision(Action.EXPLAIN, State.TRANSFER, Reveal.ERROR_EXPLANATION)
        if a.attempt in (Attempt.PARTIAL, Attempt.FULL) and a.stuck is Stuck.YES:
            return Decision(Action.HINT, State.TRANSFER, Reveal.HINT)
        if low_effort:
            return _low_effort(a.attempt, history.low_effort_streak, State.TRANSFER)
        return Decision(Action.INVITE, State.TRANSFER, Reveal.NOTHING)

    # State is ATTEMPTING or HELPING.
    full = a.attempt is Attempt.FULL
    if (
        a.valid_alternative
        and a.attempt in (Attempt.PARTIAL, Attempt.FULL)
        and checker is not Checker.FAILS
        and helped == 0
    ):
        return _ask()
    if (
        checker is Checker.PASSES
        and full
        and not a.uncertain
        and a.misconception is None
    ):
        return Decision(Action.CREDIT, State.TRANSFER, Reveal.NOTHING)
    if full and checker is Checker.NOT_CHECKED and helped == 0:
        return _ask()
    if (
        a.stuck is Stuck.YES
        and helped >= required_attempts(difficulty, familiarity, config)
        and not a.uncertain
        and checker is not Checker.PASSES
        and history.low_effort_streak == 0
    ):
        return solution
    if a.misconception is not None:
        if a.uncertain or (helped == 0 and history.low_effort_streak == 0):
            return _ask()
        return Decision(Action.EXPLAIN, State.HELPING, Reveal.ERROR_EXPLANATION)
    if a.ambiguous_question and a.attempt is Attempt.NONE:
        return _ask()
    if low_effort:
        return _low_effort(a.attempt, history.low_effort_streak, State.ATTEMPTING)
    if checker is Checker.PASSES and full:
        return _ask()
    if a.attempt in (Attempt.PARTIAL, Attempt.FULL) and a.stuck is Stuck.YES:
        return Decision(Action.HINT, State.HELPING, Reveal.HINT)
    return _ask()
