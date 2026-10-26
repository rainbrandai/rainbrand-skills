#!/usr/bin/env bash

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/plugin-common.sh"
require_commands cmp sort mktemp
validation_dir="$(mktemp -d "${TMPDIR:-/tmp}/rainbrand-release-validate.XXXXXX")"
trap 'rm -rf "$validation_dir"' EXIT
printf '%s\n' "${release_files[@]}" | sort > "$validation_dir/expected"
for file in "$repo_root"/dist/*; do
  [[ -f "$file" && ! -L "$file" ]] || fail "Release assets must be regular files: $file"
  printf '%s\n' "${file##*/}"
done | sort > "$validation_dir/actual"
cmp -s "$validation_dir/expected" "$validation_dir/actual" || fail "Release must contain exactly: ${release_files[*]}"
"$repo_root/scripts/validate-codex-plugin.sh"
"$repo_root/scripts/validate-claude-plugin.sh"
"$repo_root/scripts/validate-cursor-plugin.sh"
"$repo_root/scripts/validate-portable-plugin.sh"
echo "Validated release assets: ${release_files[*]}"
