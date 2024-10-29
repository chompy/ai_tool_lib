# SPDX-FileCopyrightText: 2024-present Nathan Ogden <nathan@ogden.tech>
#
# SPDX-License-Identifier: MIT


from ai_tool_lib import BasicTool, get_bot_client
from ai_tool_lib.bot.message import BotMessageRole
from ai_tool_lib.bot.tool.property import PropertyDefinition
from ai_tool_lib.bot.tool.response import ToolUserResponse

""" Test a simple call and response to local Ollama bot. """

client = get_bot_client(
    "openai",
    api_key="_",
    base_url="http://127.0.0.1:11434/v1",
    model="llama3.2:3b",
    tools=[
        BasicTool(
            "done",
            "Respond to the user.",
            properties=[PropertyDefinition(name="message", type=str, description="Your response to the user.")],
            execute=lambda message: ToolUserResponse(data={"message": message}),
        )
    ],
)


def test_one_shot():
    prompt = "Marco!"
    res = client.run(prompt)
    # assert that expected result properties are not empty
    assert res.uid != ""
    assert res.prompt == prompt
    assert len(res.tool_calls) > 0
    assert res.iterations > 0
    assert res.input_tokens > 0
    assert res.output_tokens > 0
    assert res.session.uid != ""
    assert len(res.session.messages) > 0

    # assert that the expected tool was called
    assert res.tool_calls[0].tool == "done"
    assert "message" in res.tool_calls[0].args
    assert isinstance(res.tool_calls[0].response, ToolUserResponse)
    assert res.response_data["message"] != ""


def test_multi_conversation_session():
    # start first bot run, ensure there is a response
    res = client.run("Hello my name is Nathan!")
    assert res.response_data["message"] != ""
    assert len(list(filter(lambda m: m.role == BotMessageRole.TOOL, res.session.messages))) == 1

    # start second bot run, pass in the previous session
    res2 = client.run("What is my name?", res.session)
    assert res2.response_data["message"] != ""
    assert len(list(filter(lambda m: m.role == BotMessageRole.TOOL, res2.session.messages))) == 2
    assert (
        "nathan" in res2.response_data["message"].lower()
    )  # test that bot is able to infer context from previous query in same session
