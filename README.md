# Rainbrand Skill and Agent Plugin

Rainbrand is the brand layer for agents. It turns a brand's identity, guidance,
and assets into shared context that agents and products can use and update as
the brand evolves, alongside the tools where it is created and managed.

This repository maintains one optional Agent Skill and packages it with
Rainbrand's remote Model Context Protocol (MCP) connection as an
[Agent Plugins 1.0](https://agent-plugins.org/specification) plugin. Both use
the identifier `rainbrand`.

The Rainbrand Skill teaches an agent when and how to use Rainbrand. A Brand
Skill contains the context for one particular brand. Installing the standalone
Skill supplies guidance; the plugin also declares the MCP connection. The
client handles authentication.

## Install

Download the latest [Rainbrand plugin ZIP](https://github.com/trybloomai/rainbrand-skills/releases/latest/download/rainbrand.plugin.zip).
It bundles the Rainbrand Skill, MCP connection, and icon.

### ChatGPT workspace upload

In ChatGPT on the web:

1. Open the workspace **Admin Console**.
2. Go to **Plugins → Add → Upload plugin**.
3. Upload `rainbrand.plugin.zip` and configure workspace access.
4. Authorize the Rainbrand connection when prompted.

You need an eligible workspace and permission to upload plugins, typically as
a workspace owner or admin. This path does not require a marketplace or an
OpenAI public-directory submission. To update the plugin, download the latest
ZIP and upload it again. See [OpenAI plugin management](https://learn.chatgpt.com/docs/enterprise/plugin-management).

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

Use this repository root as the plugin directory, or extract the local
[dist/rainbrand.plugin.zip](dist/rainbrand.plugin.zip). Load it in a client
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
that supports Streamable HTTP and OAuth. A plugin client reads that connection
from `mcp.json`; a standalone Skill installation needs it configured separately.
Complete Rainbrand sign-in, then let the client discover the live tools and
their schemas. The live tool list determines what the connected account can use.

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
| Claude | Upload the standalone Skill ZIP and configure the remote MCP connection separately. | The portable plugin ZIP is not currently compatible with Claude's native plugin upload or directory format. |
| Cursor | Test the root Agent Plugins manifest from this public repository checkout. | Verify installation and tool use in Cursor. Marketplace publication is a separate process. |

OpenAI documents workspace installation in
[Plugin management](https://learn.chatgpt.com/docs/enterprise/plugin-management)
and the portable format in
[Build plugins](https://developers.openai.com/plugins/build/plugins).

Claude's native format requires `.claude-plugin/plugin.json` and `.mcp.json`
with transport `http`. Those root paths conflict with the portable
specification's requirement that client-specific files use a reverse-domain
top-level directory. This repository does not add an undocumented adapter or a
second maintained implementation. Reconcile those contracts before adding a
native adapter. At that point, also check Claude's archive rules: the repository
contains distribution ZIPs, and a native upload must not contain nested ZIPs.
See [Claude plugin requirements](https://claude.com/docs/plugins/build), the
[pre-submission checklist](https://claude.com/docs/plugins/pre-submission-checklist),
and [directory publishing](https://claude.com/docs/directory/publish).

Cursor recognizes the root `plugin.json`; a separate `.cursor-plugin/plugin.json`
manifest is not required for this format. See
[Cursor plugins](https://cursor.com/docs/reference/plugins) and
[marketplace submission](https://cursor.com/marketplace/publish).

## Optional public-directory publication

Public-directory publication is separate from downloading and uploading the
plugin to a ChatGPT workspace. The following material is included for a future
directory submission; it is not required for workspace installation.

The manifest supplies five read-only positive cases and three negative cases
for OpenAI review. Tool names match the server's raw `tools/list` names:
`list_brands`, `get_brand`, `get_account`, `list_workspaces`, and `check_credits`.
A client may qualify them with the server name, for example
`mcp__rainbrand__list_brands`.

Prepare a dedicated reviewer account with a sample Stripe brand. Run the
positive cases in order in the same conversation: the first case supplies the
Stripe Brand session ID for `get_brand`, and the workspace case supplies the
personal `workspace_id` for `check_credits`. The personal-credit case expects
only `check_credits`. The exchange-rate, Tokyo weather, and arithmetic cases
must invoke no Rainbrand tools; the arithmetic answer is 42. Live connection,
discovery, and calls to all five tools have passed. The walkthrough exercises
all eight exact prompts with the dedicated reviewer account and Stripe brand.
Put reviewer credentials and private instructions in the provider's review
portal, never in this repository.

Before public submission:

- The manifest includes `demo_recording_url` pointing to the
  [Rainbrand walkthrough](https://github.com/trybloomai/rainbrand-skills/releases/download/v1.1.2/rainbrand-review-walkthrough-v1.1.2.mp4),
  published with v1.1.2.
- If OpenAI issues a new ownership challenge, serve the exact plain-text token
  from the portal at the eligible Rainbrand HTTPS origin. Do not reuse an old
  challenge token.
- Check public website, support, and legal pages for the completed Rainbrand
  rollout. Reachable pages alone do not establish that launch is complete.
- Complete each provider's client tests, review requirements, and submission
  process. Provider review determines whether these brand and design workflows
  are accepted; the portable format is not universal approval.

OpenAI's [submission guide](https://developers.openai.com/plugins/deploy/submission)
and [review rules](https://developers.openai.com/plugins/deploy/app-review)
describe this process. An MCP origin change requires a new submission rather
than an update to the previous submission's origin.

Earlier tags, releases, and assets remain unchanged. Use
[`trybloomai/rainbrand-skills`](https://github.com/trybloomai/rainbrand-skills)
in provider portals that require a repository URL.

## Update or remove

```bash
npx skills update rainbrand
npx skills remove rainbrand
```

Add `--global` for a global installation.

## Package and validate

The canonical source is `skills/rainbrand/SKILL.md`. Build both archives and
validate them in this order:

```bash
scripts/package-skill.sh
scripts/package-plugin.sh
scripts/validate-plugin.sh
```

Pass a ZIP path to `scripts/validate-plugin.sh` to validate another local copy
against this checkout. Check submission readiness separately:

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
plugin version, Skill version, and latest numbered changelog release must agree.
Archive checks cover integrity, exact members, regular file types, and
byte-for-byte agreement with source files. Both builders fix timestamps and
file modes so unchanged sources produce identical archives with the same ZIP
tool version, including across time zones and umasks.

For packaging changes, run the optional regression suite:

```bash
python3 scripts/test-validation.py
```

These tests exercise malformed metadata, unsafe or mismatched archives,
submission gates, and reproducible builds. Python 3 is required only for this
test suite, not for package building or validation.

## License

[MIT](LICENSE)
