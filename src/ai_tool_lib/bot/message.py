from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class BotMessageRole(StrEnum):
    """Message role/sender."""

    SYSTEM = "system"
    USER = "user"
    BOT = "assistant"
    FUNC = "function"
    TOOL = "tool"


class BotToolMessage(BaseModel):
    """Tool call request message."""

    id: str
    """ Tool call request ID. """

    name: str
    """ Tool name. """

    args: str
    """ Tool call arguments. """


class BotMessage(BaseModel):
    """A message to send to the bot."""

    role: BotMessageRole
    """ Message role/sender. """

    content: str | None
    """ Message content. """

    tool_calls: list[BotToolMessage] | None = None
    """ List of tool call requests. """

    tool_call_id: str | None = None
    """ Tool call request ID. """
