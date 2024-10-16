# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Any, Union

from pydantic import BaseModel
from typing_extensions import TypeAlias


class ToolBotResponse(BaseModel):
    """A tool response to send back to the bot for further analysis."""

    content: str
    """ The response content for the bot to analyze. """


class ToolUserResponse(BaseModel):
    """A tool response to show to the user."""

    parameters: dict[str, Any]
    """ Data passed back by the bot. """


ToolResponse: TypeAlias = Union[ToolBotResponse, ToolUserResponse]
