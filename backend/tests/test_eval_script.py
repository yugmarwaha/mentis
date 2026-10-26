"""Guards for the scenario eval (evals/run_scenarios.py) and its label file. No network, no real key."""
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from app.evaluator import ModelSetupError
from app.policy import Attempt, Stuck

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BACKEND_DIR.parent
LABELS = REPO_DIR / "evals" / "scenario_labels.json"
SCENARIOS = REPO_DIR / "docs" / "scenarios.md"
RUN_SCRIPT = REPO_DIR / "evals" / "run_scenarios.py"
FAKE_KEY = "test-key-value-77f3c1-not-a-real-key"
KEY_VARS = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
EXPECTED_KEYS = (
    "attempt", "stuck", "misconception_present", "valid_alternative", "asks_for_solution", "ambiguous_question",
)
# Pinned labels: id -> (attempt, stuck, misconception_present, valid_alternative, asks_for_solution,
# ambiguous_question). s4-m2 is partial; misconception_present is false on purpose (see evals/CLAUDE.md).
PINNED = {
    "s1-m1": ("full", "no", False, True, False, False),
    "s1-m2": ("partial", "no", False, False, False, False),
    "s2-m1": ("none", "yes", False, False, False, False),
    "s2-m2": ("partial", "no", False, False, False, False),
    "s2-m3": ("partial", "yes", False, False, False, False),
    "s3-m1": ("full", "no", True, False, False, False),
    "s3-m2": ("partial", "no", True, False, False, False),
    "s4-m1": ("none", "unclear", False, False, True, False),
    "s4-m2": ("partial", "no", False, False, False, False),
    "s4-m3": ("partial", "no", True, False, False, False),
    "s4-m4": ("none", "yes", False, False, False, False),
    "s4-m5": ("none", "unclear", False, False, False, False),
    "s5-m1": ("none", "unclear", False, False, False, True),
    "s5-m2": ("none", "unclear", False, False, False, False),
}


def cases():
    return json.loads(LABELS.read_text())


# ---- the label file --------------------------------------------------------

def test_labels_match_the_pinned_table():
    got = {c["id"]: tuple(c["expected"][k] for k in EXPECTED_KEYS) for c in cases()}
    assert got == PINNED


def plain(text):
    return text.replace("`", "").strip()


def test_scenario_labels_are_valid():
    cs = cases()
    ids = [c["id"] for c in cs]
    assert len(set(ids)) == len(ids)
    for c in cs:
        assert set(c) == {"id", "problem", "expected_approach", "turns", "message", "expected"}, c.get("id")
        assert isinstance(c["problem"], str) and c["problem"].strip()
        assert c["expected_approach"] is None or (isinstance(c["expected_approach"], str)
                                                  and c["expected_approach"].strip())
        if c["id"].startswith("s5-"):
            assert c["expected_approach"] is None
        assert isinstance(c["message"], str) and c["message"].strip()
        for t in c["turns"]:
            assert set(t) == {"speaker", "text"} and t["speaker"] in ("learner", "tutor") and t["text"].strip()
            assert not re.match(r"^\s*\[", t["text"]), "tutor lines carry no [tag]"
        e = c["expected"]
        assert set(e) == set(EXPECTED_KEYS), c["id"]
        assert e["attempt"] in {a.value for a in Attempt} and e["stuck"] in {s.value for s in Stuck}
        if e["valid_alternative"]:
            assert e["attempt"] in ("partial", "full"), c["id"]
    prefix = "> **Learner:**"
    learner = [plain(x[len(prefix):]) for x in SCENARIOS.read_text().splitlines() if x.startswith(prefix)]
    covered = {plain(c["message"]) for c in cs} | {
        plain(t["text"]) for c in cs for t in c["turns"] if t["speaker"] == "learner"}
    assert not [line for line in learner if line not in covered]


# ---- the script ------------------------------------------------------------

@pytest.fixture
def script(monkeypatch):
    """Import evals/run_scenarios.py by path, as a module. The key is a fake value."""
    spec = importlib.util.spec_from_file_location("run_scenarios_under_test", RUN_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, mod)
    monkeypatch.syspath_prepend(str(BACKEND_DIR))
    spec.loader.exec_module(mod)
    for name in KEY_VARS:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    return mod


