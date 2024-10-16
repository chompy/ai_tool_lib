from __future__ import annotations

from ai_tool_lib.bot.client.openai import OpenAIBotClient
from ai_tool_lib.error.bot import BotClientNotFoundError

AVAILABLE_CLIENTS = [OpenAIBotClient]


def get_bot_client(name: str, **kwargs):
    for client_class in AVAILABLE_CLIENTS:
        if client_class.name() == name:
            return client_class(**kwargs)
    err_msg = f"bot client {name} was not found"
    raise BotClientNotFoundError(err_msg)
