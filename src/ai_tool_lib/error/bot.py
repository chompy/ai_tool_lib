# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai_tool_lib.bot.results import BotResults


class BotClientNotFoundError(Exception):
    """Bot client of provided name does not exist."""


class BotError(Exception):
    """Generic bot error."""

    def __init__(self, *args, results: BotResults | None = None, **kwargs):
        self.results = results
        super().__init__(*args, **kwargs)


class UnexpectedBotResponseError(BotError):
    """The bot provided an unexpected response."""


class BotIterationLimitError(BotError):
    """The bot reached the iteration limit without providing a user response."""


class MalformedBotResponseError(UnexpectedBotResponseError):
    """
    Raised when LLM produces a malformed response. When this is
    raised we should ask the LLM to retry.
    """

    def retry_message(self) -> str:
        return "I'm sorry, I couldn't understand your response, or something was missing. Please try again."


class BotTokenLimitError(BotError):
    """Bot reached max token limit for the session."""
