# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from ai_tool_lib.error.user_friendly import UserFriendlyError

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_tool_lib.bot.results import BotResults


class BotClientNotFoundError(Exception, UserFriendlyError):
    """Bot client of provided name does not exist."""

    def user_friendly_message(self) -> str:
        return "Bot not available."


class BotError(Exception):
    """Generic bot error."""

    def __init__(self, *args, results: BotResults | None = None, **kwargs):
        self.results = results
        super().__init__(*args, **kwargs)


class UnexpectedBotResponseError(BotError, UserFriendlyError):
    """The bot provided an unexpected response."""

    def user_friendly_message(self) -> str:
        return "Bot provided an unexpected response."


class BotIterationLimitError(BotError, UserFriendlyError):
    """The bot reached the iteration limit without providing a user response."""

    def user_friendly_message(self) -> str:
        return "Bot reached iteration limit without providing a response."


class MalformedBotResponseError(UnexpectedBotResponseError, UserFriendlyError):
    """
    Raised when LLM produces a malformed response. When this is
    raised we should ask the LLM to retry.
    """

    def retry_message(self) -> str:
        return "I'm sorry, I couldn't understand your response, or something was missing. Please try again."

    def user_friendly_message(self) -> str:
        return "Bot provided a malformed response."


class BotTokenLimitError(BotError, UserFriendlyError):
    """Bot reached max token limit for the session."""

    def user_friendly_message(self) -> str:
        return "Bot reached token limit."