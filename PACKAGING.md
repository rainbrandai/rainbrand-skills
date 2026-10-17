# Packaging Rainbrand plugins

This document is for repository maintainers. Customer installation guidance
lives in `README.md`.

## Canonical sources

- `skills/rainbrand/SKILL.md` owns the Rainbrand package name, version,
  description, license, author, and documentation URL.
- `skills/bloom/SKILL.md` independently owns those fields and guidance for the
  standalone Bloom compatibility Skill.
- `plugin-copy.json` owns provider listing, review, and publication copy.
- `plugin-config.json` owns the Rainbrand MCP server name and endpoint.

Run the renderer after changing any canonical source:

```bash
python3 scripts/render-plugin-manifests.py --write
```

The renderer writes fully expanded provider manifests and MCP configurations.
The generated JSON must contain literal values because plugin clients do not
resolve repository variables.

Three generated MCP files are required because the provider contracts differ:

| Output | Used by | Contract |
| --- | --- | --- |
| `.codex-plugin/.mcp.json` | Codex and ChatGPT package source | Codex compatibility shape; packaged as root `.mcp.json` |
| `.mcp.json` | Claude | Native shape; the remote server entry contains `type: "http"` and `url` |
| `mcp.json` | Cursor | Native shape; the remote server entry contains `type: "http"` and `url` |

The Codex archive maps `.codex-plugin/.mcp.json` to root `.mcp.json`. All three
generated files get their server name and endpoint from `plugin-config.json`;
none is an independent source of truth.

The committed `claude/` directory is the source folder submitted to Anthropic's
plugin directory. It contains the same files and bytes as the Claude archive,
including the native MCP configuration at `claude/.mcp.json`. The Claude
package builder refreshes this projection, and validation rejects drift or
extra files. In Anthropic's developer portal, submit this repository with the
plugin path `claude` so its scanner only reads the Claude bundle.

## Build and validate

Build all release assets and run their validators:

```bash
scripts/package-release.sh
```

Run the regression suite:

```bash
python3 scripts/test-validation.py
```

The expected release assets are:

```text
rainbrand.codex-plugin.zip
rainbrand.claude-plugin.zip
rainbrand.cursor-plugin.zip
rainbrand.skill.zip
bloom.skill.zip
```

Builds are deterministic. Validation checks generated-file freshness, provider
manifest contracts, submission metadata, MCP parity, branding, exact archive
members, regular file types, source Skill and asset byte parity, and
reproducibility across time zones and umasks.

Provider references:

- [OpenAI plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [Claude plugins](https://claude.com/docs/plugins/build)
- [Cursor plugins](https://cursor.com/docs/reference/plugins)
