# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

import os
from ai_tool_lib import BasicTool, get_bot_client
from ai_tool_lib.bot.tool.property import PropertyDefinition
from ai_tool_lib.bot.tool.response import ToolUserResponse

client = get_bot_client(
    "openai",
    # api_key=os.environ.get("OPENAI_API_KEY"),
    api_key="123",
    base_url="http://127.0.0.1:11434/v1",
    model="llama3.2:3b",
    tools=[
        BasicTool(
            "done",
            "Respond to the user.",
            properties=[PropertyDefinition(name="message", type=str, description="Your response to the user.")],
            execute=lambda message: ToolUserResponse(parameters={"message": message}),
        )
    ],
)

res = client.run("Test!")

print(res, res.response)

print(res.session)

resb = client.run("Marco!", res.session)

print(resb, resb.response)
