from __future__ import annotations


class ScriptedModel:
    """A fake model. It returns or raises the next scripted reply."""

    def __init__(self, replies: list[str | Exception]) -> None:
        replies = list(replies)
        for reply in replies:
            if not isinstance(reply, (str, Exception)):
                raise TypeError("each reply must be a str or an Exception instance")
        self._replies = replies
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self._replies:
            raise IndexError("no scripted replies left")
        reply = self._replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply
