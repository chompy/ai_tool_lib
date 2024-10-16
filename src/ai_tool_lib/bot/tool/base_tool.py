# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from ai_tool_lib.bot.tool.property import PropertyDefinition
    from ai_tool_lib.bot.tool.response import ToolResponse


class BaseTool:
    @abstractmethod
    def name(self) -> str:
        """The tool name. The bot uses this to call the tool."""
        ...

    @abstractmethod
    def description(self) -> str:
        """Description for the bot on how to use the tool."""
        ...

    @abstractmethod
    def properties(self) -> Iterable[PropertyDefinition]:
        """The properties and their constraints that the bot should provide when calling the tool."""
        ...

    @abstractmethod
    def execute(self, *args, **kwargs) -> ToolResponse:
        """Executes the tool."""
        ...
