"""Demo app: calls OpenRouter (openai/gpt-4o) with tools from the local MCP server."""
import asyncio
import json
import os
import sys
from openai import OpenAI
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

OPENROUTER_MODEL = "openai/gpt-oss-20b:free"

async def main():
    client = OpenAI(
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
    )

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools from the MCP server
            tools_result = await session.list_tools()
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in tools_result.tools
            ]
            print(f"MCP tools available: {[t['function']['name'] for t in openai_tools]}\n")

            messages = [{"role": "user", "content": "Please greet George Mateev using the greeting tool."}]

            # Agentic loop — keep going until the model stops calling tools
            while True:
                response = client.chat.completions.create(
                    model=OPENROUTER_MODEL,
                    max_tokens=1024,
                    tools=openai_tools,
                    messages=messages,
                )

                if not response.choices:
                    print("Error response:", response)
                    break
                choice = response.choices[0]
                message = choice.message

                if choice.finish_reason == "stop":
                    print("OpenRouter:", message.content)
                    break

                if choice.finish_reason == "tool_calls":
                    messages.append(message)

                    for tool_call in message.tool_calls:
                        args = json.loads(tool_call.function.arguments)
                        print(f"Tool call: {tool_call.function.name}({args})")
                        result = await session.call_tool(tool_call.function.name, args)
                        text = result.content[0].text if result.content else ""
                        print(f"Tool result: {text}\n")
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": text,
                        })
                else:
                    break


if __name__ == "__main__":
    asyncio.run(main())
