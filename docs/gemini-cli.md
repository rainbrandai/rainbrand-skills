# Rainbrand in Gemini CLI

Rainbrand is the brand layer for agents. This extension includes the Rainbrand
Skill and a connection to Rainbrand's hosted MCP server.

Install from the repository's main branch:

```bash
gemini extensions install https://github.com/rainbrandai/rainbrand-skills --ref=main
```

Review the extension permissions, then restart Gemini CLI. In its interactive
session, sign in to your Rainbrand account:

```text
/mcp auth rainbrand
```

Complete authorization in your browser. Use `/mcp list` to inspect the connection
and available tools, and `/skills list` to see the Rainbrand Skill.

You can then ask:

```text
Show me the brands I can access in Rainbrand.
```

The extension connects to `https://mcp.rainbrand.com/mcp` using Streamable HTTP
and OAuth discovery. No API key or shared client secret is included in the
extension.

For account setup and Rainbrand usage, see the
[MCP getting-started guide](https://docs.rainbrand.com/mcp/getting-started).

To remove the extension:

```bash
gemini extensions uninstall rainbrand
```
