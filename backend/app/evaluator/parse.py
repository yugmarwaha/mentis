from __future__ import annotations

import json
import re
import unicodedata
from enum import Enum

from app.policy.types import Assessment, Attempt, Stuck

_KEYS = {
    "attempt",
    "stuck",
    "misconception",
    "valid_alternative",
    "asks_for_solution",
    "ambiguous_question",
    "uncertain",
}
_FLAGS = ("valid_alternative", "asks_for_solution", "ambiguous_question", "uncertain")
_FENCE = re.compile(r"```[ \t]*(?:json)?[ \t]*\n?(.*?)\n?```", re.DOTALL | re.IGNORECASE)
_MAX_LABEL_CHARS = 80
_NONE_WORDS = {
    "none",
    "null",
    "n/a",
    "na",
    "nil",
    "nothing",
    "no",
    "none found",
    "no misconception",
    "no misconceptions",
    "no wrong belief",
    "no wrong beliefs",
    "not applicable",
}
_TRAILING = " .,;:!?"


def _normalize(label: str) -> str:
    text = unicodedata.normalize("NFKD", label)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text.casefold().strip().rstrip(_TRAILING).strip()


class ReplyError(ValueError):
    """The model reply is not a valid assessment."""


def _enum(kind: type[Enum], value: object, name: str) -> Enum:
    if isinstance(value, str):
        for member in kind:
            if member.value == value:
                return member
    raise ReplyError(f"{name} has an invalid value")


def _misconception(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ReplyError("misconception must be null or a string")
    label = value.strip()
    if not label:
        raise ReplyError("misconception must not be blank")
    if not label.isprintable():
        raise ReplyError("misconception must be one printable line")
    if len(label) > _MAX_LABEL_CHARS:
        raise ReplyError(f"misconception must be {_MAX_LABEL_CHARS} characters or fewer")
    if not any(c.isalpha() for c in label):
        raise ReplyError("misconception must contain a letter")
    if _normalize(label) in _NONE_WORDS:
        return None
    return label


def _reject_duplicates(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ReplyError("reply has a duplicate key")
        result[key] = value
    return result


def _reject_constant(name: str) -> object:
    raise ReplyError(f"reply has the constant {name}")


def parse_reply(text: str) -> Assessment:
    if type(text) is not str:
        raise ReplyError("reply must be a str")
    text = text.strip()
    fence = _FENCE.fullmatch(text)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(
            text, object_pairs_hook=_reject_duplicates, parse_constant=_reject_constant
        )
    except ReplyError:
        raise
    except Exception as error:  # includes RecursionError
        raise ReplyError("reply is not valid JSON") from error
    if not isinstance(data, dict) or set(data) != _KEYS:
        raise ReplyError("reply must be an object with exactly the form fields")
    for name in _FLAGS:
        if not isinstance(data[name], bool):
            raise ReplyError(f"{name} must be true or false")
    attempt = _enum(Attempt, data["attempt"], "attempt")
    if data["valid_alternative"] and attempt in (Attempt.NONE, Attempt.GUESS):
        raise ReplyError("valid_alternative needs attempt partial or full")
    try:
        return Assessment(
            attempt=attempt,
            stuck=_enum(Stuck, data["stuck"], "stuck"),
            misconception=_misconception(data["misconception"]),
            **{name: data[name] for name in _FLAGS},
        )
    except ReplyError:
        raise
    except (TypeError, ValueError) as error:
        raise ReplyError(str(error)) from error
