from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from .types import Difficulty, Familiarity

# Every default below is a placeholder, untested.


def _difficulty_offset() -> Mapping[Difficulty, int]:
    return MappingProxyType(
        {Difficulty.EASY: -1, Difficulty.MEDIUM: 0, Difficulty.HARD: 1}
    )


def _familiarity_offset() -> Mapping[Familiarity, int]:
    return MappingProxyType(
        {Familiarity.FIRST_TIME: -1, Familiarity.SOME: 0, Familiarity.FAMILIAR: 1}
    )


@dataclass(frozen=True)
class PolicyConfig:
    base_required_attempts: int = 2  # placeholder, untested
    min_required_attempts: int = 1  # placeholder, untested
    difficulty_offset: Mapping[Difficulty, int] = field(
        default_factory=_difficulty_offset
    )  # placeholder, untested
    familiarity_offset: Mapping[Familiarity, int] = field(
        default_factory=_familiarity_offset
    )  # placeholder, untested
    transfer_helps_before_solution: int = 3  # placeholder, untested

    def __post_init__(self) -> None:
        counts = (
            "base_required_attempts",
            "min_required_attempts",
            "transfer_helps_before_solution",
        )
        for name in counts:
            if type(getattr(self, name)) is not int:
                raise TypeError(f"{name} must be an int")
        for name in counts:
            if getattr(self, name) < 1:
                raise ValueError(f"{name} must be at least 1")
        if self.base_required_attempts < self.min_required_attempts:
            raise ValueError(
                "base_required_attempts must be at least min_required_attempts"
            )
        for name, keys in (
            ("difficulty_offset", Difficulty),
            ("familiarity_offset", Familiarity),
        ):
            offsets = getattr(self, name)
            if not isinstance(offsets, Mapping):
                raise TypeError(f"{name} must be a mapping")
            if set(offsets) != set(keys):
                raise ValueError(f"{name} must have one value for every {keys.__name__}")
            if any(type(v) is not int for v in offsets.values()):
                raise TypeError(f"{name} values must be ints")
            ordered = [offsets[k] for k in keys]
            if any(x >= y for x, y in zip(ordered, ordered[1:])):
                raise ValueError(f"{name} must increase with {keys.__name__} order")
            object.__setattr__(self, name, MappingProxyType(dict(offsets)))


DEFAULT_CONFIG = PolicyConfig()
