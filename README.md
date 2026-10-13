# Rainbrand Skill and Agent Plugin

Rainbrand is the brand layer for agents. It turns a brand's identity, guidance,
and assets into shared context that agents and products can use and update as
the brand evolves, alongside the tools where it is created and managed.

This repository maintains one optional Agent Skill and packages it with
Rainbrand's remote Model Context Protocol (MCP) connection in two formats:
a portable [Agent Plugins 1.0](https://agent-plugins.org/specification) plugin
and a separate Claude-native plugin. All use the identifier `rainbrand` and
the same canonical Skill.

The Rainbrand Skill teaches an agent when and how to use Rainbrand. A Brand
Skill contains the context for one particular brand. Installing the standalone
Skill supplies guidance; the plugin also declares the MCP connection. The
client handles authentication.

## Install

Choose the archive for your installation flow before downloading:

| Installation flow | Archive | MCP connection |
| --- | --- | --- |
| Claude native plugin upload | `rainbrand.claude-plugin.zip` (introduced in v1.1.8) | Bundled in `.mcp.json`; connect and authorize Rainbrand. |
| ChatGPT workspace plugin upload or Agent Plugins 1.0 client | `rainbrand.plugin.zip` | Bundled in `mcp.json`; authorize Rainbrand. |
| Standalone Skill installation, including Claude's Skill upload | `rainbrand.skill.zip` | Configure MCP separately. |

The portable `rainbrand.plugin.zip` is incompatible with Claude's native
plugin upload. Skill upload and plugin upload are separate flows.

### Claude native plugin upload

Download the [v1.1.8 Claude-native plugin ZIP](https://github.com/trybloomai/rainbrand-skills/releases/download/v1.1.8/rainbrand.claude-plugin.zip)
once that release is published, or build
[dist/rainbrand.claude-plugin.zip](dist/rainbrand.claude-plugin.zip) using the
commands below while publication is pending.

1. In Claude, open **Customize → Plugins → Add → Upload plugin**.
2. Upload `rainbrand.claude-plugin.zip`.
3. Open the plugin's **Connectors** tab, connect Rainbrand, and complete OAuth sign-in.
4. In a fresh chat, confirm the Rainbrand Skill is available and discover the connected tools.

The native archive contains exactly these files at its root, with no wrapper
directory or nested ZIPs:

```text
.claude-plugin/plugin.json
.mcp.json
skills/rainbrand/SKILL.md
README.md
CHANGELOG.md
LICENSE
assets/rainbrand-logo.png
```

The adapter declares the same hosted MCP endpoint with Claude's `http`
transport. Its Skill is copied directly from the canonical source; it adds no
separate guidance or tool behavior. The manifest's `icon` points to the bundled
Rainbrand image. A v1.1.8 candidate successfully uploaded to Claude and appeared
as Rainbrand with one Skill and one Connector, as reported by a live tester.
That candidate omitted the image. Re-upload the final package to confirm the
icon, OAuth sign-in, and tool discovery; those checks remain pending.

### ChatGPT workspace upload

Download the [portable Rainbrand plugin ZIP](https://github.com/trybloomai/rainbrand-skills/releases/latest/download/rainbrand.plugin.zip).
It bundles the Rainbrand Skill, MCP connection, and icon. In ChatGPT on the web:

1. Open the workspace **Admin Console**.
2. Go to **Plugins → Add → Upload plugin**.
3. Upload `rainbrand.plugin.zip` and configure workspace access.
4. Authorize the Rainbrand connection when prompted.

### Standalone Skill

From this checkout, install the Skill in the current project:

```bash
npx skills add . --skill rainbrand
```

Prefer a project installation so the guidance is reviewable with the project.

Alternatively, download the latest [Rainbrand Skill ZIP](https://github.com/trybloomai/rainbrand-skills/releases/latest/download/rainbrand.skill.zip)
and upload it through Claude's Skill upload flow. It contains the canonical
Skill as `rainbrand/SKILL.md`; configure the MCP connection separately.

### Portable plugin

Extract the local [dist/rainbrand.plugin.zip](dist/rainbrand.plugin.zip) and
use the extracted contents as the plugin directory. Load it in a client
that supports Agent Plugins 1.0 and Streamable HTTP, then follow the client's
OAuth sign-in flow.

The archive contains these files directly at its root:

```text
plugin.json
mcp.json
assets/rainbrand-logo.png
skills/rainbrand/SKILL.md
README.md
CHANGELOG.md
LICENSE
```

Both manifests declare the Agent Plugins `1.0.0` schemas. `mcp.json` defines
one server named `rainbrand` with transport `streamable-http` and endpoint
`https://mcp.rainbrand.com/mcp`. The package contains no credentials.
`assets/rainbrand-logo.png` is the final Rainbrand icon, used for both the
OpenAI listing logo and composer icon.

## Connect Rainbrand

For interactive work, connect `https://mcp.rainbrand.com/mcp` in an MCP client
that supports Streamable HTTP and OAuth. A portable plugin client reads that
connection from `mcp.json`; Claude reads `.mcp.json`. A standalone Skill
installation needs it configured separately.
Complete Rainbrand sign-in, then let the client discover the live tools and
their schemas. The live tool list determines what the connected account can use.

The Skill is packaged before the consuming account is known. It provides stable
guidance for discovery and brand work; the connected account's live tools,
descriptions, and schemas define the available capabilities and how to use them.
The package does not infer an account or contain account-specific workflows.

For product information, support, and API integration guidance, use the
[Rainbrand website](https://www.rainbrand.com/) and
[FAQ](https://www.rainbrand.com/faq/). Before building an application or backend
integration, obtain a current, verified Rainbrand API contract. Keep API keys
in the application's secret store.

## Provider compatibility

Use the installation path supported by your client. Package validation checks
the archive; test authentication and tool use in the target client as well.

| Provider | Installation path | Compatibility notes |
| --- | --- | --- |
| OpenAI | Upload the plugin ZIP through the ChatGPT workspace Admin Console, then authorize Rainbrand. | Requires an eligible workspace and upload permission. Public-directory publication is a separate, optional process. |
| Claude | Upload `rainbrand.claude-plugin.zip` through native plugin upload, then connect Rainbrand; or upload `rainbrand.skill.zip` through Skill upload and configure MCP separately. | Candidate upload passed with one Skill and one Connector. Final-package icon, OAuth, and tool discovery confirmation remains pending. Never use the portable ZIP for native upload. |
| Cursor | Test the portable plugin ZIP's extracted Agent Plugins manifest. | Verify installation and tool use in Cursor. Marketplace publication is a separate process. |

OpenAI documents workspace installation in
[Plugin management](https://learn.chatgpt.com/docs/enterprise/plugin-management)
and the portable format in
[Build plugins](https://developers.openai.com/plugins/build/plugins).

Claude's native format requires `.claude-plugin/plugin.json` and root
`.mcp.json` with transport `http`. The separate native archive includes those
files and the canonical Skill. The portable archive keeps its Agent Plugins
layout and excludes the native adapter. Use the built native ZIP for upload;
zipping the entire checkout would include nested distribution ZIPs.
See [Claude plugin requirements](https://claude.com/docs/plugins/build), the
[pre-submission checklist](https://claude.com/docs/plugins/pre-submission-checklist),
and [directory publishing](https://claude.com/docs/directory/publish).

Cursor recognizes the root `plugin.json`; a separate `.cursor-plugin/plugin.json`
manifest is not required for this format. See
[Cursor plugins](https://cursor.com/docs/reference/plugins) and
[marketplace submission](https://cursor.com/marketplace/publish).

## Update or remove

```bash
npx skills update rainbrand
npx skills remove rainbrand
```

Add `--global` for a global installation.

## Package and validate

The canonical source is `skills/rainbrand/SKILL.md` in this public repository.
The builders generate `rainbrand.skill.zip`, `rainbrand.plugin.zip`, and
`rainbrand.claude-plugin.zip` from that source; each archive must contain the
exact same Skill bytes. Do not edit an archive's copy independently. Build all
three archives and validate them in this order:

```bash
scripts/package-skill.sh
scripts/package-plugin.sh
scripts/package-claude-plugin.sh
scripts/validate-plugin.sh
scripts/validate-claude-plugin.sh
claude plugin validate .
```

Pass a ZIP path to the appropriate `validate-plugin.sh` or
`validate-claude-plugin.sh` script to validate another local copy against this
checkout. Claude Code is required only for `claude plugin validate .`; the
repository's package scripts run offline. Check OpenAI submission readiness
separately:

```bash
scripts/validate-plugin.sh --submission
```

Submission readiness checks the additional metadata required for a directory
submission. It is not required for workspace ZIP upload and does not replace
client testing or provider review.

The scripts run offline with Bash 3.2 or later, POSIX `awk`, `zip`, Info-ZIP
`unzip` (including `-Z`), and standard shell utilities. They require no package
manager or additional language runtime.

Validation checks JSON types, duplicate and unsupported fields, schema
identifiers, matching names, the exact MCP endpoint, and OpenAI metadata. The
versions of both plugins, the Skill, and latest numbered changelog release must
agree. The native manifest must reference the bundled Rainbrand icon.
Archive checks cover integrity, exact members, regular file types, and
byte-for-byte agreement with source files, including the Skill and native icon.
All three builders fix timestamps and file modes so unchanged sources produce
identical archives with the same ZIP
tool version, including across time zones and umasks.

For packaging changes, run the optional regression suite:

```bash
python3 scripts/test-validation.py
```

These tests exercise malformed portable and native metadata and MCP configs,
unsafe or mismatched archives, missing or altered icons, submission gates, and
reproducible builds. Python 3 is required only for this test suite, not for
package building or validation.

## License

[MIT](LICENSE)
