# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from ai_tool_lib.error.bot import MalformedBotResponseError
from ai_tool_lib.error.user_friendly import UserFriendlyError


class ToolPropertyTypeError(TypeError, UserFriendlyError):
    """Tool property definition has an invalid property type."""

    def user_friendly_message(self) -> str:
        return "One or more tools are improperly configured."


class ToolPropertyChoiceTypeError(TypeError, UserFriendlyError):
    """Tool property definition has a choice that does not match the property type."""

    def user_friendly_message(self) -> str:
        return "One or more tools are improperly configured."


class ToolListEmptyError(Exception, UserFriendlyError):
    """Tool handler received empty list of tools."""

    def user_friendly_message(self) -> str:
        return "No tools have been provided."


class ToolPropertyInvalidError(ValueError, MalformedBotResponseError, UserFriendlyError):
    """A tool property failed to pass contraint validation."""

    def __init__(self, tool_name: str, property_name: str, why: str | None = None) -> None:
        self.tool_name = tool_name
        self.property_name = property_name
        self.why = why
        super().__init__(f"property '{self.property_name!s}' is invalid for tool '{self.tool_name!s}'")

    def retry_message(self):
        return f"Property '{self.property_name!s}' was invalid in your call to the '{self.tool_name!s}' tool. {(self.why + " ") if self.why else ""}Please try again."

    def user_friendly_message(self) -> str:
        return "Bot tool call failed to pass constraint validation."


class ToolPropertyMissingError(AttributeError, MalformedBotResponseError, UserFriendlyError):
    """A required tool property is missing."""

    def __init__(self, tool_name: str, property_name: str) -> None:
        self.tool_name = tool_name
        self.property_name = property_name
        super().__init__(f"required property '{self.property_name!s}' is missing for tool '{self.tool_name!s}'")

    def retry_message(self):
        return f"A required property, '{self.property_name!s}', was missing in your call to the '{self.tool_name!s}' tool. Please try again."

    def user_friendly_message(self) -> str:
        return "Bot tool call failed to pass constraint validation."


class ToolNotDefinedError(MalformedBotResponseError, UserFriendlyError):
    """The called tool is not defined."""

    def __init__(self, tool_name: str) -> None:
        self.tool_name = tool_name
        super().__init__(f"tool '{self.tool_name!s}' is not defined")

    def retry_message(self):
        return f"You tried to call a non-existent tool, '{self.tool_name!s}'. Please try again."

    def user_friendly_message(self) -> str:
        return "Bot tried to call an undefined tool."
