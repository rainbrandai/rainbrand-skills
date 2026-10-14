# Rainbrand Skill and plugins

Rainbrand is the brand layer for agents. It turns a brand's identity, guidance,
and assets into shared context that agents and products can use and update.

This repository maintains one canonical Skill at
[`skills/rainbrand/SKILL.md`](skills/rainbrand/SKILL.md). The release builders
copy those exact bytes into provider-native Claude, Codex/OpenAI, and Cursor
packages. Each plugin connects to `https://mcp.rainbrand.com/mcp`; the client
handles OAuth sign-in and discovers the tools available to the connected
account.

## Install

### Claude

Download [`rainbrand.claude-plugin.zip`](dist/rainbrand.claude-plugin.zip). In
Claude, open **Customize → Plugins → Add → Upload plugin**, upload the archive,
then connect Rainbrand from the plugin's Connectors tab.

### Codex

Use [`rainbrand.codex-plugin.zip`](dist/rainbrand.codex-plugin.zip) for Codex
plugin testing or OpenAI directory submission. Until Rainbrand has a verified
public listing, install it only through an approved local, workspace, or review
flow and authorize Rainbrand when prompted.

### ChatGPT Work

Workspace admins and reviewers use the same
[`rainbrand.codex-plugin.zip`](dist/rainbrand.codex-plugin.zip). Upload it
through the workspace's enabled plugin upload flow, install it, and authorize
Rainbrand. Unpublished workspace imports that declare MCP are currently
desktop-only; Rainbrand does not claim a public ChatGPT or Codex directory
listing.

### Cursor

Download [`rainbrand.cursor-plugin.zip`](dist/rainbrand.cursor-plugin.zip) and
extract it to `~/.cursor/plugins/local/rainbrand`. Restart Cursor or run
**Developer: Reload Window**, then confirm Rainbrand under **Customize** and
complete MCP authorization.

### Direct MCP or standalone Skill

In any compatible MCP client, connect directly to
`https://mcp.rainbrand.com/mcp` and complete OAuth sign-in.

To install only the canonical Skill from this checkout:

```bash
npx skills add . --skill rainbrand
```

The standalone archives are [`rainbrand.skill.zip`](dist/rainbrand.skill.zip)
and the generated Bloom compatibility archive
[`bloom.skill.zip`](dist/bloom.skill.zip). A standalone Skill does not configure
the MCP connection.

## Package and validate

Shared name, version, and description come from the canonical Skill
frontmatter. All other provider listing and review copy lives in
[`plugin-copy.json`](plugin-copy.json). After editing either source, regenerate
the checked-in provider manifests directly with:

```bash
python3 scripts/render-plugin-manifests.py --write
```

The package commands run this renderer automatically before validation and
write fully expanded JSON manifests into each archive.

Build every release asset and run all archive validators:

```bash
scripts/package-release.sh
```

Run the packaging regression suite:

```bash
python3 scripts/test-validation.py
```

The release contains exactly these files:

```text
rainbrand.codex-plugin.zip
rainbrand.claude-plugin.zip
rainbrand.cursor-plugin.zip
rainbrand.skill.zip
bloom.skill.zip
```

Builds are deterministic. Validation checks provider manifest contracts,
submission metadata, the exact MCP endpoint, branding, exact archive members,
regular file types, canonical Skill and asset byte parity, and reproducibility
across time zones and umasks.

For current platform behavior, see the official
[OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins),
[ChatGPT workspace plugin management](https://learn.chatgpt.com/docs/enterprise/plugin-management),
[Claude plugin](https://claude.com/docs/plugins/build), and
[Cursor plugin](https://cursor.com/docs/reference/plugins) documentation.
Rainbrand product and integration documentation is available on the
[Rainbrand website](https://www.rainbrand.com/),
[FAQ](https://www.rainbrand.com/faq/), and
[MCP guide](https://docs.rainbrand.com/mcp/getting-started).

## License

[MIT](LICENSE)
