import ast
import dataclasses
import inspect
import itertools
import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.policy import (
    Action,
    Assessment,
    Attempt,
    Checker,
    Decision,
    Difficulty,
    Familiarity,
    History,
    PolicyConfig,
    Reveal,
    State,
    Stuck,
    decide,
    required_attempts,
)

BACKEND_DIR = Path(__file__).resolve().parents[1]
POLICY_DIR = BACKEND_DIR / "app" / "policy"
ALLOWED_STDLIB = {"enum", "dataclasses", "types", "typing", "collections", "__future__"}
FORBIDDEN_CALLS = {"__import__", "importlib", "eval", "exec", "open", "globals", "vars"}
MED, SOME = Difficulty.MEDIUM, Familiarity.SOME
SOLUTION_SHOWN_RESULT = (Action.TRANSFER_PROBLEM, State.TRANSFER, Reveal.NOTHING)


def assess(attempt=Attempt.NONE, stuck=Stuck.NO, misconception=None, uncertain=False,
           asks=False, valid_alt=False, ambiguous=False):
    return Assessment(
        attempt=attempt, stuck=stuck, misconception=misconception,
        valid_alternative=valid_alt, asks_for_solution=asks,
        ambiguous_question=ambiguous, uncertain=uncertain,
    )


def hist(helped=0, low=0, helps=0):
    return History(helped_attempts=helped, low_effort_streak=low, help_streak=helps)


def product(states=tuple(State), lows=(0,), helps=(0,)):
    for s, a, st, m, c, asks, unc, h, lo, hi in itertools.product(
        states, Attempt, Stuck, (None, "x"), Checker, (False, True), (False, True),
        range(4), lows, helps,
    ):
        yield s, assess(a, st, m, unc, asks), c, hist(h, lo, hi)


def run(state, assessment, checker, history, difficulty=MED, familiarity=SOME, config=None):
    if config is None:
        return decide(state, assessment, checker, history, difficulty, familiarity)
    return decide(state, assessment, checker, history, difficulty, familiarity, config)


def triple(d):
    return d.action, d.next_state, d.reveal


def test_policy_package_is_pure():
    files = list(POLICY_DIR.glob("*.py"))
    assert files
    bad = []
    for f in files:
        tree = ast.parse(f.read_text())
        modules = {(a.asname or a.name).split(".")[0] for n in ast.walk(tree)
                   if isinstance(n, ast.Import) for a in n.names}
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr"
                    and node.args and isinstance(node.args[0], ast.Name) and node.args[0].id in modules):
                bad.append((f.name, "getattr on a module"))
            if isinstance(node, ast.Constant) and node.value == "__builtins__":
                bad.append((f.name, "__builtins__ string"))
            if isinstance(node, ast.Name) and node.id == "__builtins__":
                bad.append((f.name, "__builtins__"))
            if isinstance(node, ast.Attribute) and node.attr == "__builtins__":
                bad.append((f.name, "__builtins__"))
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                if node.level > 1:
                    bad.append((f.name, "relative import level > 1"))
                if node.level > 0:
                    continue
                mods = [node.module or ""]
            elif isinstance(node, ast.Call):
                fn = node.func
                name = fn.id if isinstance(fn, ast.Name) else fn.attr if isinstance(fn, ast.Attribute) else ""
                if name in FORBIDDEN_CALLS:
                    bad.append((f.name, name))
                continue
            else:
                continue
            for m in mods:
                root = m.split(".")[0]
                if root not in ALLOWED_STDLIB and m != "app.policy" and not m.startswith("app.policy."):
                    bad.append((f.name, m))
    assert not bad


def test_importing_policy_loads_no_io_modules():
    code = (
        "import sys\n"
        "BLOCK = {'time','socket','urllib','http','datetime','random'}\n"
        "before = set(sys.modules)  # the interpreter may preload time\n"
        "class Block:\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name.split('.')[0] in BLOCK:\n"
        "            raise ImportError('blocked ' + name)\n"
        "sys.meta_path.insert(0, Block())\n"
        "import app.policy\n"
        "bad = [m for m in BLOCK if m in sys.modules and m not in before]\n"
        "sys.exit('loaded: ' + ','.join(bad) if bad else 0)\n"
    )
    env = {**os.environ, "PYTHONPATH": str(BACKEND_DIR)}
    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_decide_signature_has_no_extra_inputs():
    assert list(inspect.signature(required_attempts).parameters) == ["difficulty", "familiarity", "config"]
    params = list(inspect.signature(decide).parameters)
    assert params == ["state", "assessment", "checker", "history", "difficulty", "familiarity", "config"]


