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

**Current quickstart: connect Rainbrand MCP directly.** Provider-specific plugin
release checks are still pending. Use the [direct MCP connection](#connect-rainbrand)
while those checks are completed; the public MCP quickstart remains
MCP-first until the artifacts are releasable and tested.

For launch, prefer the Rainbrand plugin wherever the client and account support
it: the plugin packages the Rainbrand Skill with the MCP connector/reference.
Plugin installation does not connect or authorize your Rainbrand account.
Complete the client's connector setup and OAuth sign-in separately.

The following launch paths become customer recommendations only after the
[provider release gates](#provider-release-gates) pass. Choose the provider and
installation flow before downloading an archive.

| Client or installation flow | Launch recommendation | Package for testing or fallback |
| --- | --- | --- |
| Claude with plugin support | Install the Claude-native Rainbrand plugin, then connect its bundled connector. | Pre-directory testers can upload `rainbrand.claude-plugin.zip`. |
| ChatGPT with plugin support | Install Rainbrand from the Plugins Directory once published, then connect/authenticate when prompted. | `rainbrand.plugin.zip` is the portable/OpenAI package for publishers, testers, or eligible workspace admins. |
| Other clients, or clients/accounts without plugin support | Connect Rainbrand MCP directly in a compatible client. | No ZIP is required. |
| Skill-capable clients without plugins, or an existing separate MCP setup | Optionally add the standalone Skill as an advanced fallback. | `rainbrand.skill.zip` supplies guidance only. |

The Claude-native and portable/OpenAI archives are **not interchangeable**.
Do not upload `rainbrand.plugin.zip` through Claude's native plugin flow, or
use `rainbrand.claude-plugin.zip` as the portable/OpenAI package. Skill upload
is a separate, optional flow.

### Claude: native Rainbrand plugin

Once the Claude release gates pass, recommend the Claude-native Rainbrand
plugin. For pre-directory testing, build
[dist/rainbrand.claude-plugin.zip](dist/rainbrand.claude-plugin.zip) with the
commands below. The [v1.1.8 Claude-native ZIP](https://github.com/trybloomai/rainbrand-skills/releases/download/v1.1.8/rainbrand.claude-plugin.zip)
will be available after authorized publication.

1. In Claude, open **Customize → Plugins → Add → Upload plugin**.
2. Upload `rainbrand.claude-plugin.zip`.
3. Open the plugin's **Connectors** tab, connect Rainbrand, and complete OAuth sign-in.
4. In a fresh chat, confirm the Rainbrand Skill is available and discover the connected tools.

A live tester reports that a v1.1.8 candidate uploaded successfully as Rainbrand
with exactly one Skill and one Connector. That candidate omitted the image.
The corrected package includes it, but visual icon confirmation, OAuth, tool
discovery, and exact supported surfaces and account requirements remain pending.

### ChatGPT: Plugins Directory

Once Rainbrand is published and the ChatGPT release gates pass, open the
**Plugins Directory**, find Rainbrand, and install it. Complete the Rainbrand
connection and OAuth sign-in when prompted, then start a fresh conversation
and confirm tool discovery. See OpenAI's [plugin installation guidance](https://learn.chatgpt.com/docs/plugins).

ZIP upload/import is a publisher, tester, or eligible workspace-admin path.
It is not the ordinary customer installation path. Directory installation and
workspace import need separate verification; do not infer one path's supported
surfaces from another.

For package testing or submission, build
[dist/rainbrand.plugin.zip](dist/rainbrand.plugin.zip). The
[v1.1.8 portable/OpenAI ZIP](https://github.com/trybloomai/rainbrand-skills/releases/download/v1.1.8/rainbrand.plugin.zip)
will be available after authorized publication. Use the upload/import flow
available to the testing account or workspace. Workspace management requires
an eligible workspace admin, appropriate access policies, and permission to
use the Rainbrand connection; import does not grant account access.

OpenAI currently documents imported plugins that declare MCP configuration as
**Desktop-only**, including remote HTTPS servers. This portable package
contains `mcp.json`, so test imported use in the ChatGPT desktop app. Do not
assume it works on web or mobile. The exact Rainbrand directory release path,
supported surfaces, and account/workspace requirements must be verified before
launch guidance promises them. See [Plugin management](https://learn.chatgpt.com/docs/enterprise/plugin-management#desktop-only-plugins).

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

## Provider release gates

Before public onboarding switches to plugin-first, validate the Claude-native
and portable/OpenAI artifacts independently, using each intended release and
installation path. For each provider, record:

- Successful package validation and installation of the exact artifact.
- Correct Rainbrand name and visually confirmed Rainbrand icon.
- MCP connection and successful OAuth sign-in after installation.
- Connected-tool discovery in a fresh conversation.
- Exact supported surfaces and account/workspace requirements.

Local validation proves package structure and source parity. It does not prove
client behavior, directory availability, account eligibility, or OAuth access.
Claude's earlier candidate upload passed; the remaining checks must use the
final package. The ChatGPT directory and restricted upload/import paths require
independent live verification. Until these gates pass, use direct MCP as the
current quickstart and keep standalone Skill installation optional.

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
