# llm

The Haiku client for the evaluator. It implements the `Model` interface from `app/evaluator/`. Spec: `docs/adr/0004-haiku-evaluator-model.md`.

## Files
- `haiku.py`: `HaikuModel`, `ModelCallError`, and the constants `MODEL_ID`, `MAX_TOKENS`, `EFFORT`, `TIMEOUT_SECONDS`, `SDK_MAX_RETRIES`. `complete(prompt)` makes one call and returns the text of the first text block.
- `schema.py`: `ASSESSMENT_SCHEMA`. The JSON schema for the seven assessment fields. It builds the enum lists from `app.policy.types`.

## Rules
- Read the key from the environment only. The SDK reads `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` from the environment. Never read, store, log, or print it.
- Never log or print the prompt or the reply.
- Send no sampling parameters (`temperature`, `top_p`, `top_k`). Send no `thinking`, no `system`, and no assistant prefill.
- Read the reply from the first content block with `type == "text"`.
- The default client uses a timeout of 30 seconds and no SDK retries. The evaluator retries once.
- Only `stop_reason` `end_turn` may return text. `refusal` raises `ModelRefusal`. A refusal is final: the evaluator does not retry it.
- Any other `stop_reason` raises `ModelCallError` and names the value. A reply with no text block also raises it.
- `AuthenticationError`, `PermissionDeniedError`, `NotFoundError`, and `BadRequestError` raise `ModelSetupError`. The message holds the class name only.
- With no key, the SDK raises a `TypeError` at call time. The message starts with "Could not resolve authentication method". Only that `TypeError` becomes `ModelSetupError("MissingCredentials")`. Any other `TypeError` passes through.
- Other SDK errors (rate limit, connection, timeout, server error) pass through unchanged.
- The schema uses only keywords that the API supports. `parse_reply` stays the real check.
- Tests use a fake client. They need no key and no network.
