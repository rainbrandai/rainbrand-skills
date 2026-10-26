#!/usr/bin/env bash

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/plugin-common.sh"
require_commands awk find cmp sort mktemp
# The portable OpenAI extension reuses the validated native listing and review
# metadata. Renderer freshness checks ensure neither copy can drift.
validate_plugin_sources codex
validation_dir="$(mktemp -d "${TMPDIR:-/tmp}/rainbrand-portable-validate.XXXXXX")"
trap 'rm -rf "$validation_dir"' EXIT
validate_portable_directory "$validation_dir"
skill_metadata="$(read_skill_metadata "$repo_root/skills/rainbrand/SKILL.md" rainbrand Rainbrand \
  https://docs.rainbrand.com/mcp/getting-started)"
IFS=$'\t' read -r skill_name skill_version skill_description <<< "$skill_metadata"
awk -v kind=portable-plugin -v expected_name="$skill_name" -v expected_version="$skill_version" \
  -v expected_description="$skill_description" \
  -f "$repo_root/scripts/validate-manifests.awk" "$portable_directory_root/plugin.json"
awk -v kind=portable-mcp -v expected_name="$skill_name" \
  -f "$repo_root/scripts/validate-manifests.awk" "$portable_directory_root/mcp.json"
echo "Validated $portable_directory_root"