def test_input_field_names_are_pinned():
    names = lambda cls: [f.name for f in dataclasses.fields(cls)]
    assert names(Assessment) == [
        "attempt", "stuck", "misconception", "valid_alternative", "asks_for_solution",
        "ambiguous_question", "uncertain",
    ]
    assert names(History) == ["helped_attempts", "low_effort_streak", "help_streak"]
    assert names(Decision) == ["action", "next_state", "reveal"]
    assert names(PolicyConfig) == [
        "base_required_attempts", "min_required_attempts", "difficulty_offset",
        "familiarity_offset", "transfer_helps_before_solution",
    ]


class SubHistory(History):
    pass


class SubAssessment(Assessment):
    pass


class SubConfig(PolicyConfig):
    pass


def test_invalid_inputs_are_rejected():
    ok = (State.ATTEMPTING, assess(), Checker.FAILS, hist())
    with pytest.raises(TypeError):
        run("transfer", *ok[1:])
    with pytest.raises(TypeError):
        run(State.ATTEMPTING, assess(), "passes", hist())
    with pytest.raises(TypeError):
        run(State.ATTEMPTING, assess(), Checker.FAILS, SubHistory())
    with pytest.raises(TypeError):
        run(State.ATTEMPTING, SubAssessment(**dataclasses.asdict(assess())), Checker.FAILS, hist())
    with pytest.raises(TypeError):
        required_attempts("medium", SOME)
    for field in ("helped_attempts", "low_effort_streak", "help_streak"):
        with pytest.raises(ValueError):
            History(**{field: -1})
        with pytest.raises(TypeError):
            History(**{field: True})
    with pytest.raises(ValueError):
        PolicyConfig(min_required_attempts=0)
    with pytest.raises(ValueError):
        PolicyConfig(difficulty_offset={Difficulty.EASY: 1, Difficulty.MEDIUM: 0, Difficulty.HARD: 0})
    with pytest.raises(ValueError):
        PolicyConfig(familiarity_offset={Familiarity.FIRST_TIME: 0, Familiarity.SOME: 0, Familiarity.FAMILIAR: -1})
    with pytest.raises(TypeError):
        PolicyConfig(base_required_attempts=2.0)
    with pytest.raises(TypeError):
        Assessment(attempt="none", stuck=Stuck.NO, misconception=None, valid_alternative=False,
                   asks_for_solution=False, ambiguous_question=False, uncertain=False)
    with pytest.raises(TypeError):
        assess(uncertain=1)
    with pytest.raises(TypeError):
        Assessment(attempt=Attempt.NONE, stuck="yes", misconception=None, valid_alternative=False,
                   asks_for_solution=False, ambiguous_question=False, uncertain=False)
    for bad in ("medium",):
        with pytest.raises(TypeError):
            run(State.ATTEMPTING, assess(), Checker.FAILS, hist(), difficulty=bad)
    with pytest.raises(TypeError):
        run(State.ATTEMPTING, assess(), Checker.FAILS, hist(), familiarity="some")
    with pytest.raises(TypeError):
        run(State.ATTEMPTING, assess(), Checker.FAILS, hist(), config=SubConfig())
    D, F = Difficulty, Familiarity
    with pytest.raises(ValueError):
        PolicyConfig(difficulty_offset={D.EASY: -1, D.MEDIUM: 0})
    with pytest.raises(TypeError):
        PolicyConfig(difficulty_offset={D.EASY: -1, D.MEDIUM: 0.0, D.HARD: 1})
    with pytest.raises(ValueError):
        PolicyConfig(base_required_attempts=1, min_required_attempts=2)
    with pytest.raises(ValueError):
        PolicyConfig(difficulty_offset={D.EASY: 0, D.MEDIUM: 0, D.HARD: 1})
    with pytest.raises(ValueError):
        PolicyConfig(familiarity_offset={F.FIRST_TIME: -1, F.SOME: 0, F.FAMILIAR: 0})


@pytest.mark.parametrize("obj", [
    assess(), History(), Decision(Action.END, State.DONE, Reveal.NOTHING), PolicyConfig(),
])
def test_dataclasses_are_frozen(obj):
    field = dataclasses.fields(obj)[0].name
    with pytest.raises(dataclasses.FrozenInstanceError):
        setattr(obj, field, getattr(obj, field))


def test_solution_shown_always_goes_to_transfer():
    for args in product([State.SOLUTION_SHOWN], lows=(0, 2), helps=(0, 3)):
        assert triple(run(*args)) == SOLUTION_SHOWN_RESULT


def test_done_stays_done():
    for args in product([State.DONE], lows=(0, 2), helps=(0, 3)):
        assert triple(run(*args)) == (Action.END, State.DONE, Reveal.NOTHING)


