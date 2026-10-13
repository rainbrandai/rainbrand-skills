#!/usr/bin/env bash

set -euo pipefail
export LC_ALL=C

source "$(dirname "${BASH_SOURCE[0]}")/plugin-common.sh"
[[ $# -le 1 ]] || fail "Usage: $0 [claude-plugin.zip]"
require_commands awk unzip cmp sort mktemp
validate_plugin_sources --claude

archive="${1:-$repo_root/dist/rainbrand.claude-plugin.zip}"
validation_dir="$(mktemp -d "${TMPDIR:-/tmp}/rainbrand-claude-validate.XXXXXX")"
trap 'rm -rf "$validation_dir"' EXIT

validate_zip_contents "$archive" "$repo_root" "$validation_dir" "${claude_plugin_files[@]}"
validate_zip_contents "$repo_root/dist/rainbrand.skill.zip" "$repo_root/skills" "$validation_dir" "${skill_files[@]}"

echo "Validated $archive"
