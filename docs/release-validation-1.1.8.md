# Rainbrand 1.1.8 packaging verification

Verified locally on 2026-10-13 in the `conductor/claude-plugin-fix` branch.
The native adapter follows [Claude's plugin layout](https://claude.com/docs/plugins/build)
and the supported top-level [`icon` field](https://code.claude.com/docs/en/plugins/manifest-reference#directory-listing-fields).

The portable plugin retains root `plugin.json` and `mcp.json` with transport
`streamable-http`. The native ZIP contains `.claude-plugin/plugin.json`, root
`.mcp.json` with transport `http`, and the existing Rainbrand image referenced
by `icon`. Both connect to `https://mcp.rainbrand.com/mcp`. All three ZIPs copy
the same canonical `skills/rainbrand/SKILL.md` bytes.

## Commands and results

Run from the repository root:

```bash
scripts/package-skill.sh && scripts/package-plugin.sh && scripts/package-claude-plugin.sh && scripts/validate-plugin.sh && scripts/validate-claude-plugin.sh && scripts/validate-plugin.sh --submission
```

Exit 0. All three archives built successfully. The portable, native, and
OpenAI submission metadata validators passed. Submission metadata validation
does not establish provider approval or live client behavior.

```bash
python3 scripts/test-validation.py
```

Exit 0: `Ran 15 tests in 16.926s`, `OK`. Coverage includes malformed native
manifest and MCP JSON, duplicate and unsupported fields, version mismatches,
unsafe archives, missing/altered image members, every native member's byte
parity, canonical Skill parity, and rejection of the other plugin format.
All three archives reproduced identical bytes under `Pacific/Honolulu` with
umask `077` and `Asia/Tokyo` with umask `022`. The existing portable draft and
OpenAI submission gates remain covered.

```bash
claude plugin validate .
```

Exit 0: `Validation passed`, using Claude Code 2.1.296. Only informational
advice to add a marketplace install line appeared; this repository documents
ZIP upload and does not declare a marketplace.

The actual validated ZIP was also unpacked into a temporary directory and
checked with the same CLI command:

```bash
python3 - <<'PY'
from pathlib import Path
import subprocess
import tempfile
import zipfile
with tempfile.TemporaryDirectory(prefix='rainbrand-native-check-') as check:
    with zipfile.ZipFile('dist/rainbrand.claude-plugin.zip') as archive:
        archive.extractall(check)
    subprocess.run(['claude', 'plugin', 'validate', '.'], cwd=check, check=True)
PY
```

Exit 0: `Validation passed`, with the same marketplace advice.

```bash
bash -n scripts/package-skill.sh scripts/package-plugin.sh scripts/package-claude-plugin.sh scripts/validate-plugin.sh scripts/validate-claude-plugin.sh scripts/plugin-common.sh
git diff --check
sha256sum dist/rainbrand.claude-plugin.zip
```

Shell syntax and diff checks exited 0. The artifact is
`dist/rainbrand.claude-plugin.zip`, SHA-256:

```text
6dbf50c565737c844369750cdf47865944205dd460941817bec96319ba7975af
```

Build environment: Bash 5.2.15, Info-ZIP Zip 3.0, UnZip 6.00, Python 3.9.25.
Builders and offline validators retain the existing Bash 3.2/POSIX awk
implementation; Python is needed only for regression tests. Bash 3.2 was not
available for a separate runtime check.

## Live evidence and release gates

The original rejection is recorded in
[Hero #3550](https://github.com/trybloomai/hero/issues/3550) and its
[packaging finding](https://github.com/trybloomai/hero/issues/3550#issuecomment-6156757378).
The user subsequently reported successful Claude upload of the v1.1.8 native
candidate: it appeared as Rainbrand with exactly **1 Skill and 1 Connector**.
This closes the archive-layout/upload portion of the P0. The screenshot is
in the separate Hero dogfood workspace and was not inspected here.

That candidate omitted the manifest icon and image, producing Claude's generic
plug glyph. This is a non-behavioral presentation defect. The final ZIP now
includes both, and offline validation proves the image bytes match the source.
Visual confirmation requires uploading this corrected package again; it has
not been claimed as passed.

Before release approval, synchronize Hero's mirrored Skill copies (including
`mintlify-docs/skill.md`) to the canonical 1.1.8 bytes. Only the Skill's version
metadata changed; its guidance did not. No Hero files were changed here.

Remaining gates:

- Upload the corrected final package and visually confirm the Rainbrand image.
- Complete OAuth sign-in with the final package.
- Confirm connected-tool discovery with the final package.
- Synchronize Hero's Skill mirrors before publishing the 1.1.8 distributions.
- After authorized publication, confirm the released native asset matches this
  SHA-256 and repeat the live checks against that released asset.

**SHIP: NO** until those release gates pass. The artifact is locally validated
and ready for review and final client testing. No push, PR, merge, release
publication, or tracker update was performed in this workspace.
