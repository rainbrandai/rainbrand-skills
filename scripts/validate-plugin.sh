#!/usr/bin/env bash

set -euo pipefail
export LC_ALL=C

source "$(dirname "${BASH_SOURCE[0]}")/plugin-common.sh"
submission=0
if [[ "${1:-}" == --submission ]]; then
  submission=1
  shift
fi
[[ $# -le 1 ]] || fail "Usage: $0 [--submission] [plugin.zip]"
require_commands awk unzip cmp sort mktemp
validate_plugin_sources

archive="${1:-$repo_root/dist/rainbrand.plugin.zip}"
[[ -f "$archive" && ! -L "$archive" ]] || fail "Missing regular plugin archive: $archive"
validation_dir="$(mktemp -d "${TMPDIR:-/tmp}/rainbrand-validate.XXXXXX")"
trap 'rm -rf "$validation_dir"' EXIT

validate_zip_contents "$archive" "$repo_root" "$validation_dir" "${plugin_files[@]}"

# Keep both standalone distributions aligned without rebuilding them.
validate_skill_archives "$repo_root/dist" "$validation_dir"

echo "Validated $archive"
