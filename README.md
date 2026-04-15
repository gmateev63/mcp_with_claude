# mcp_with_claude
Build MCP Server with Claude code

1. Install dependencies
*pip install -r requirements.txt*
2. Set your Anthropic API key

#####     Windows CMD
​    *set ANTHROPIC_API_KEY=sk-ant-...*

#####     Windows PowerShell
​    *$env:ANTHROPIC_API_KEY="sk-ant-..."*

#####     Git Bash / WSL
​    *export ANTHROPIC_API_KEY=sk-ant-...*

3. Get your key at https://console.anthropic.com → API Keys.
4. Run it
*python app.py*

That's it — app.py starts mcp_server.py automatically in the background.