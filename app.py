"""Demo app: calls Claude (claude-opus-4-6) with tools from the local MCP server."""
import asyncio
import sys
import anthropic
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


async def main():
    client = anthropic.Anthropic()

    # Launch mcp_server.py as a subprocess and connect to it via stdio
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["mcp_server.py"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools from the MCP server
            tools_result = await session.list_tools()
            anthropic_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in tools_result.tools
            ]
            print(f"MCP tools available: {[t['name'] for t in anthropic_tools]}\n")

            messages = [{"role": "user", "content": "Please greet Alice using the greeting tool."}]

            # Agentic loop — keep going until Claude stops calling tools
            while True:
                response = client.messages.create(
                    model="claude-opus-4-6",
                    max_tokens=1024,
                    tools=anthropic_tools,
                    messages=messages,
                )

                if response.stop_reason == "end_turn":
                    for block in response.content:
                        if block.type == "text":
                            print("Claude:", block.text)
                    break

                if response.stop_reason == "tool_use":
                    messages.append({"role": "assistant", "content": response.content})

                    tool_results = []
                    for block in response.content:
                        if block.type == "tool_use":
                            print(f"Tool call: {block.name}({block.input})")
                            result = await session.call_tool(block.name, block.input)
                            text = result.content[0].text if result.content else ""
                            print(f"Tool result: {text}\n")
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": text,
                            })

                    messages.append({"role": "user", "content": tool_results})
                else:
                    break


if __name__ == "__main__":
    asyncio.run(main())
