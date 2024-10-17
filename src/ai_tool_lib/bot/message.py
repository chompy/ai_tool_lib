from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class BotMessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    BOT = "assistant"
    FUNC = "function"
    TOOL = "tool"


class BotToolMessage(BaseModel):
    id: str
    name: str
    args: str


class BotMessage(BaseModel):
    """A message to send to the bot."""

    role: BotMessageRole
    content: str | None
    tool_calls: list[BotToolMessage] | None = None
    tool_call_id: str | None = None
