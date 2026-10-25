from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from app.policy.types import Assessment, Attempt, Stuck


MAX_TEXT_CHARS = 5000


def is_blank(text: str) -> bool:
    """True when no character is both printable and not whitespace."""
    return not any(c.isprintable() and not c.isspace() for c in text)


def check_text(text: object, name: str) -> None:
    if type(text) is not str:
        raise TypeError(f"{name} must be a str")
    if is_blank(text):
        raise ValueError(f"{name} must not be blank")
    if any(unicodedata.category(c) == "Cc" and c not in "\n\r\t" for c in text):
        raise ValueError(f"{name} must not contain control characters")
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError(f"{name} must be {MAX_TEXT_CHARS} characters or fewer")


class Speaker(Enum):
    LEARNER = "learner"
    TUTOR = "tutor"


@dataclass(frozen=True)
class Turn:
    speaker: Speaker
    text: str

    def __post_init__(self) -> None:
        if not isinstance(self.speaker, Speaker):
            raise TypeError("speaker must be a Speaker")
        check_text(self.text, "text")


@dataclass(frozen=True)
class Problem:
    statement: str
    expected_approach: str | None = None

    def __post_init__(self) -> None:
        check_text(self.statement, "statement")
        if self.expected_approach is not None:
            check_text(self.expected_approach, "expected_approach")


class ModelSetupError(Exception):
    """A setup mistake: wrong key, no permission, unknown model, or bad request.

    A retry cannot fix it.
    """


class ModelRefusal(Exception):
    """The model refused to answer. A retry will likely refuse again."""


class Model(Protocol):
    def complete(self, prompt: str) -> str:
        """Return text that should be a JSON object."""
        ...


# The form when the evaluator cannot get a valid reply. When `is_fallback(assessment)`
# is true the caller does not call the policy, shows a fixed message, and changes
# no counts or state.
FALLBACK = Assessment(
    attempt=Attempt.NONE,
    stuck=Stuck.UNCLEAR,
    misconception=None,
    valid_alternative=False,
    asks_for_solution=False,
    ambiguous_question=False,
    uncertain=True,
)


def is_fallback(assessment: Assessment) -> bool:
    """True when the assessment equals the fallback form."""
    return assessment == FALLBACK
