# Verify Rainbrand in Pi

The Pi package is prepared for Tomas's review. Its npm name is
`@rainbrand-ai/pi-plugin` and its version follows the canonical Rainbrand Skill.
The customer instructions ship in
[the package README](../packages/pi/README.md).

## Isolated local install

Run these commands from the repository root with Python 3.9 or later,
Node.js 22.19 or later, and pnpm 10.34.7. All Pi installation and state for
this smoke test live under the gitignored `.context/` directory.

```bash
pi_test_root="$PWD/.context/pi-review"
mkdir -p "$pi_test_root/project" "$pi_test_root/agent"
pi_tarball="$(python3 packages/pi/pack.py "$pi_test_root/artifacts")"
pnpm --dir "$pi_test_root" add @earendil-works/pi-coding-agent@1.5.2 --ignore-scripts
pnpm --dir "$pi_test_root" add "$pi_tarball" --ignore-scripts
pi_package_name="$(node -p "JSON.parse(require('fs').readFileSync('packages/pi/package.template.json', 'utf8')).name")"
export PI_CODING_AGENT_DIR="$pi_test_root/agent"
cd "$pi_test_root/project"
"$pi_test_root/node_modules/.bin/pi" install "$pi_test_root/node_modules/$pi_package_name"
"$pi_test_root/node_modules/.bin/pi" list
"$pi_test_root/node_modules/.bin/pi"
```

This installs the actual packed npm artifact through pnpm and registers its
installed directory through Pi's local package entry point. Pi loads the
manifest's extension and Skill from that directory.

## Sign in and request a Brief

In the Pi session, check that `/skill:rainbrand` is available and run `/mcp`.
Rainbrand should appear with its connection state. Run `/mcp login rainbrand`,
sign in using the existing Rainbrand reviewer account, and approve access in
the browser. If the browser is on another machine, paste its redirected URL
directly into Pi's sign-in prompt. Keep authorization codes and tokens in Pi.

The shell command `pi mcp login` reads file-configured servers. Use the
in-session command for Rainbrand's extension registration. If an existing
file configuration also defines `rainbrand`, Pi gives that configuration
precedence. Check `/mcp` for overrides when troubleshooting.

Select an authenticated model in Pi, then send this prompt.

```text
Use Rainbrand and the existing Stripe Brand in this reviewer account. Get a
Brief for a homepage hero, then summarize the applicable voice, supported
claims, visual guidance, and available assets. Discover the current Rainbrand
tools and their schemas and use the existing Brand.
```

Record successful OAuth, loaded Rainbrand tools, the selected Brand, the
returned Brief, and a concise summary of those four categories. Check the
result against the live tool output. Pi owns OAuth discovery, browser
authorization, token storage, and refresh.

## Verification on November 18, 2026

The isolated smoke test used Pi 1.5.2, Node.js 24.22.1, pnpm 10.34.7, and
Rainbrand Skill version 1.1.14. The `@rainbrand-ai/pi-plugin` artifact installed
successfully through pnpm and `pi install` registered its local directory.
Pi's RPC `get_commands` response discovered `skill:rainbrand` from the installed package. The native
`/mcp` command reported `rainbrand` as needing sign-in.

The hosted MCP endpoint returned HTTP 401 with protected-resource metadata
pointing to Rainbrand's authorization server. Pi's native `/mcp login rainbrand`
completed discovery and generated an authorization request to
`www.rainbrand.com/api/auth/oauth2/authorize` with PKCE S256 and a loopback
callback. Pi then requested browser sign-in. The test cancelled at that prompt.

After the npm scope update, all seven package regression tests, manifest
freshness, and the release validators pass. The 31 existing regression tests
passed on the preceding implementation. The rebuilt tarball contains six
regular files and its SHA-256 is
`c60e9308ea85b0cd20515ff2287e046d774eeb52c7f96370eef3631c2e16e76d`.
Reviewer sign-in credentials were absent from the test workspace and environment.
Successful browser approval, token exchange and refresh, authenticated tool
loading, and the Stripe homepage-hero Brief remain unverified. To complete
those checks, start the isolated Pi session above, run `/mcp login rainbrand`,
approve access as the reviewer, select an authenticated model, and send the
Brief prompt. Record the result before publication.

The coordinating parent workspace verified npm access on November 18, 2026.
`pnpm whoami` returned `tomasward`, and
`pnpm exec npm org ls rainbrand-ai --json --registry=https://registry.npmjs.org/`
returned `{"tomasward":"owner"}`. Scope ownership is verified. Publication
requires Tomas's review and explicit approval.
