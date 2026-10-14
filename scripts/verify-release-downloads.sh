#!/usr/bin/env bash

# Read-only post-publication check, run from the released version's checkout.
set -euo pipefail
source "$(dirname "${BASH_SOURCE[0]}")/plugin-common.sh"
[[ $# == 0 ]] || fail "Usage: $0"
require_commands curl mktemp
download_dir="$(mktemp -d "${TMPDIR:-/tmp}/rainbrand-release-downloads.XXXXXX")"
trap 'rm -rf "$download_dir"' EXIT
for asset in \
  rainbrand.skill.zip \
  rainbrand.codex-plugin.zip \
  rainbrand.claude-plugin.zip \
  rainbrand.cursor-plugin.zip \
  bloom.skill.zip; do
  if [[ "$asset" == bloom.skill.zip ]]; then
    repository=bloom-skills
  else
    repository=rainbrand-skills
  fi
  url="https://github.com/trybloomai/$repository/releases/latest/download/$asset"
  curl --fail --location --silent --show-error --proto '=https' --proto-redir '=https' \
    --output "$download_dir/$asset" "$url"
  echo "Downloaded $url (followed redirects)"
done
"$repo_root/scripts/validate-skills.sh" "$download_dir"
"$repo_root/scripts/validate-codex-plugin.sh" "$download_dir/rainbrand.codex-plugin.zip"
"$repo_root/scripts/validate-claude-plugin.sh" "$download_dir/rainbrand.claude-plugin.zip"
"$repo_root/scripts/validate-cursor-plugin.sh" "$download_dir/rainbrand.cursor-plugin.zip"
