# ADR 0004: Claude Haiku 5.5 runs the evaluator

**Status:** Accepted. It amends ADR 0003.

## Decision
- The evaluator model is Claude Haiku 5.5. The model ID is `claude-haiku-5-5`. Keep the ID in one constant.
- Put the Haiku client in `backend/app/llm/`. It implements the `Model` interface from ADR 0003. `app/evaluator/` stays free of network code.
- Use the Anthropic Python SDK (`anthropic`). Call `client.messages.create`.
- The SDK reads `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` from the environment. Never store the key in the repository.
- Ask for JSON with `output_config.format` (`json_schema`). The schema lists the seven fields, the allowed `attempt` and `stuck` values, and `additionalProperties: false`.
- `parse_reply` stays the real check. The schema cannot state the 80-character limit or the cross-field rule.
- Set `output_config.effort` to `low`. The task is labeling, not reasoning.
- Leave `thinking` unset. Thinking tokens count toward `max_tokens`, so set `max_tokens` to 2048.
- Do not send `temperature`, `top_p`, or `top_k`. They can return an error on this model.
- End `messages` with one user turn. Do not send an assistant prefill.
- Read the answer from the first content block with `type == "text"`. A reply can start with a thinking block.
- Set a timeout of 30 seconds. Set SDK retries to 0. The evaluator retries once (ADR 0003).
- Only `stop_reason` `end_turn` may return text. `refusal` raises `ModelRefusal`. The evaluator does not retry it and returns the fallback form. Any other value raises `ModelCallError`. A reply with no text block also raises it.
- `AuthenticationError`, `PermissionDeniedError`, `NotFoundError`, and `BadRequestError` raise `ModelSetupError`. A retry cannot fix them. The evaluator raises it again. Other SDK errors pass through unchanged, and the evaluator retries once.
- Unit tests use a fake Anthropic client. They need no key and no network.
- A manual script in `evals/` runs the Haiku client on the five conversations in `docs/scenarios.md`. The developer runs it.

## Options considered
- Haiku 5.5 with low effort: chosen. Fastest and cheapest of the current models. The price is $0.10 / $0.50 per million tokens up to 100,000 prompt tokens; $0.50 / $2.50 above.
- Sonnet 5.5: may label hard cases better. It costs about 20 times more for each token.
- Haiku 5.5 at default effort (medium): slower and costs more. Try it if the evals show weak labels.

## Risks
- The docs say Claude may change the capitalization of an enum value. The parser accepts any ASCII letter case for `attempt` and `stuck`.
- The first request with a new schema is slower. The API caches the compiled schema for 24 hours.
- Version 1 has no streaming and no cost log.

## Revisit when
- The evals show a field with weak agreement. Raise the effort or change the model.
- A newer Haiku or a cheaper model appears.

## Sources (read 2026-10-16)
- Haiku 5.5 overview: https://platform.claude.com/docs/en/models/haiku-5-5/overview
- Haiku 5.5 migration guide: https://platform.claude.com/docs/en/models/haiku-5-5/migration-guide
- Structured outputs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- Effort: https://platform.claude.com/docs/en/build-with-claude/effort
