#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/plugin-common.sh"
require_commands awk zip unzip cmp sort mktemp
validate_shared_sources
package_dir="$(mktemp -d "${TMPDIR:-/tmp}/rainbrand-skill.XXXXXX")"
candidate="$package_dir/rainbrand.skill.zip"
archive="$repo_root/dist/rainbrand.skill.zip"
bloom_candidate="$package_dir/bloom.skill.zip"
bloom_archive="$repo_root/dist/bloom.skill.zip"

trap 'rm -rf "$package_dir"' EXIT

build_deterministic_zip "$repo_root/skills" "$package_dir/stage" "$candidate" "${skill_files[@]}"
mkdir -p "$package_dir/check"
validate_zip_contents "$candidate" "$repo_root/skills" "$package_dir/check" "${skill_files[@]}"
build_deterministic_zip "$repo_root" "$package_dir/bloom-stage" "$bloom_candidate" "${bloom_skill_files[@]}"
validate_zip_contents "$bloom_candidate" "$repo_root" "$package_dir/check" "${bloom_skill_files[@]}"
mkdir -p "$repo_root/dist"
mv "$candidate" "$archive"
mv "$bloom_candidate" "$bloom_archive"

echo "Packaged $archive"
echo "Packaged $bloom_archive"
