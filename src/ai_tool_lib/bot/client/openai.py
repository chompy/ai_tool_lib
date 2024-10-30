# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import openai
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionFunctionMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCall,
    ChatCompletionMessageToolCallParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from openai.types.chat.chat_completion_message_tool_call_param import Function
from openai.types.shared_params.function_definition import FunctionDefinition

from ai_tool_lib.bot.client.base import BaseBotClient
from ai_tool_lib.bot.message import BotMessage, BotMessageRole, BotToolMessage
from ai_tool_lib.bot.results import BotResults, BotToolCall
from ai_tool_lib.bot.tool.response import ToolBotResponse, ToolResponse, ToolUserResponse
from ai_tool_lib.error.bot import BotNoToolCallError, UnexpectedBotResponseError

if TYPE_CHECKING:
    from ai_tool_lib.bot.tool.handler import ToolHandler


class OpenAIBotClient(BaseBotClient):
    def __init__(self, api_key: str, base_url: str | None = None, model: str = "gpt-4o-mini", **kwargs):
        super().__init__(**kwargs)
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.model = model
        self._log("Using OpenAI client.", base_url=base_url, model=model)

    @staticmethod
    def name() -> str:
        return "openai"

    def _handle_chat_completion(self, messages: list[BotMessage], results: BotResults):
        tool_handler = self._get_tool_handler(results)
        response = self.client.chat.completions.create(
            messages=[self._chat_completion_from_bot_message(m) for m in messages],
            model=self.model,
            temperature=0.2,
            top_p=0.1,
            tools=self._get_tool_definitions(tool_handler),
            tool_choice="required",
        )
        if len(response.choices) == 0:
            msg = "empty response from chat completion endpoint"
            raise UnexpectedBotResponseError(msg, results=results)

        response_message = response.choices[0].message
        out = [
            BotMessage(
                role=BotMessageRole.BOT,
                content=response_message.content,
                tool_calls=[
                    BotToolMessage(id=t.id, name=t.function.name, args=t.function.arguments)
                    for t in response_message.tool_calls
                ]
                if response_message.tool_calls
                else None,
            )
        ]

        # add token usages
        if response.usage:
            results.input_tokens += response.usage.prompt_tokens
            results.output_tokens += response.usage.completion_tokens

        # let bot know it must use tool calls if none provided
        if not response_message.tool_calls:
            err_msg = "bot did not call a tool"
            raise BotNoToolCallError(err_msg, results=results)

        # handle tool calls
        for call in response_message.tool_calls:
            resp = self._tool_call(tool_handler, call)
            results.tool_calls.append(
                BotToolCall(tool=call.function.name, args=json.loads(call.function.arguments), response=resp)
            )
            # tool provided a user answer
            if isinstance(resp, ToolUserResponse):
                out.append(BotMessage(role=BotMessageRole.TOOL, content="(done)", tool_call_id=call.id))
                break
            # tool provided a response for the bot to read
            if isinstance(resp, ToolBotResponse):
                out.append(BotMessage(role=BotMessageRole.TOOL, content=resp.content, tool_call_id=call.id))

        return out

    def _tool_call(self, tool_handler: ToolHandler, tool_call: ChatCompletionMessageToolCall) -> ToolResponse:
        return tool_handler.call(tool_call.function.name, json.loads(tool_call.function.arguments))

    def _get_tool_definitions(self, tool_handler: ToolHandler) -> list[ChatCompletionToolParam]:
        return [
            ChatCompletionToolParam(
                function=FunctionDefinition(
                    name=t.name(),
                    description=t.description(),
                    parameters={
                        "type": "object",
                        "properties": {p.name: p.to_json_schema() for p in t.properties()},
                        "required": [p.name for p in filter(lambda p: p.required, t.properties())],
                    },
                ),
                type="function",
            )
            for t in tool_handler.tools
        ]

    def _chat_completion_from_bot_message(self, message: BotMessage) -> ChatCompletionMessageParam:
        dump = message.model_dump(mode="json")
        match message.role:
            case BotMessageRole.FUNC:
                return ChatCompletionFunctionMessageParam(**dump)
            case BotMessageRole.SYSTEM:
                return ChatCompletionSystemMessageParam(**dump)
            case BotMessageRole.TOOL:
                return ChatCompletionToolMessageParam(**dump)
            case BotMessageRole.USER:
                return ChatCompletionUserMessageParam(**dump)
            case BotMessageRole.BOT:
                tool_calls = []
                if message.tool_calls:
                    tool_calls = [
                        ChatCompletionMessageToolCallParam(
                            type="function", id=t.id, function=Function(name=t.name, arguments=t.args)
                        )
                        for t in message.tool_calls
                    ]
                dump["tool_calls"] = tool_calls

                return ChatCompletionAssistantMessageParam(**dump)
