#!/usr/bin/env bash

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/plugin-common.sh"
"$repo_root/scripts/package-skill.sh"
"$repo_root/scripts/package-codex-plugin.sh"
"$repo_root/scripts/package-claude-plugin.sh"
"$repo_root/scripts/package-cursor-plugin.sh"
"$repo_root/scripts/validate-release.sh"
