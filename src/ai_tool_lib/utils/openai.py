# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionFunctionMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionUserMessageParam,
)


def chat_completion_from_dict(message: dict) -> ChatCompletionMessageParam:
    match message.get("role"):
        case "function":
            return ChatCompletionFunctionMessageParam(**message)
        case "system":
            return ChatCompletionSystemMessageParam(**message)
        case "tool":
            return ChatCompletionToolMessageParam(**message)
        case "user":
            return ChatCompletionUserMessageParam(**message)
        case "assistant":
            return ChatCompletionAssistantMessageParam(**message)
    err_msg = "unexpected message type"
    raise TypeError(err_msg)
