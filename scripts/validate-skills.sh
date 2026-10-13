#!/usr/bin/env bash

set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/plugin-common.sh"
[[ $# -le 1 ]] || fail "Usage: $0 [archive-directory]"
require_commands awk unzip cmp sort mktemp
validate_plugin_sources
validation_dir="$(mktemp -d "${TMPDIR:-/tmp}/rainbrand-skills-validate.XXXXXX")"
trap 'rm -rf "$validation_dir"' EXIT
validate_skill_archives "${1:-$repo_root/dist}" "$validation_dir"
echo "Validated rainbrand.skill.zip and bloom.skill.zip"
