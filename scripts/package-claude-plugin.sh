#!/usr/bin/env bash

set -euo pipefail
export LC_ALL=C

source "$(dirname "${BASH_SOURCE[0]}")/plugin-common.sh"
require_commands awk zip unzip cmp sort mktemp od tr
render_plugin_manifests
render_claude_directory
validate_plugin_sources claude

package_dir="$(mktemp -d "${TMPDIR:-/tmp}/rainbrand-claude-plugin.XXXXXX")"
trap 'rm -rf "$package_dir"' EXIT
stage_dir="$package_dir/stage"
candidate="$package_dir/rainbrand.claude-plugin.zip"

# Reuse the canonical Skill directly. Only native manifest paths differ.
build_deterministic_zip "$repo_root" "$stage_dir" "$candidate" "${claude_plugin_files[@]}"

"$repo_root/scripts/validate-claude-plugin.sh" "$candidate"
mkdir -p "$repo_root/dist"
mv "$candidate" "$repo_root/dist/rainbrand.claude-plugin.zip"
echo "Packaged $repo_root/dist/rainbrand.claude-plugin.zip"
