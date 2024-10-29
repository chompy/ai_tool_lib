# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import datetime
from typing import Any, Literal

from pydantic import BaseModel


class ToolResponse(BaseModel):
    created: datetime.datetime | None = None
    """ Time response was created. """

    data: dict[str, Any] | None = None
    """ Data collected from bot response. """

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        if not self.created:
            self.created = datetime.datetime.now(tz=datetime.UTC)


class ToolBotResponse(ToolResponse):
    """A tool response to send back to the bot for further analysis."""

    type: Literal["bot"] = "bot"
    """ Response type name. """

    content: str
    """ The response content for the bot to analyze. """


class ToolUserResponse(ToolResponse):
    """A tool response to show to the user."""

    type: Literal["user"] = "user"
    """ Response type name. """
