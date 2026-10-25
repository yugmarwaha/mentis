"""Label the scenario messages with the Haiku client and compare with the expected labels.

Usage: cd backend && uv run python ../evals/run_scenarios.py [--model-id ID] [--effort LEVEL]
       [--max-tokens N]
Costs a little money. The SDK reads ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN from the
environment.
Exit codes: 0 done, 2 no key or bad option or argument error, 3 every case fell back,
4 setup error, 1 unexpected error (traceback).
"""
import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.evaluator import (  # noqa: E402
    ModelSetupError,
    Problem,
    Speaker,
    Turn,
    evaluate,
    is_fallback,
)
from app.llm.haiku import EFFORT, MAX_TOKENS, MODEL_ID, HaikuModel  # noqa: E402

FIELDS = (
    "attempt",
    "stuck",
    "misconception_present",
    "valid_alternative",
    "asks_for_solution",
    "ambiguous_question",
)


def got_value(a, field):
    if field == "misconception_present":
        return a.misconception is not None
    value = getattr(a, field)
    return value.value if hasattr(value, "value") else value


def _max_tokens(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer") from None
    if value < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-id", default=MODEL_ID)
    parser.add_argument("--effort", default=EFFORT, choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--max-tokens", type=_max_tokens, default=MAX_TOKENS)
    args = parser.parse_args(argv)
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        print("No key. Set ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN and run again.")
        return 2
    cases = json.loads((Path(__file__).parent / "scenario_labels.json").read_text())
    try:
        model = HaikuModel(model=args.model_id, effort=args.effort, max_tokens=args.max_tokens)
    except (ValueError, TypeError) as error:
        print(f"Bad option: {type(error).__name__}.")
        return 2
    failures: Counter[str] = Counter()

    def on_failure(kind: str, detail: str) -> None:
        failures[kind] += 1

    agree = dict.fromkeys(FIELDS, 0)
    fallbacks = 0
    scored = 0
    lines = []
    for case in cases:
        problem = Problem(case["problem"], case["expected_approach"])
        turns = [Turn(Speaker(t["speaker"]), t["text"]) for t in case["turns"]]
        try:
            a = evaluate(problem, turns, case["message"], model, on_failure=on_failure)
        except ModelSetupError as error:
            print(f"Setup error: {str(error)}. Check the key and the model ID.")
            return 4
        if is_fallback(a):
            fallbacks += 1
            lines.append(f"{case['id']}  (fallback, not scored)")
            continue
        scored += 1
        lines.append(case["id"])
        for f in FIELDS:
            want, got = case["expected"][f], got_value(a, f)
            ok = want == got
            agree[f] += ok
            lines.append(f"  {'ok ' if ok else 'BAD'} {f}: expected {want!r}, got {got!r}")
    total = len(cases)
    print(f"Model {args.model_id}, effort {args.effort}")
    print(f"fallback {fallbacks}/{total}")
    for kind in sorted(failures):
        print(f"  {kind}: {failures[kind]}")
    if scored == 0:
        print("All calls failed.")
        return 3
    print()
    print("\n".join(lines))
    print(f"\n{'field':<22}agreement (cases without fallback)")
    for f in FIELDS:
        print(f"{f:<22}{agree[f]}/{scored}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
