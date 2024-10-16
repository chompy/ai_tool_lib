# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import openai
from openai.types.chat import (
    ChatCompletionMessageToolCall,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
)
from openai.types.shared_params.function_definition import FunctionDefinition

from ai_tool_lib.bot.client.base import BaseBotClient
from ai_tool_lib.bot.results import BotResults, BotToolCall
from ai_tool_lib.bot.tool.response import ToolResponse, ToolUserResponse
from ai_tool_lib.error.bot import UnexpectedBotResponseError
from ai_tool_lib.utils.openai import chat_completion_from_dict

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

    @staticmethod
    def name() -> str:
        return "openai"

    def _handle_chat_completion(self, messages: list[dict], results: BotResults) -> list[dict]:
        tool_handler = self._get_tool_handler(results)
        response = self.client.chat.completions.create(
            messages=[chat_completion_from_dict(m) for m in messages],
            model=self.model,
            temperature=0.2,
            top_p=0.1,
            tools=self._get_tool_definitions(tool_handler),
            tool_choice="required",
        )
        if len(response.choices) == 0:
            msg = "empty response from chat completion endpoint"
            raise UnexpectedBotResponseError(msg, results=results)
        out = []
        response_message = response.choices[0].message
        out.append(response_message.to_dict(mode="json"))
        # make tool calls
        if response_message.tool_calls:
            for call in response_message.tool_calls:
                resp = self._tool_call(tool_handler, call)
                results.tool_calls.append(
                    BotToolCall(tool=call.function.name, args=json.loads(call.function.arguments), response=resp)
                )
                # tool provided a user answer
                if isinstance(resp, ToolUserResponse):
                    out.append(ChatCompletionToolMessageParam(content="(done)", role="tool", tool_call_id=call.id))
                    break
                # tool provided a response for the bot to read
                out.append(ChatCompletionToolMessageParam(content=resp.content, role="tool", tool_call_id=call.id))
        # add token usages
        if response.usage:
            results.input_tokens += response.usage.prompt_tokens
            results.output_tokens += response.usage.completion_tokens
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
                        "properties": {p.name: p.to_dict() for p in t.properties()},
                        "required": [p.name for p in filter(lambda p: p.required, t.properties())],
                    },
                ),
                type="function",
            )
            for t in tool_handler.tools
        ]
