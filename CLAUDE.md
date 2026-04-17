# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY=sk-...   # required by app.py
```

## Running

```bash
# Run the demo app (starts MCP server automatically as a subprocess)
python app.py

# Run the MCP server standalone (communicates via stdio)
python mcp_server.py
```

## Architecture

Two files, two roles:

**`mcp_server.py`** — A stdio-based MCP server built with the `mcp` Python SDK. Exposes one tool (`get_greeting`). Claude never talks to this directly — it is spawned as a subprocess by the client.

**`app.py`** — The client. It:
1. Launches `mcp_server.py` as a subprocess via `StdioServerParameters`
2. Opens an `mcp.ClientSession` over stdio to discover available tools
3. Passes those tools (converted to Anthropic format) to `claude-opus-4-6` via the `anthropic` SDK
4. Runs a standard tool-use agentic loop: sends tool results back until `stop_reason == "end_turn"`

**Tool format conversion**: MCP tools (`tool.name`, `tool.description`, `tool.inputSchema`) map directly to the Anthropic `tools` array (`name`, `description`, `input_schema`).

**Adding tools**: Add new `mcp.types.Tool` entries in `mcp_server.py`'s `list_tools()` handler and a matching branch in `call_tool()`. The client picks them up automatically on the next run.
