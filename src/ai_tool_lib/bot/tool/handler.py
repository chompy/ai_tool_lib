# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Iterable

from ai_tool_lib.error.tool import ToolListEmptyError, ToolNotDefinedError

if TYPE_CHECKING:
    from ai_tool_lib.bot.tool.base_tool import BaseTool
    from ai_tool_lib.bot.tool.response import ToolResponse


class ToolHandler:
    """Handles tool calls."""

    def __init__(self, tools: Iterable[BaseTool], logger: logging.Logger | None = None):
        self.tools = list(tools)
        self.logger = logger
        self._log("Init tool handler.", tool_names=[t.name() for t in self.tools])
        if not self.tools:
            err_msg = "tool handler requires at least one tool"
            raise ToolListEmptyError(err_msg)

    def call(self, name: str, args: dict) -> ToolResponse:
        """
        Find and execute a tool from its name.
        :param name: The tool name.
        :param args: Arguments to pass in to the tool, should match the tool's properties.
        """
        self._log(
            message=f"Call tool '{name!s}'.", action="call", object=f"tool '{name!s}'", tool_name=name, tool_args=args
        )
        try:
            for tool in self.tools:
                if tool.name() == name:
                    # check properties
                    for prop in tool.properties():
                        prop.check_value(args.get(prop.name), name)
                    # call tool
                    resp = tool.execute(**args)
                    self._log(
                        message=f"Tool '{name!s}' response.",
                        action="response",
                        object=tool,
                        tool_name=name,
                        tool_args=args,
                        tool_response=resp,
                    )
                    return resp
        except Exception as e:
            self._log(
                message=f"Tool '{name!s}' error.",
                level=logging.ERROR,
                action="error",
                object=f"tool '{name!s}'",
                tool_name=name,
                tool_args=args,
                error_class=e.__class__.__name__,
                error=str(e),
            )
            raise
        raise ToolNotDefinedError(name)

    def _log(self, message: str = "", level: int = logging.INFO, **kwargs):
        if self.logger:
            self.logger.log(level, message, extra={"_module": "tool", **kwargs})
