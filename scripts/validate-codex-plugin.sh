#!/usr/bin/env bash

set -euo pipefail
export LC_ALL=C

source "$(dirname "${BASH_SOURCE[0]}")/plugin-common.sh"
[[ $# -le 1 ]] || fail "Usage: $0 [codex-plugin.zip]"
require_commands awk unzip cmp sort mktemp od tr
validate_plugin_sources codex

archive="${1:-$repo_root/dist/rainbrand.codex-plugin.zip}"
validation_dir="$(mktemp -d "${TMPDIR:-/tmp}/rainbrand-codex-validate.XXXXXX")"
trap 'rm -rf "$validation_dir"' EXIT

validate_zip_contents "$archive" "$repo_root" "$validation_dir" "${codex_plugin_files[@]}"
validate_skill_archives "$repo_root/dist" "$validation_dir"

echo "Validated $archive"
