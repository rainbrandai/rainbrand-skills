#!/usr/bin/env bash

set -euo pipefail
export LC_ALL=C

source "$(dirname "${BASH_SOURCE[0]}")/plugin-common.sh"
[[ $# -le 1 ]] || fail "Usage: $0 [cursor-plugin.zip]"
require_commands awk unzip cmp sort mktemp od tr
validate_plugin_sources cursor

archive="${1:-$repo_root/dist/rainbrand.cursor-plugin.zip}"
validation_dir="$(mktemp -d "${TMPDIR:-/tmp}/rainbrand-cursor-validate.XXXXXX")"
trap 'rm -rf "$validation_dir"' EXIT

validate_zip_contents "$archive" "$repo_root" "$validation_dir" "${cursor_plugin_files[@]}"
validate_skill_archives "$repo_root/dist" "$validation_dir"

echo "Validated $archive"