def test_asks_for_solution_is_ignored():
    for state, a, c, h in product(lows=(0, 1), helps=(0, 3)):
        flipped = dataclasses.replace(a, asks_for_solution=not a.asks_for_solution)
        assert run(state, a, c, h) == run(state, flipped, c, h)


def test_solution_is_gated_and_reveals_match_actions():
    reveal_of = {Action.SOLUTION: Reveal.FULL_SOLUTION, Action.EXPLAIN: Reveal.ERROR_EXPLANATION,
                 Action.HINT: Reveal.HINT}
    seen = set()
    for state, a, c, h in product(lows=(0, 1), helps=(0, 2, 3)):
        for diff, fam in ((Difficulty.EASY, Familiarity.FIRST_TIME), (MED, SOME),
                          (Difficulty.HARD, Familiarity.FAMILIAR)):
            d = run(state, a, c, h, diff, fam)
            assert d.reveal is reveal_of.get(d.action, Reveal.NOTHING)
            if d.action is Action.SOLUTION:
                seen.add(state)
                assert a.stuck is Stuck.YES and not a.uncertain
                assert c is not Checker.PASSES
                if state is State.TRANSFER:
                    assert h.help_streak >= PolicyConfig().transfer_helps_before_solution
                    assert h.low_effort_streak == 0
                else:
                    assert state in (State.ATTEMPTING, State.HELPING)
                    assert h.helped_attempts >= max(1, required_attempts(diff, fam))
                    assert h.low_effort_streak == 0
            if a.uncertain:
                assert d.action not in (Action.SOLUTION, Action.EXPLAIN, Action.CREDIT)
    assert seen == {State.ATTEMPTING, State.HELPING, State.TRANSFER}


def test_config_drives_behavior():
    a, h = assess(Attempt.NONE, Stuck.YES), hist(helped=2)
    assert run(State.ATTEMPTING, a, Checker.FAILS, h).action is Action.SOLUTION
    strict = PolicyConfig(base_required_attempts=5)
    assert run(State.ATTEMPTING, a, Checker.FAILS, h, config=strict).action is not Action.SOLUTION
    t = assess(Attempt.PARTIAL, Stuck.YES)
    assert run(State.TRANSFER, t, Checker.FAILS, hist(helps=3)).action is Action.SOLUTION
    slow = PolicyConfig(transfer_helps_before_solution=4)
    assert run(State.TRANSFER, t, Checker.FAILS, hist(helps=3), config=slow).action is Action.HINT
    diffs = [required_attempts(d_, SOME) for d_ in Difficulty]
    fams = [required_attempts(MED, f) for f in Familiarity]
    assert diffs[0] < diffs[1] < diffs[2]
    assert fams == sorted(fams) and fams[0] < fams[-1]


@pytest.mark.parametrize("state", [State.ATTEMPTING, State.HELPING])
@pytest.mark.parametrize("attempt", [Attempt.PARTIAL, Attempt.FULL])
@pytest.mark.parametrize("valid_alt, helped", [(False, 0), (False, 1), (True, 0)])
def test_stuck_below_threshold_gets_a_hint(state, attempt, valid_alt, helped):
    a = assess(attempt, Stuck.YES, valid_alt=valid_alt)
    d = run(state, a, Checker.FAILS, hist(helped))
    assert triple(d) == (Action.HINT, State.HELPING, Reveal.HINT)


def test_valid_alternative_is_probed_once_then_credited():
    a = assess(Attempt.FULL, valid_alt=True)
    assert run(State.ATTEMPTING, a, Checker.PASSES, hist(0)).action is Action.ASK
    assert run(State.ATTEMPTING, a, Checker.PASSES, hist(1)).action is Action.CREDIT


@pytest.mark.parametrize("state", [State.ATTEMPTING, State.HELPING])
@pytest.mark.parametrize("attempt", [Attempt.NONE, Attempt.GUESS])
@pytest.mark.parametrize("streak, action, reveal", [
    (0, None, Reveal.NOTHING),
    (1, Action.HINT, Reveal.HINT),
    (2, Action.NUDGE, Reveal.NOTHING),
    (3, Action.NUDGE, Reveal.NOTHING),
])
def test_low_effort_ladder(state, attempt, streak, action, reveal):
    for st in (State.ATTEMPTING, State.TRANSFER):
        d = run(st, assess(attempt), Checker.FAILS, hist(low=streak))
        want = action or (Action.INVITE if attempt is Attempt.NONE else Action.ASK)
        assert (d.action, d.reveal) == (want, reveal)
        hint_in_attempting = want is Action.HINT and st is State.ATTEMPTING
        assert d.next_state is (State.HELPING if hint_in_attempting else st)


