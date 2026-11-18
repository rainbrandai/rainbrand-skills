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
| `gemini-extension.json` | Gemini CLI repository installs | Native extension with `httpUrl` and OAuth discovery |

The Codex archive maps `.codex-plugin/.mcp.json` to root `.mcp.json`. All
generated connection files get their server name and endpoint from `plugin-config.json`;
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
python3 packages/pi/test_pack.py
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

Release validation also builds and inspects the Pi tarball in a temporary
directory. Install Python 3.9 or later, Node.js 22.19 or later, and pnpm
10.34.7 for the Pi checks. The package has no runtime npm dependencies.

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

## Gemini CLI extension

The renderer generates root `gemini-extension.json` using the Skill's name and
version, the existing short listing description in `plugin-copy.json`, and the
MCP endpoint in `plugin-config.json`. Gemini CLI discovers the existing
`skills/rainbrand/SKILL.md` through the extension's `skills/` directory. There
is no separate Skill copy or Gemini ZIP. Installation and OAuth steps are in
[the Gemini CLI guide](docs/gemini-cli.md).

Before enabling gallery discovery, verify installation and OAuth on a client,
then publish a stable repository release containing this manifest. The older
v1.1.13 release predates the manifest: the unqualified Gemini install command
prefers GitHub's latest release, so merging a manifest into main alone does not
make that command work. Do not replace or retag an existing release. Follow the
normal version/render/package process for the next stable release, keeping the
manifest version and release tag aligned. Until then, install from `--ref=main`.

After a working release is public, add the `gemini-cli-extension` repository
topic. The [gallery crawler](https://geminicli.com/docs/extensions/releasing/)
uses that topic and the root manifest; publication is only complete once a
public gallery entry and its install command have been verified.

## Pi package

Build the Pi distribution with pnpm through its staging wrapper.

```bash
python3 packages/pi/pack.py .context/pi-artifacts
python3 packages/pi/test_pack.py
```

`packages/pi/package.template.json` owns the npm name
`@rainbrand-ai/pi-plugin`, catalog keyword, and Pi resource paths. The npm
organization is `rainbrand-ai`. GitHub sources remain under
`rainbrandai/rainbrand-skills`.

The wrapper reuses the canonical renderer's metadata parser to populate the
version, description, author, and license directly from
`skills/rainbrand/SKILL.md`. It renders Pi's URL-only MCP configuration from
`plugin-config.json`. Version changes take effect on the next pack.

Each invocation creates an isolated temporary package directory, copies the
canonical Skill and license, adds the extension and package README, and runs
`pnpm pack`. It verifies exactly six regular files and their contents before
atomically placing the tarball in the requested output directory. Temporary
staging is removed on success and exceptions. Concurrent builds use separate
staging directories. The tracked package source contains a manifest template
and the pack entry point. Use the wrapper to create the installable package.

The release validator exercises that same pack path. The regression tests
cover native registration, compatibility warnings, canonical updates, scope
changes, exact contents, failure cleanup, concurrent packs, and deterministic
bytes across time zones and umasks. The existing five GitHub ZIP release
assets retain their established release process.

Complete the isolated install and OAuth smoke test described in
[the Pi verification guide](docs/pi.md). Tomas reviews the PR before npm
publication. After Tomas's review, explicit publication approval, and merge,
build from the reviewed release and publish the inspected tarball using pnpm
from an authenticated `rainbrand-ai` publisher environment.

```bash
pi_tarball="$(python3 packages/pi/pack.py .context/pi-artifacts)"
pnpm publish "$pi_tarball" --access public
```

After publication, verify the versioned npm install and the public Pi catalog
entry, then record their URLs and verification date in
[the distribution issue](https://github.com/rainbrandai/hero/issues/3542).
The `pi-package` keyword makes a published package eligible for indexing.
Public catalog visibility requires a separate check.

Packaging references checked on November 18, 2026 include
[Pi packages](https://docs.pi.dev/latest/packages),
[Pi extensions](https://docs.pi.dev/latest/extensions#mcp-servers),
[Pi native MCP and OAuth](https://docs.pi.dev/latest/mcp), and
[Postman's installer staging](https://github.com/postmanlabs/postman-plugin/tree/main/installer).
Pi's native MCP support first shipped in
[0.99.0](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/CHANGELOG.md#0990---2026-09-29).

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
