# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from typing import Any, Self

from pydantic import BaseModel

from ai_tool_lib.bot.session import BotSession
from ai_tool_lib.bot.tool.response import ToolResponse, ToolUserResponse
from ai_tool_lib.utils.uuid import generate_uuid


class BotToolCall(BaseModel):
    """Information about a bot tool call."""

    tool: str
    """ The name of the tool. """

    args: dict[str, Any]
    """ The args used to call the tool. """

    response: ToolResponse
    """ The results of the tool call that is sent to the bot. """


class BotResults(BaseModel):
    """The results of a bot query."""

    uid: str
    """ Unique ID for this result. """

    created: datetime.datetime
    """ Time results were generated. """

    prompt: str = ""
    """ The user's prompt for the bot. """

    tool_calls: list[BotToolCall]
    """ List of tool calls the bot made. """

    iterations: int = 0
    """ The number of iterations it took to complete. """

    input_tokens: int = 0
    """ The number of tokens sent to the bot. """

    output_tokens: int = 0
    """ The number of tokens the bot generated. """

    session: BotSession
    """ The session that was used to generate the results. """

    @classmethod
    def new(cls, prompt: str = "", session: BotSession | None = None) -> Self:
        """Create new results."""
        if not session:
            session = BotSession.new()
        return cls(
            uid=generate_uuid(),
            prompt=prompt,
            tool_calls=[],
            created=datetime.datetime.now(tz=datetime.UTC),
            session=session,
        )

    @property
    def response(self) -> ToolUserResponse | None:
        return (
            self.tool_calls[-1].response
            if self.tool_calls and isinstance(self.tool_calls[-1].response, ToolUserResponse)
            else None
        )

    @property
    def response_data(self) -> dict[str, Any]:
        resp = self.response
        return resp.data if resp and resp.data else {}