def test_transfer_rules():
    stuck = assess(Attempt.PARTIAL, Stuck.YES)
    assert triple(run(State.TRANSFER, stuck, Checker.FAILS, hist(helps=3))) == (
        Action.SOLUTION, State.SOLUTION_SHOWN, Reveal.FULL_SOLUTION)
    assert triple(run(State.TRANSFER, stuck, Checker.FAILS, hist(helps=2))) == (
        Action.HINT, State.TRANSFER, Reveal.HINT)
    done = (Action.END, State.DONE, Reveal.NOTHING)
    assert triple(run(State.TRANSFER, assess(Attempt.FULL), Checker.PASSES, hist())) == done
    for a in (assess(Attempt.FULL, uncertain=True), assess(Attempt.FULL, misconception="x")):
        assert run(State.TRANSFER, a, Checker.PASSES, hist()).action is not Action.END
    m = assess(Attempt.FULL, misconception="x")
    assert triple(run(State.TRANSFER, m, Checker.FAILS, hist(0))) == (Action.ASK, State.TRANSFER, Reveal.NOTHING)
    assert triple(run(State.TRANSFER, m, Checker.FAILS, hist(1))) == (
        Action.EXPLAIN, State.TRANSFER, Reveal.ERROR_EXPLANATION)


def test_passing_code_with_misconception_is_never_credited():
    m = assess(Attempt.FULL, misconception="x")
    assert run(State.ATTEMPTING, m, Checker.PASSES, hist(0)).action is Action.ASK
    assert run(State.ATTEMPTING, m, Checker.PASSES, hist(1)).action is Action.EXPLAIN
    for state, a, c, h in product([State.ATTEMPTING, State.HELPING]):
        if a.misconception is not None:
            assert run(state, a, c, h).action is not Action.CREDIT
    d = run(State.ATTEMPTING, assess(Attempt.FULL), Checker.PASSES, hist(0))
    assert (d.action, d.next_state) == (Action.CREDIT, State.TRANSFER)


def test_unverified_code_and_cannot_run():
    a = assess(Attempt.FULL, Stuck.YES)
    d = run(State.ATTEMPTING, a, Checker.NOT_CHECKED, hist(0))
    assert (d.action, d.next_state) == (Action.ASK, State.ATTEMPTING)
    assert run(State.ATTEMPTING, a, Checker.NOT_CHECKED, hist(1)) == run(
        State.ATTEMPTING, a, Checker.FAILS, hist(1))
    for state, a, c, h in product(lows=(0, 1), helps=(0, 3)):
        if c is Checker.FAILS:
            assert run(state, a, Checker.CANNOT_RUN, h) == run(state, a, c, h)


def test_solution_rule_comes_before_misconception_rule():
    a = assess(Attempt.FULL, Stuck.YES, misconception="x")
    assert run(State.HELPING, a, Checker.FAILS, hist(2)).action is Action.SOLUTION


def test_pinned_decisions():
    A_, H_, T_ = State.ATTEMPTING, State.HELPING, State.TRANSFER
    cases = [
        (A_, assess(Attempt.FULL, Stuck.YES, uncertain=True), Checker.PASSES, hist(),
         (Action.ASK, State.ATTEMPTING, Reveal.NOTHING)),
        (H_, assess(Attempt.FULL, misconception="x"), Checker.FAILS, hist(1),
         (Action.EXPLAIN, State.HELPING, Reveal.ERROR_EXPLANATION)),
        (A_, assess(Attempt.FULL, Stuck.YES, valid_alt=True), Checker.CANNOT_RUN, hist(0),
         (Action.HINT, State.HELPING, Reveal.HINT)),
        (T_, assess(Attempt.PARTIAL, Stuck.YES, misconception="x"), Checker.FAILS, hist(1, helps=2),
         (Action.EXPLAIN, State.TRANSFER, Reveal.ERROR_EXPLANATION)),
        (T_, assess(Attempt.PARTIAL, Stuck.YES, misconception="x"), Checker.FAILS, hist(helps=3),
         (Action.SOLUTION, State.SOLUTION_SHOWN, Reveal.FULL_SOLUTION)),
        (A_, assess(Attempt.GUESS, misconception="x"), Checker.FAILS, hist(0, low=0),
         (Action.ASK, State.ATTEMPTING, Reveal.NOTHING)),
        (A_, assess(Attempt.GUESS, misconception="x"), Checker.FAILS, hist(0, low=1),
         (Action.EXPLAIN, State.HELPING, Reveal.ERROR_EXPLANATION)),
    ]
    for state, a, c, h, want in cases:
        assert triple(run(state, a, c, h)) == want
