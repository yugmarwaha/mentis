import ast
import dataclasses
import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import anthropic
import pytest

import app.llm
from app.evaluator import FALLBACK, ModelRefusal, ModelSetupError, Problem, build_prompt, evaluate, is_fallback
from app.evaluator.prompt import NOTE_CALL_FAILED
from app.llm import haiku as haiku_mod
from app.llm.haiku import (
    EFFORT, MAX_TOKENS, MODEL_ID, SDK_MAX_RETRIES, TIMEOUT_SECONDS, HaikuModel, ModelCallError,
)
from app.llm.schema import ASSESSMENT_SCHEMA
from app.policy import Assessment, Attempt, Stuck

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BACKEND_DIR.parent
LLM_DIR = BACKEND_DIR / "app" / "llm"
KEY_PREFIX = "sk-" + "ant-"  # split so that this file does not match its own scan
FAKE_KEY = "test-key-value-77f3c1-not-a-real-key"

PROBLEM = Problem("Write a function that returns the sum of a list of integers.")
MESSAGE = "I think I loop over the list and add each item to a total."
GOOD = {
    "attempt": "partial", "stuck": "no", "misconception": None, "valid_alternative": False,
    "asks_for_solution": False, "ambiguous_question": False, "uncertain": False,
}
GOOD_ASSESSMENT = Assessment(Attempt.PARTIAL, Stuck.NO, None, False, False, False, False)
FIELDS = [f.name for f in dataclasses.fields(Assessment)]
BOOL_FIELDS = ("valid_alternative", "asks_for_solution", "ambiguous_question", "uncertain")
FORBIDDEN_SCHEMA_KEYS = {"minLength", "maxLength", "minimum", "maximum", "pattern", "multipleOf"}
SETUP_ERRORS = ("AuthenticationError", "PermissionDeniedError", "NotFoundError", "BadRequestError")
PASS_ERRORS = ("RateLimitError", "APIConnectionError", "APITimeoutError", "InternalServerError")


def sdk_error(name, message="secret-detail-9a2b"):
    """Build an SDK error without __init__: its request/response arguments differ between SDK versions."""
    cls = getattr(anthropic, name)
    err = cls.__new__(cls)
    err.args = (message,)
    return err


def text_block(text):
    return SimpleNamespace(type="text", text=text)


def response(*blocks, stop_reason="end_turn"):
    return SimpleNamespace(stop_reason=stop_reason, content=list(blocks))


GOOD_RESPONSE = response(text_block(json.dumps(GOOD)))


class FakeClient:
    """A stand-in for anthropic.Anthropic. Each create() call records its kwargs and returns or raises the next item."""

    def __init__(self, items):
        self.items, self.calls = list(items), []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, *args, **kwargs):
        assert not args, "create() must use keyword arguments only"
        self.calls.append(kwargs)
        item = self.items.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


def sent_output_config(kwargs):
    """Return (kwargs without output_config, output_config). Accept extra_body if the SDK lacks the keyword."""
    kwargs = dict(kwargs)
    if "output_config" in kwargs:
        return kwargs, kwargs.pop("output_config")
    extra = dict(kwargs.pop("extra_body"))
    config = extra.pop("output_config")
    assert not extra, extra
    return kwargs, config


# ---- the API call ----------------------------------------------------------

def test_constants_are_pinned():
    assert (MODEL_ID, MAX_TOKENS, EFFORT) == ("claude-haiku-5-5", 2048, "low")
    assert (TIMEOUT_SECONDS, SDK_MAX_RETRIES) == (30.0, 0)
    assert issubclass(ModelCallError, Exception)  # the evaluator treats it as a failed call
    assert {"HaikuModel", "ModelCallError", "ASSESSMENT_SCHEMA"} <= set(dir(app.llm))


