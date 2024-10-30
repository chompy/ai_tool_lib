# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from abc import abstractmethod
from typing import TYPE_CHECKING, Callable, Iterable

from ai_tool_lib.bot.message import BotMessage, BotMessageRole
from ai_tool_lib.bot.results import BotResults
from ai_tool_lib.bot.session import BotSession
from ai_tool_lib.bot.tool.handler import ToolHandler
from ai_tool_lib.bot.tool.response import ToolUserResponse
from ai_tool_lib.error.bot import BotIterationLimitError, BotTokenLimitError, MalformedBotResponseError

if TYPE_CHECKING:
    from ai_tool_lib.bot.tool.base_tool import BaseTool

DEFAULT_SYSTEM_PROMPT = """
You are a helpful assistant with access to tools which can help you assist the user.
"""

DEFAULT_ITERATION_LIMIT_PROMPT = """
It is now time to respond to the user. If you were unable to complete the task then let the user know why.
"""


class BaseBotClient:
    def __init__(
        self,
        tools: Iterable[BaseTool] | Callable[[BotResults], Iterable[BaseTool]],
        logger: logging.Logger | None = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        session_token_limit: int = 64000,
        iteration_limit: int = 5,
        iteration_limit_prompt: str | None = DEFAULT_ITERATION_LIMIT_PROMPT,
        error_retry_limit: int = 3,
    ):
        """
        Client used to interact with AI LLM bot.
        :param tools: The tools the bot can use, must provide at least one. It can be a callable that is passed BotResults every iteration.
        :param logger: Optional logger.
        :param system_prompt: The system prompt which gives the bot instructions on how to handle the user's prompt.
        :param session_token_limit: Number of input tokens allowed in a session.
        :param iteration_limit: Number of iterations allowed in a single run.
        :param iteration_limit_prompt: Message to send to the bot on the last iteration.
        :param error_retry_limit: Number of retries the bot is allowed when it provides an errorneous response.
        """
        self.tools = tools
        if isinstance(self.tools, Iterable):
            self.tools = list(self.tools)
        self.logger = logger
        self.system_prompt = system_prompt
        self.session_token_limit = session_token_limit
        self.iteration_limit = iteration_limit
        self.iteration_limit_prompt = iteration_limit_prompt
        self.error_retry_limit = error_retry_limit

    def run(self, prompt: str, session: BotSession | None = None) -> BotResults:
        """
        Run the bot with given prompt. Resume previous session if provided.
        :param prompt: Prompt for bot.
        :param session: Session with previous chat history.
        """

        if not session:
            session = BotSession.new()
            session.messages = [BotMessage(role=BotMessageRole.SYSTEM, content=self.system_prompt)]

        self._log("Init bot.", prompt=prompt, client=self.name(), session_uid=session.uid)

        session.messages.append(BotMessage(role=BotMessageRole.USER, content=prompt))
        results = BotResults.new(prompt=prompt, session=session)

        for iteration in range(1, self.iteration_limit + 1):
            self._log(f"Iteration {iteration}.", iteration=iteration, results=results, session_uid=session.uid)
            results.iterations = iteration

            # check token limit
            if self.session_token_limit > 0 and results.input_tokens > self.session_token_limit:
                err_msg = "session reached token limit"
                raise BotTokenLimitError(err_msg, results=results)

            # on last iteration add iteration limit prompt
            if iteration == self.iteration_limit:
                self._log("Iteration limit reached", iteration_limit=self.iteration_limit, session_uid=session.uid)
                if self.iteration_limit_prompt:
                    session.messages.append(BotMessage(role=BotMessageRole.USER, content=self.iteration_limit_prompt))

            # submit messages to llm, allow it to retry if malformed response is returned
            for err_retry_iter in range(self.error_retry_limit):
                try:
                    session.messages += self._handle_chat_completion(messages=session.messages, results=results)
                    break
                except MalformedBotResponseError as e:
                    if err_retry_iter >= self.error_retry_limit - 1:
                        raise
                    session.messages.append(BotMessage(role=BotMessageRole.USER, content=e.retry_message()))
                    self._log(
                        f"Bot malformed response. Retry #{err_retry_iter+1}",
                        level=logging.WARNING,
                        retry_number=err_retry_iter + 1,
                        error_class=e.__class__.__name__,
                        error=str(e),
                        retry_message=e.retry_message(),
                        session_uid=session.uid,
                    )

            # if tool returns a user response then we're done
            if results.tool_calls and isinstance(results.tool_calls[-1].response, ToolUserResponse):
                self._log(
                    "User response received.",
                    response=results.tool_calls[-1].response,
                    results=results,
                    session_uid=session.uid,
                )
                return results

        err_msg = "bot reached iteration limit without producing a user response"
        raise BotIterationLimitError(err_msg, results=results)

    @staticmethod
    @abstractmethod
    def name() -> str:
        """Name of the client."""
        ...

    @abstractmethod
    def _handle_chat_completion(self, messages: list[BotMessage], results: BotResults) -> list[BotMessage]:
        """
        Submit current context to LLM as chat completion.
        :param messages: Chat history with LLM.
        :param results: Current results
        """
        ...

    def _generate_message(self, role: str, content: str) -> dict:
        return {"role": role, "content": content}

    def _get_tool_handler(self, results: BotResults) -> ToolHandler:
        tools = []
        if isinstance(self.tools, list):
            tools = self.tools
        elif isinstance(self.tools, Callable):
            tools = list(self.tools(results))
        return ToolHandler(tools=tools, logger=self.logger)

    def _log(self, message: str, level: int = logging.INFO, **kwargs):
        if self.logger:
            self.logger.log(level, message, extra={"_module": "bot", **kwargs})