def label_reply(case):
    e = case["expected"]
    return json.dumps({
        "attempt": e["attempt"], "stuck": e["stuck"],
        "misconception": "off by one" if e["misconception_present"] else None,
        "valid_alternative": e["valid_alternative"], "asks_for_solution": e["asks_for_solution"],
        "ambiguous_question": e["ambiguous_question"], "uncertain": False,
    })


class FakeModel:
    """Stands in for HaikuModel. It finds the case from the latest-message line and answers with its labels."""

    def __init__(self, fail_ids=(), all_fail=False, setup_error=False):
        self.fail_ids, self.all_fail, self.setup_error = set(fail_ids), all_fail, setup_error
        self.by_line = {"latest_learner_message: " + json.dumps(c["message"], ensure_ascii=False): c
                        for c in cases()}
        self.calls, self.made = [], []

    def __call__(self, *args, **kwargs):  # used as the HaikuModel class
        self.made.append((args, kwargs))
        return self

    def complete(self, prompt):
        found = [c for line, c in self.by_line.items() if line in prompt.splitlines()]
        assert len(found) == 1
        self.calls.append(found[0]["id"])
        if self.setup_error:
            raise ModelSetupError("AuthenticationError")
        if self.all_fail or found[0]["id"] in self.fail_ids:
            return "not json"
        return label_reply(found[0])


def run(script, monkeypatch, capsys, fake, argv=()):
    monkeypatch.setattr(script, "HaikuModel", fake)
    code = script.main(list(argv))
    out = capsys.readouterr()
    text = out.out + out.err
    assert FAKE_KEY not in text
    return code, text


def test_all_valid_replies_exit_0_with_one_call_per_case(script, monkeypatch, capsys):
    fake = FakeModel()
    code, text = run(script, monkeypatch, capsys, fake)
    assert code == 0, text
    assert sorted(fake.calls) == sorted(PINNED)
    n = len(PINNED)
    assert re.search(rf"fallback\s*:?\s*0/{n}", text), text


def test_fallback_cases_are_left_out_of_the_scores(script, monkeypatch, capsys):
    fake = FakeModel(fail_ids={"s1-m1", "s4-m1"})
    code, text = run(script, monkeypatch, capsys, fake)
    assert code == 0, text
    n = len(PINNED)
    lines = text.splitlines()
    fb = [i for i, line in enumerate(lines) if re.search(rf"fallback\s*:?\s*2/{n}", line)]
    scores = [i for i, line in enumerate(lines)
              if any(k in line for k in EXPECTED_KEYS) and re.search(r"\d+/\d+", line)]
    assert fb and scores, text
    assert fb[0] < scores[0], "the fallback count comes first"
    for i in scores:
        assert all(int(b) == n - 2 for _, b in re.findall(r"(\d+)/(\d+)", lines[i])), lines[i]
    assert fake.calls.count("s1-m1") == 2 and fake.calls.count("s2-m1") == 1


def test_all_fallback_returns_3(script, monkeypatch, capsys):
    code, text = run(script, monkeypatch, capsys, FakeModel(all_fail=True))
    assert code == 3 and "All calls failed." in text


def test_setup_error_returns_4_after_the_first_call(script, monkeypatch, capsys):
    fake = FakeModel(setup_error=True)
    code, text = run(script, monkeypatch, capsys, fake)
    assert code == 4 and len(fake.calls) == 1
    assert "Setup error:" in text and "Check the key and the model ID." in text


def test_setup_error_message_has_the_safe_name_only(script, monkeypatch, capsys):
    code, text = run(script, monkeypatch, capsys, FakeModel(setup_error=True))
    assert code == 4 and "Setup error: AuthenticationError. Check the key and the model ID." in text


@pytest.mark.parametrize("exc", [ValueError, TypeError])
def test_bad_option_while_building_the_model_returns_2(script, monkeypatch, capsys, exc):
    def boom(*args, **kwargs):
        raise exc("secret-detail")

    code, text = run(script, monkeypatch, capsys, boom)
    assert code == 2 and f"Bad option: {exc.__name__}." in text and "secret-detail" not in text


def test_blank_model_id_is_a_bad_option(script, monkeypatch, capsys):
    monkeypatch.setattr(script, "HaikuModel", __import__("app.llm.haiku", fromlist=["HaikuModel"]).HaikuModel)
    monkeypatch.setattr("anthropic.Anthropic", lambda **kw: object())
    assert script.main(["--model-id", " "]) == 2
    assert "Bad option: ValueError." in capsys.readouterr().out