@pytest.mark.parametrize("init, want", [
    ({}, (MODEL_ID, MAX_TOKENS, EFFORT)),
    ({"model": "claude-other-1", "max_tokens": 1, "effort": "max"}, ("claude-other-1", 1, "max")),
])
def test_create_gets_exactly_the_approved_kwargs(init, want):
    client = FakeClient([GOOD_RESPONSE])
    prompt = "line one\nline two"
    assert HaikuModel(client, **init).complete(prompt) == json.dumps(GOOD)
    assert len(client.calls) == 1
    rest, config = sent_output_config(client.calls[0])
    # Exact equality also proves: no temperature, top_p, top_k, thinking, system, or assistant prefill.
    assert rest == {"model": want[0], "max_tokens": want[1], "messages": [{"role": "user", "content": prompt}]}
    assert config == {"effort": want[2], "format": {"type": "json_schema", "schema": ASSESSMENT_SCHEMA}}
    assert rest["messages"][0]["content"] is prompt


def test_first_text_block_after_a_thinking_block_is_the_reply():
    thinking = SimpleNamespace(type="thinking", thinking="hmm", text="decoy from a thinking block")
    client = FakeClient([response(thinking, text_block("first"), text_block("second"))])
    assert HaikuModel(client).complete("p") == "first"


@pytest.mark.parametrize("stop", [
    "max_tokens", "model_context_window_exceeded", "tool_use", "pause_turn", "stop_sequence", None])
def test_only_end_turn_returns_text(stop):
    with pytest.raises(ModelCallError, match=re.escape(str(stop))):
        HaikuModel(FakeClient([response(text_block(json.dumps(GOOD)), stop_reason=stop)])).complete("p")


def test_refusal_raises_model_refusal():
    client = FakeClient([response(text_block(json.dumps(GOOD)), stop_reason="refusal"), GOOD_RESPONSE])
    with pytest.raises(ModelRefusal):
        HaikuModel(client).complete("p")
    assert len(client.calls) == 1


@pytest.mark.parametrize("resp, match", [
    (response(), None),
    (response(SimpleNamespace(type="thinking", thinking="only thinking", text="decoy")), None),
    (response(SimpleNamespace(type="tool_use", text="decoy")), None),
])
def test_bad_responses_raise_model_call_error(resp, match):
    with pytest.raises(ModelCallError, match=match):
        HaikuModel(FakeClient([resp])).complete("p")


def test_non_str_text_is_not_returned():
    with pytest.raises((ModelCallError, TypeError)):
        HaikuModel(FakeClient([response(text_block(None))])).complete("p")


@pytest.mark.parametrize("name", SETUP_ERRORS)
def test_setup_sdk_errors_become_model_setup_error(name):
    err = sdk_error(name)
    client = FakeClient([err, GOOD_RESPONSE])
    with pytest.raises(ModelSetupError) as caught:
        HaikuModel(client).complete("p")
    assert str(caught.value) == name  # the class name only, never the SDK message
    assert caught.value.__cause__ is err
    assert len(client.calls) == 1


SDK_MISSING_CREDENTIALS = (
    '"Could not resolve authentication method. Expected one of api_key, auth_token, or credentials '
    'to be set. Or for one of the `X-Api-Key` or `Authorization` headers to be explicitly omitted"'
)


def test_missing_credentials_type_error_becomes_model_setup_error():
    err = TypeError(SDK_MISSING_CREDENTIALS)
    client = FakeClient([err, GOOD_RESPONSE])
    with pytest.raises(ModelSetupError) as caught:
        HaikuModel(client).complete("p")
    assert str(caught.value) == "MissingCredentials"
    assert caught.value.__cause__ is err
    assert len(client.calls) == 1


@pytest.mark.parametrize("message", ["unsupported operand", "", "Pass at most one of `credentials=`, `config=`, or `profile=`."])
def test_other_type_errors_propagate_unchanged(message):
    err = TypeError(message)
    with pytest.raises(TypeError) as caught:
        HaikuModel(FakeClient([err])).complete("p")
    assert caught.value is err


def test_other_sdk_exceptions_propagate_unchanged():
    errors = [*(sdk_error(n) for n in PASS_ERRORS), RuntimeError("rate limited"), KeyboardInterrupt()]
    for err in errors:
        client = FakeClient([err, GOOD_RESPONSE])
        with pytest.raises(type(err)) as caught:
            HaikuModel(client).complete("p")
        assert caught.value is err
        assert len(client.calls) == 1  # the client does not retry


