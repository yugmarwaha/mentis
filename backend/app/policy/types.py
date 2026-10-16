from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class State(Enum):
    ATTEMPTING = "attempting"
    HELPING = "helping"
    SOLUTION_SHOWN = "solution_shown"
    TRANSFER = "transfer"
    DONE = "done"


class Action(Enum):
    INVITE = "invite"
    ASK = "ask"
    HINT = "hint"
    EXPLAIN = "explain"
    SOLUTION = "solution"
    CREDIT = "credit"
    TRANSFER_PROBLEM = "transfer_problem"
    END = "end"
    NUDGE = "nudge"


class Reveal(Enum):
    NOTHING = "nothing"
    HINT = "hint"
    ERROR_EXPLANATION = "error_explanation"
    FULL_SOLUTION = "full_solution"


class Attempt(Enum):
    NONE = "none"
    GUESS = "guess"
    PARTIAL = "partial"
    FULL = "full"


class Stuck(Enum):
    YES = "yes"
    NO = "no"
    UNCLEAR = "unclear"


class Checker(Enum):
    PASSES = "passes"
    FAILS = "fails"
    CANNOT_RUN = "cannot_run"
    NOT_CHECKED = "not_checked"


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Familiarity(Enum):
    FIRST_TIME = "first_time"
    SOME = "some"
    FAMILIAR = "familiar"


@dataclass(frozen=True)
class Assessment:
    attempt: Attempt
    stuck: Stuck
    misconception: str | None
    valid_alternative: bool
    asks_for_solution: bool
    ambiguous_question: bool
    uncertain: bool

    def __post_init__(self) -> None:
        if not isinstance(self.attempt, Attempt):
            raise TypeError("attempt must be an Attempt")
        if not isinstance(self.stuck, Stuck):
            raise TypeError("stuck must be a Stuck")
        if self.misconception is not None and (
            not isinstance(self.misconception, str) or not self.misconception.strip()
        ):
            raise TypeError("misconception must be None or a non-blank str")
        for name in (
            "valid_alternative",
            "asks_for_solution",
            "ambiguous_question",
            "uncertain",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a bool")


@dataclass(frozen=True)
class History:
    # Partial or full attempts before this message that got a tutor reply.
    helped_attempts: int = 0
    # Consecutive earlier learner messages with attempt NONE or GUESS.
    low_effort_streak: int = 0
    # Consecutive earlier tutor hints or explanations with no other action between.
    help_streak: int = 0

    def __post_init__(self) -> None:
        for name in ("helped_attempts", "low_effort_streak", "help_streak"):
            value = getattr(self, name)
            if type(value) is not int:
                raise TypeError(f"{name} must be an int")
            if value < 0:
                raise ValueError(f"{name} must be at least 0")


@dataclass(frozen=True)
class Decision:
    action: Action
    next_state: State
    reveal: Reveal
