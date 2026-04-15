"""Simple MCP server with one demo tool: get_greeting."""
import asyncio
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

server = Server("demo-server")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_greeting",
            description="Returns a personalized greeting for the given name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the person to greet.",
                    }
                },
                "required": ["name"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "get_greeting":
        person = arguments.get("name", "World")
        return [types.TextContent(type="text", text=f"Hello, {person}! Welcome to the MCP demo.")]
    raise ValueError(f"Unknown tool: {name}")


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
