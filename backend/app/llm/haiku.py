from __future__ import annotations

import anthropic

from app.evaluator import ModelRefusal, ModelSetupError

from .schema import ASSESSMENT_SCHEMA

MODEL_ID = "claude-haiku-5-5"
MAX_TOKENS = 2048
EFFORT = "low"
TIMEOUT_SECONDS = 30.0
SDK_MAX_RETRIES = 0

_EFFORTS = frozenset({"low", "medium", "high", "xhigh", "max"})
_SETUP_ERRORS = (
    anthropic.AuthenticationError,
    anthropic.PermissionDeniedError,
    anthropic.NotFoundError,
    anthropic.BadRequestError,
)


# The SDK raises a TypeError with this text when no credential is set.
_MISSING_CREDENTIALS_TEXT = "Could not resolve authentication method"


class ModelCallError(Exception):
    """The model call returned no usable text."""


class HaikuModel:
    """The `Model` interface from `app.evaluator`, backed by Claude Haiku."""

    def __init__(
        self,
        client=None,
        *,
        model: str = MODEL_ID,
        max_tokens: int = MAX_TOKENS,
        effort: str = EFFORT,
    ) -> None:
        if type(model) is not str:
            raise TypeError("model must be a str")
        if not model.strip():
            raise ValueError("model must not be blank")
        if type(max_tokens) is not int:
            raise TypeError("max_tokens must be an int")
        if max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
        if type(effort) is not str:
            raise TypeError("effort must be a str")
        if effort not in _EFFORTS:
            raise ValueError(f"effort must be one of {sorted(_EFFORTS)}")
        if client is None:
            # The SDK reads the key from the environment itself.
            client = anthropic.Anthropic(
                timeout=TIMEOUT_SECONDS, max_retries=SDK_MAX_RETRIES
            )
        self._client = client
        self._model = model
        self._max_tokens = max_tokens
        self._effort = effort

    def complete(self, prompt: str) -> str:
        if type(prompt) is not str:
            raise TypeError("prompt must be a str")
        if not prompt.strip():
            raise ValueError("prompt must not be blank")
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                messages=[{"role": "user", "content": prompt}],
                output_config={
                    "effort": self._effort,
                    "format": {"type": "json_schema", "schema": ASSESSMENT_SCHEMA},
                },
            )
        except _SETUP_ERRORS as exc:
            raise ModelSetupError(f"{type(exc).__name__}") from exc
        except TypeError as exc:
            if _MISSING_CREDENTIALS_TEXT in str(exc):
                raise ModelSetupError("MissingCredentials") from exc
            raise
        reason = response.stop_reason
        if reason == "refusal":
            raise ModelRefusal("model refused")
        if reason != "end_turn":
            raise ModelCallError(f"model stopped with stop_reason {reason!r}")
        for block in response.content:
            if block.type == "text":
                if not isinstance(block.text, str):
                    raise ModelCallError("text block is not a str")
                return block.text
        raise ModelCallError("response has no text block")