@pytest.mark.parametrize("prompt, exc", [
    (None, TypeError), (3, TypeError), (b"bytes", TypeError), (["p"], TypeError),
    ("", ValueError), ("   \n\t", ValueError),
])
def test_bad_prompt_is_rejected_before_the_call(prompt, exc):
    client = FakeClient([GOOD_RESPONSE])
    with pytest.raises(exc):
        HaikuModel(client).complete(prompt)
    assert client.calls == []


@pytest.mark.parametrize("kw, exc", [
    ({"model": ""}, ValueError), ({"model": "  "}, ValueError), ({"model": None}, TypeError),
    ({"model": 3}, TypeError),
    ({"max_tokens": 0}, ValueError), ({"max_tokens": -1}, ValueError), ({"max_tokens": True}, TypeError),
    ({"max_tokens": 2.0}, TypeError), ({"max_tokens": "2048"}, TypeError),
    ({"effort": "none"}, (TypeError, ValueError)), ({"effort": "LOW"}, (TypeError, ValueError)),
    ({"effort": ""}, (TypeError, ValueError)), ({"effort": None}, (TypeError, ValueError)),
])
def test_constructor_validates(kw, exc):
    with pytest.raises(exc):
        HaikuModel(FakeClient([]), **kw)


@pytest.mark.parametrize("effort", ["low", "medium", "high", "xhigh", "max"])
def test_constructor_accepts_each_effort(effort):
    HaikuModel(FakeClient([]), effort=effort)


def test_default_client_is_made_by_the_sdk_and_the_key_is_not_read(monkeypatch):
    made = []

    class StubAnthropic:
        def __init__(self, *args, **kwargs):
            made.append((args, kwargs))
            self.messages = FakeClient([GOOD_RESPONSE]).messages

    monkeypatch.setenv("ANTHROPIC_API_KEY", FAKE_KEY)
    monkeypatch.setattr(haiku_mod.anthropic, "Anthropic", StubAnthropic)
    model = HaikuModel()
    assert made == [((), {"timeout": 30.0, "max_retries": 0})]  # the SDK reads ANTHROPIC_API_KEY itself
    assert model.complete("p") == json.dumps(GOOD)
    for text in (repr(model), str(model), repr(getattr(model, "__dict__", {}))):
        assert FAKE_KEY not in text


def test_haiku_module_does_not_touch_env_or_print():
    tree = ast.parse((LLM_DIR / "haiku.py").read_text())
    bad = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            bad += [a.name for a in node.names if a.name.split(".")[0] in {"os", "sys", "logging", "dotenv"}]
        elif isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] in {
                "os", "sys", "logging", "dotenv"}:
            bad.append(node.module)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "print":
            bad.append("print")
        elif isinstance(node, (ast.Name, ast.Attribute)) and getattr(node, "id", getattr(node, "attr", "")) in {
                "environ", "getenv"}:
            bad.append("environ")
        elif isinstance(node, ast.Constant) and node.value == "ANTHROPIC_API_KEY":
            bad.append("ANTHROPIC_API_KEY")
    assert not bad


def test_complete_writes_nothing(capfd, caplog):
    caplog.set_level(logging.DEBUG)
    assert HaikuModel(FakeClient([GOOD_RESPONSE])).complete("p") == json.dumps(GOOD)
    out, err = capfd.readouterr()
    assert (out, err) == ("", "") and not caplog.records


# ---- the schema ------------------------------------------------------------

def walk(node, path="$"):
    yield path, node
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, f"{path}[{i}]")


