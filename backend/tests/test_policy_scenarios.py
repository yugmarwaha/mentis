import pytest

from app.policy import (
    Action, Assessment, Attempt, Checker, Difficulty, Familiarity, History, State, Stuck, decide,
)

A, H = State.ATTEMPTING, State.HELPING


def case(attempt, stuck, helped, misconception=None, asks=False, ambiguous=False,
         valid_alt=False, checker=Checker.FAILS, low=0):
    a = Assessment(attempt=attempt, stuck=stuck, misconception=misconception,
                   valid_alternative=valid_alt, asks_for_solution=asks,
                   ambiguous_question=ambiguous, uncertain=False)
    return a, checker, helped, low


SCENARIOS = [
    ("s1", case(Attempt.FULL, Stuck.NO, 0, valid_alt=True, checker=Checker.PASSES), Action.ASK, None),
    ("s2a", case(Attempt.NONE, Stuck.YES, 0), Action.INVITE, None),
    ("s2b", case(Attempt.PARTIAL, Stuck.NO, 0, low=1), Action.ASK, None),
    ("s2c", case(Attempt.PARTIAL, Stuck.YES, 1), Action.HINT, None),
    ("s3a", case(Attempt.FULL, Stuck.NO, 0, misconception="range starts at 1"), Action.ASK, None),
    ("s3b", case(Attempt.FULL, Stuck.NO, 1, misconception="range starts at 1"), Action.EXPLAIN, None),
    ("s4d", case(Attempt.NONE, Stuck.YES, 2, asks=True), Action.SOLUTION, State.SOLUTION_SHOWN),
    ("s5", case(Attempt.NONE, Stuck.NO, 0, ambiguous=True), Action.ASK, None),
    ("s5b", case(Attempt.NONE, Stuck.NO, 0), Action.INVITE, None),
]


@pytest.mark.parametrize("name,inp,action,next_state", SCENARIOS, ids=[s[0] for s in SCENARIOS])
def test_scenarios(name, inp, action, next_state):
    a, checker, helped, low = inp
    d = decide(A, a, checker, History(helped_attempts=helped, low_effort_streak=low), Difficulty.MEDIUM, Familiarity.SOME)
    assert d.action is action
    if next_state:
        assert d.next_state is next_state

