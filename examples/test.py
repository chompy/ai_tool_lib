# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT

from ai_tool_lib import SimpleTool, get_bot_client
from ai_tool_lib.bot.tool.property import PropertyDefinition
from ai_tool_lib.bot.tool.response import ToolUserResponse

client = get_bot_client(
    "openai",
    api_key="",
    tools=[
        SimpleTool(
            "done",
            "Respond to the user.",
            properties=[PropertyDefinition("message", str, "Your response to the user.")],
            execute=lambda message: ToolUserResponse(parameters={"message": message}),
        )
    ],
)

res = client.run("Test!")

print(res, res.response)

print(res.session)

resb = client.run("Marco!", res.session)

print(resb, resb.response)