def test_schema_matches_the_assessment():
    s = ASSESSMENT_SCHEMA
    json.dumps(s)  # plain JSON data only
    assert s["type"] == "object" and s["additionalProperties"] is False
    assert set(s["properties"]) == set(FIELDS)
    assert sorted(s["required"]) == sorted(FIELDS) and len(s["required"]) == 7
    p = s["properties"]
    assert p["attempt"]["type"] == "string" and sorted(p["attempt"]["enum"]) == sorted(a.value for a in Attempt)
    assert p["stuck"]["type"] == "string" and sorted(p["stuck"]["enum"]) == sorted(x.value for x in Stuck)
    assert sorted(json.dumps(b, sort_keys=True) for b in p["misconception"]["anyOf"]) == sorted(
        json.dumps(b, sort_keys=True) for b in ({"type": "string"}, {"type": "null"}))
    for name in BOOL_FIELDS:
        assert p[name]["type"] == "boolean", name


def test_schema_uses_only_supported_keywords():
    found = []
    for path, node in walk(ASSESSMENT_SCHEMA):
        if isinstance(node, dict):
            found += [f"{path}.{k}" for k in node if k in FORBIDDEN_SCHEMA_KEYS or k == "$ref"]
            if "additionalProperties" in node and node["additionalProperties"] is not False:
                found.append(f"{path}.additionalProperties")
    assert not found


# ---- through the evaluator -------------------------------------------------

def test_evaluate_with_haiku_model_returns_the_assessment():
    client = FakeClient([GOOD_RESPONSE])
    assert evaluate(PROBLEM, [], MESSAGE, HaikuModel(client)) == GOOD_ASSESSMENT
    assert client.calls[0]["messages"][0]["content"] == build_prompt(PROBLEM, [], MESSAGE)


def test_two_failed_calls_give_fallback():
    client = FakeClient([RuntimeError("down"), response(stop_reason="max_tokens"), GOOD_RESPONSE])
    got = evaluate(PROBLEM, [], MESSAGE, HaikuModel(client))
    assert got == FALLBACK and is_fallback(got) and len(client.calls) == 2


def test_refusal_gives_fallback_after_one_call():
    kinds = []
    client = FakeClient([response(text_block(json.dumps(GOOD)), stop_reason="refusal"), GOOD_RESPONSE])
    got = evaluate(PROBLEM, [], MESSAGE, HaikuModel(client), on_failure=lambda *a: kinds.append(a))
    assert got == FALLBACK and len(client.calls) == 1
    assert kinds == [("refusal", "ModelRefusal"), ("fallback", "")]


def test_auth_error_raises_model_setup_error():
    client = FakeClient([sdk_error("AuthenticationError"), GOOD_RESPONSE])
    with pytest.raises(ModelSetupError):
        evaluate(PROBLEM, [], MESSAGE, HaikuModel(client))
    assert len(client.calls) == 1


def test_rate_limit_then_valid_reply_succeeds_on_the_retry():
    client = FakeClient([sdk_error("RateLimitError"), GOOD_RESPONSE])
    assert evaluate(PROBLEM, [], MESSAGE, HaikuModel(client)) == GOOD_ASSESSMENT
    assert [c["messages"][0]["content"] for c in client.calls] == [
        build_prompt(PROBLEM, [], MESSAGE), build_prompt(PROBLEM, [], MESSAGE, note=NOTE_CALL_FAILED)]


def test_evaluator_and_policy_do_not_load_the_sdk():
    code = (
        "import sys\n"
        "import app.evaluator, app.evaluator.fake, app.policy\n"
        "bad = [m for m in sys.modules if m.split('.')[0] == 'anthropic' or m.startswith('app.llm')]\n"
        "sys.exit('loaded: ' + ','.join(bad) if bad else 0)\n"
    )
    env = {**os.environ, "PYTHONPATH": str(BACKEND_DIR)}
    r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


# ---- repository and evals --------------------------------------------------

def test_no_api_key_in_the_repository():
    r = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                       cwd=REPO_DIR, capture_output=True, check=True)
    hits = []
    for name in filter(None, r.stdout.decode().split("\0")):
        path = REPO_DIR / name
        if not path.is_file():
            continue
        data = path.read_bytes()
        if b"\0" in data:
            continue  # binary file
        if KEY_PREFIX.encode() in data:
            hits.append(name)
    assert not hits
