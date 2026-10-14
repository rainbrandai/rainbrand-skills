# Rainbrand

Rainbrand is the brand layer for agents. It turns a brand's identity, guidance,
and assets into shared context that agents and products can use and update.

Connect Rainbrand to give Claude, Codex, ChatGPT, and Cursor access to your
brand context and the Rainbrand tools available to your account.

## Install

### Claude

Download [`rainbrand.claude-plugin.zip`](dist/rainbrand.claude-plugin.zip). In
Claude, open **Customize → Plugins → Add → Upload plugin**, upload the archive,
then connect Rainbrand from the plugin's Connectors tab.

### Codex

Download [`rainbrand.codex-plugin.zip`](dist/rainbrand.codex-plugin.zip). Add
the plugin in Codex, then authorize Rainbrand when prompted.

### ChatGPT Work

If your workspace allows custom plugins, ask a workspace admin to upload
[`rainbrand.codex-plugin.zip`](dist/rainbrand.codex-plugin.zip). Install
Rainbrand from your workspace's plugins and complete authorization.

### Cursor

Download [`rainbrand.cursor-plugin.zip`](dist/rainbrand.cursor-plugin.zip) and
extract it to `~/.cursor/plugins/local/rainbrand`. Restart Cursor or run
**Developer: Reload Window**, then confirm Rainbrand under **Customize** and
complete MCP authorization.

### Other MCP clients

In any compatible MCP client, connect directly to
`https://mcp.rainbrand.com/mcp` and complete OAuth sign-in.

### Standalone Skill

To install the Rainbrand Skill without the MCP connection:

```bash
npx skills add trybloomai/rainbrand-skills --skill rainbrand
```

You can also download [`rainbrand.skill.zip`](dist/rainbrand.skill.zip).

Learn more on the [Rainbrand website](https://www.rainbrand.com/), read the
[FAQ](https://www.rainbrand.com/faq/), or see the
[MCP guide](https://docs.rainbrand.com/mcp/getting-started).

## License

[MIT](LICENSE)
