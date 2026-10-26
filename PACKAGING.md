# Packaging Rainbrand plugins

This document is for repository maintainers. Customer installation guidance
lives in `README.md`.

## Canonical sources

- `skills/rainbrand/SKILL.md` owns the Rainbrand package name, version,
  description, license, author, and documentation URL.
- `compatibility/bloom.md` independently owns those fields and guidance for
  the legacy Bloom download. It is outside Skill discovery; the builder maps
  its unchanged bytes to `bloom/SKILL.md` in `bloom.skill.zip`.
- `plugin-copy.json` owns provider listing, review, and publication copy.
- `plugin-config.json` owns the Rainbrand MCP server name and endpoint.

Run the renderer after changing any canonical source:

```bash
python3 scripts/render-plugin-manifests.py --write
```

The renderer writes fully expanded provider manifests and MCP configurations.
The generated JSON must contain literal values because plugin clients do not
resolve repository variables.

Generated MCP files keep portable and native connection formats separate:

| Output | Used by | Contract |
| --- | --- | --- |
| `.codex-plugin/.mcp.json` | Codex and ChatGPT package source | Codex compatibility shape; packaged as root `.mcp.json` |
| `.mcp.json` | Claude and Cursor repository installs | Native shape; the remote server entry contains `type: "http"` and `url` |
| `mcp.json` | Portable Agent Plugins clients | Portable schema with `type: "streamable-http"` and `url` |

The Codex archive maps `.codex-plugin/.mcp.json` to root `.mcp.json`. All three
generated files get their server name and endpoint from `plugin-config.json`;
none is an independent source of truth.

Cursor's repository manifest explicitly reads `./.mcp.json`. Its generated
`archive-plugin.json` retains the ZIP's original `./mcp.json` reference; the
builder maps that manifest and the native MCP file to their existing archive
paths. This preserves the submitted Cursor ZIP byte-for-byte without asking a
native loader to interpret the portable configuration.

The committed `claude/` directory is the source folder submitted to Anthropic's
plugin directory. It contains the runtime and listing files from the Claude
archive, including the native MCP configuration at `claude/.mcp.json`, but
omits the release-only changelog. The Claude package builder refreshes this
projection, and validation rejects drift or extra files. In Anthropic's
developer portal, submit this repository with the plugin path `claude` so its
scanner only reads the Claude bundle.

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

## Portable Agent Plugins package

The repository root is the plugin root for clients and registries that accept
[Agent Plugins 1.0](https://agent-plugins.org/specification). Submit that root
at a reviewed commit. Check each registry's intake requirements before
submitting; publishing these files does not imply a public listing.

The existing renderer generates `plugin.json` and portable `mcp.json` from the
same identity, listing metadata, and endpoint as the native packages. Run
`scripts/validate-portable-plugin.sh` to check their contracts and freshness.
Only the Rainbrand Skill lives under `skills/`, so portable discovery does not
offer the legacy Bloom Skill. The native archives and Anthropic's submitted
`claude/` directory retain their existing contents. No portable ZIP is added
to the five release assets.

## Legacy Bloom download

Keep `compatibility/bloom.md` as ordinary packaging input, not a discoverable
`SKILL.md`. The builder maps its unchanged bytes into `bloom.skill.zip` as
`bloom/SKILL.md`. Its version is independent of Rainbrand's version. Keep this
ZIP and its existing release download URLs available while legacy support
continues, without adding it to customer-facing install instructions or new
plugin catalogs. Previously indexed third-party listings need separate cleanup.

## Claude Code marketplace

The renderer also generates `.claude-plugin/marketplace.json`. Its Rainbrand
entry points to `./claude`, the same directory used for Anthropic's submission.
The marketplace file stays outside the submitted directory and release ZIPs.

After this change is merged, install through the repository's marketplace:

```bash
claude plugin marketplace add rainbrandai/rainbrand-skills
claude plugin install rainbrand@rainbrand
```

For local validation before merging:

```bash
claude plugin validate .
claude plugin validate ./claude
```

The catalog provides direct installation from this repository. Anthropic's
directory submission and approval are separate. See the
[Claude marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference).