def test_no_key_returns_2(script, monkeypatch, capsys):
    for name in KEY_VARS:
        monkeypatch.delenv(name, raising=False)
    fake = FakeModel()
    code, _ = run(script, monkeypatch, capsys, fake)
    assert code == 2 and fake.calls == []


@pytest.mark.parametrize("argv", [["--effort", "bad"], ["--effort", "LOW"], ["--max-tokens", "0"],
                                  ["--max-tokens", "-5"]])
def test_bad_arguments_are_argparse_errors(script, monkeypatch, capsys, argv):
    fake = FakeModel()
    monkeypatch.setattr(script, "HaikuModel", fake)
    with pytest.raises(SystemExit) as caught:
        script.main(argv)
    assert caught.value.code == 2 and fake.calls == []


def test_script_run_as_a_program_exits_2_without_a_key():
    env = {k: v for k, v in os.environ.items() if k not in KEY_VARS}
    env["PYTHONPATH"] = str(BACKEND_DIR)
    r = subprocess.run([sys.executable, str(RUN_SCRIPT), "--env-file", os.devnull], cwd=BACKEND_DIR,
                       env=env, capture_output=True, text=True, timeout=60)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "ANTHROPIC_API_KEY" in r.stdout + r.stderr


# ---- the .env file ---------------------------------------------------------

def test_env_file_sets_the_key_and_prints_nothing(script, monkeypatch, capsys, tmp_path):
    for name in KEY_VARS:
        monkeypatch.delenv(name, raising=False)
    env = tmp_path / ".env"
    env.write_text('# comment\n\nexport OTHER_VAR_FOR_TEST="quoted value"\n'
                   f"ANTHROPIC_API_KEY={FAKE_KEY}\nBAD LINE\n=novalue\n")
    monkeypatch.delenv("OTHER_VAR_FOR_TEST", raising=False)
    script.load_env_file(env)
    assert os.environ["ANTHROPIC_API_KEY"] == FAKE_KEY
    assert os.environ["OTHER_VAR_FOR_TEST"] == "quoted value"
    monkeypatch.delenv("OTHER_VAR_FOR_TEST", raising=False)
    out = capsys.readouterr()
    assert out.out == "" and out.err == ""


def test_a_variable_already_set_wins_over_the_file(script, monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    env = tmp_path / ".env"
    env.write_text("ANTHROPIC_API_KEY=from-the-file\n")
    script.load_env_file(env)
    assert os.environ["ANTHROPIC_API_KEY"] == FAKE_KEY


def test_an_empty_value_and_a_missing_file_set_nothing(script, monkeypatch, tmp_path):
    for name in KEY_VARS:
        monkeypatch.delenv(name, raising=False)
    env = tmp_path / ".env"
    env.write_text("ANTHROPIC_API_KEY=\n")
    script.load_env_file(env)
    script.load_env_file(tmp_path / "does-not-exist")
    assert "ANTHROPIC_API_KEY" not in os.environ


def test_main_loads_the_env_file_option_before_the_key_check(script, monkeypatch, capsys, tmp_path):
    for name in KEY_VARS:
        monkeypatch.delenv(name, raising=False)
    env = tmp_path / ".env"
    env.write_text(f"ANTHROPIC_API_KEY={FAKE_KEY}\n")
    fake = FakeModel()
    monkeypatch.setattr(script, "HaikuModel", fake)
    code = script.main(["--env-file", str(env)])
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert code == 0 and fake.calls
    assert FAKE_KEY not in capsys.readouterr().out


def test_main_without_an_env_file_reads_no_file(script, monkeypatch, capsys):
    for name in KEY_VARS:
        monkeypatch.delenv(name, raising=False)
    fake = FakeModel()
    monkeypatch.setattr(script, "HaikuModel", fake)
    assert script.main([]) == 2 and fake.calls == []


def test_env_example_is_tracked_and_has_no_key():
    text = (RUN_SCRIPT.parents[1] / ".env.example").read_text()
    assert "ANTHROPIC_API_KEY=" in text
    assert not re.search(r"ANTHROPIC_API_KEY=\S", text)
