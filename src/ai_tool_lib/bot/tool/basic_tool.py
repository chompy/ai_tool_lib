# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from typing import Callable, Iterable

from ai_tool_lib.bot.tool.base_tool import BaseTool
from ai_tool_lib.bot.tool.property import PropertyDefinition
from ai_tool_lib.bot.tool.response import ToolResponse


class BasicTool(BaseTool):
    """Basic implementation of a tool."""

    def __init__(
        self,
        name: str,
        description: str,
        properties: Iterable[PropertyDefinition],
        execute: Callable[..., ToolResponse],
    ):
        self._name = name
        self._description = description
        self._properties = list(properties)
        self._execute = execute

    def name(self):
        return self._name

    def description(self):
        return self._description

    def properties(self):
        return self._properties

    def execute(self, *args, **kwargs):
        return self._execute(*args, **kwargs)
