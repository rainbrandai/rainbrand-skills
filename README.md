# Rainbrand Plugins and Skill

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

To get started, [connect Rainbrand MCP directly](#connect-rainbrand). You do not
need to install a standalone Skill to connect.

When Rainbrand is available as a plugin in your client, it packages the
Rainbrand Skill with the MCP connector/reference. Installing a plugin does not
connect or authorize your Rainbrand account; complete connector setup and
OAuth sign-in separately.

Choose the installation path supported by your client and account:

| Client or installation flow | Installation path |
| --- | --- |
| Claude with plugin support | Use the Claude-native Rainbrand plugin. If you have a plugin ZIP for upload, use `rainbrand.claude-plugin.zip`. |
| ChatGPT with plugin support | Install Rainbrand from the Plugins Directory when it is listed. ZIP upload/import is for publishers, testers, or eligible workspace admins. |
| Other clients, or clients/accounts without plugin support | Connect Rainbrand MCP directly in a compatible client. No ZIP is required. |
| Skill-capable clients without plugins, or an existing separate MCP setup | Optionally add `rainbrand.skill.zip` for guidance. MCP must be configured separately. |

The Claude-native and portable/OpenAI archives are **not interchangeable**.
`rainbrand.claude-plugin.zip` is for Claude native plugin upload.
`rainbrand.plugin.zip` is the portable/OpenAI package. Skill upload is a
separate, optional flow.

### Claude: native Rainbrand plugin

For Claude native plugin upload, use `rainbrand.claude-plugin.zip` from the
[Rainbrand releases](https://github.com/trybloomai/rainbrand-skills/releases)
when available. It includes the Rainbrand Skill and connector configuration.

1. In Claude, open **Customize → Plugins → Add → Upload plugin**.
2. Upload `rainbrand.claude-plugin.zip`.
3. Open the plugin's **Connectors** tab, connect Rainbrand, and complete OAuth sign-in.
4. Start a fresh chat to use Rainbrand's connected tools.

### ChatGPT: Plugins Directory

When Rainbrand is listed in the **Plugins Directory**, find it and install it.
Complete the Rainbrand connection and OAuth sign-in when prompted, then start
a fresh conversation. Follow the listing's supported surfaces and account
requirements. See OpenAI's [plugin installation guidance](https://learn.chatgpt.com/docs/plugins).

The portable/OpenAI `rainbrand.plugin.zip` is for publisher submission, testing,
or upload/import by an eligible workspace admin. Import does not grant access
to Rainbrand or connect workspace members' accounts.

OpenAI documents imported plugins with MCP configuration as **Desktop-only**,
including remote HTTPS servers. This restriction applies to this package's
import path. Directory installation is a separate path; follow its listing for
supported surfaces. See [Plugin management](https://learn.chatgpt.com/docs/enterprise/plugin-management#desktop-only-plugins).

### Standalone Skill: optional advanced fallback

Use the standalone Skill only when the client supports Skills but not plugins,
or when MCP is already configured separately. It adds guidance; it does not
install a connector or authorize an account. It is not required to connect
Rainbrand MCP.

From this checkout, install it in the current project:

```bash
npx skills add . --skill rainbrand
```

Prefer a project installation so the guidance is reviewable with the project.
Alternatively, download the [Rainbrand Skill ZIP](https://github.com/trybloomai/rainbrand-skills/releases/latest/download/rainbrand.skill.zip)
and use the client's Skill upload flow. It contains `rainbrand/SKILL.md`;
configure MCP separately if it is not already connected.

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

## Distribution formats

All three distributions reuse the canonical Skill and hosted MCP endpoint.
There are no credentials or account-specific workflows in the packages.

### Claude-native ZIP: `rainbrand.claude-plugin.zip`

The archive contains exactly these files at its root:

```text
.claude-plugin/plugin.json
.mcp.json
skills/rainbrand/SKILL.md
README.md
CHANGELOG.md
LICENSE
assets/rainbrand-logo.png
```

The native manifest references `./assets/rainbrand-logo.png` through `icon`.
Root `.mcp.json` uses transport `http` and endpoint
`https://mcp.rainbrand.com/mcp`. The adapter adds no separate Skill guidance or
tool behavior. Use the built ZIP for native upload; zipping the checkout would
include nested distribution ZIPs. See [Claude plugin requirements](https://claude.com/docs/plugins/build)
and [manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference).

### Portable/OpenAI ZIP: `rainbrand.plugin.zip`

The archive contains exactly these files at its root:

```text
plugin.json
mcp.json
skills/rainbrand/SKILL.md
README.md
CHANGELOG.md
LICENSE
assets/rainbrand-logo.png
```

Both manifests declare the Agent Plugins `1.0.0` schemas. `mcp.json` defines
one server named `rainbrand`, transport `streamable-http`, and endpoint
`https://mcp.rainbrand.com/mcp`. The Rainbrand image is used for the OpenAI
listing logo and composer icon. The archive excludes the Claude-native adapter.
See OpenAI's [package guide](https://developers.openai.com/plugins/build/plugins).

For testing an Agent Plugins 1.0 client, extract this ZIP and use its contents
as the plugin directory. Other clients should use direct MCP for onboarding
unless their plugin path has been validated. Client support is not established
by the portable manifest alone.

### Standalone Skill ZIP: `rainbrand.skill.zip`

Contains only `rainbrand/SKILL.md`. It supplies optional guidance and requires
a separately configured MCP connection for connected work.

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
identical archives with the same ZIP tool version, including across time zones and umasks.

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
