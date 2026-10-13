#!/usr/bin/env bash

# Shared Rainbrand source, archive, and deterministic packaging checks.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export LC_ALL=C
export TZ=UTC
review_recording_url="https://github.com/trybloomai/rainbrand-skills/releases/download/v1.1.2/rainbrand-review-walkthrough-v1.1.2.mp4"
plugin_files=(
  plugin.json
  mcp.json
  skills/rainbrand/SKILL.md
  README.md
  CHANGELOG.md
  LICENSE
)
# A portable draft may omit artwork. Submission requires the approved icon
# and both manifest references; neither a placeholder nor the prior icon ships.
if [[ -e "$repo_root/assets/rainbrand-logo.png" ]]; then
  plugin_files+=(assets/rainbrand-logo.png)
fi
skill_files=(rainbrand/SKILL.md)
bloom_skill_files=(bloom/SKILL.md)
release_files=(rainbrand.skill.zip bloom.skill.zip rainbrand.plugin.zip rainbrand.claude-plugin.zip)
claude_plugin_files=(
  .claude-plugin/plugin.json
  .mcp.json
  skills/rainbrand/SKILL.md
  README.md
  CHANGELOG.md
  LICENSE
  assets/rainbrand-logo.png
)

fail() {
  echo "Error: $*" >&2
  exit 1
}

require_commands() {
  local command_name
  for command_name in "$@"; do
    command -v "$command_name" >/dev/null 2>&1 || fail "Required command not found: $command_name"
  done
}

validate_regular_zip_members() {
  # Info-ZIP's long listing exposes Unix symlinks and other special file types.
  # The package builder writes regular files only; enforce that on read too.
  # Skip the two header lines, which include the archive path.
  unzip -Z -l "$1" | awk -v expected="$2" '
    NR > 2 && $2 ~ /^[0-9]+\.[0-9]+$/ {
      if ($1 !~ /^-/) exit 1
      files++
    }
    END { if (files != expected) exit 1 }
  ' || fail "Archive members must be regular files: $1"
}

read_skill_metadata() {
  awk -v quote="'" -v expected_name="$2" -v expected_author="$3" -v expected_url="$4" '
    function scalar(text,    first) {
      first = substr(text, 1, 1)
      if (length(text) > 1 && (first == "\"" || first == quote) && substr(text, length(text)) == first)
        return substr(text, 2, length(text) - 2)
      return text
    }
    NR == 1 { if ($0 != "---") exit 1; next }
    /^---$/ { closed = 1; exit }
    /^name: / { name = scalar(substr($0, 7)); names++ }
    /^description: / {
      description = scalar(substr($0, 14)); descriptions++
      if (description == "" || length(description) > 200 || description ~ /[<>]/) exit 1
    }
    /^license: / { if (scalar(substr($0, 10)) != "MIT") exit 1; licenses++ }
    /^metadata:$/ { metadata = 1; next }
    /^[^ ]/ { metadata = 0 }
    metadata && /^  version: / {
      version = scalar(substr($0, 12))
      versions++
    }
    metadata && /^  author: / { if (scalar(substr($0, 11)) != expected_author) exit 1; authors++ }
    metadata && /^  url: / { if (scalar(substr($0, 8)) != expected_url) exit 1; urls++ }
    END {
      if (!closed || names != 1 || versions != 1 || descriptions != 1 || licenses != 1 || authors != 1 || urls != 1 || name != expected_name || version == "") exit 1
      print name
      print version
    }
  ' "$1" || fail "Invalid Skill frontmatter (including the 200-character upload description limit): $1"
}

validate_plugin_sources() {
  local file skill_metadata skill_name skill_version release_version
  local source_files=("${plugin_files[@]}")
  # Portable drafts may still omit artwork. Native builds require the icon.
  if [[ "${1:-}" == --claude ]]; then
    source_files+=("${claude_plugin_files[@]}")
    [[ -d "$repo_root/.claude-plugin" && ! -L "$repo_root/.claude-plugin" ]] || fail "Expected a regular source directory: .claude-plugin"
  fi
  for file in "${source_files[@]}"; do
    [[ -f "$repo_root/$file" && ! -L "$repo_root/$file" ]] || fail "Missing regular source file: $file"
  done
  for file in skills skills/rainbrand; do
    [[ -d "$repo_root/$file" && ! -L "$repo_root/$file" ]] || fail "Expected a regular source directory: $file"
  done
  for file in "$repo_root"/skills/*; do
    [[ "$file" == "$repo_root/skills/rainbrand" ]] || fail "Expected only the Rainbrand Skill"
  done
  if [[ -e "$repo_root/assets" || -L "$repo_root/assets" ]]; then
    [[ -d "$repo_root/assets" && ! -L "$repo_root/assets" ]] || fail "Expected a regular source directory: assets"
    for file in "$repo_root"/assets/*; do
      [[ -e "$file" ]] || continue
      [[ "$file" == "$repo_root/assets/rainbrand-logo.png" ]] || fail "Unexpected asset: ${file##*/}"
    done
  fi

  # The active package must not carry prior presentation or connection data.
  # The review recording remains on its immutable v1.1.2 release, so allow
  # only that exact versioned URL while rejecting prior product branding.
  for file in "${source_files[@]}"; do
    local allow_compatibility=0
    if [[ "$file" == README.md || "$file" == CHANGELOG.md ]]; then
      allow_compatibility=1
    fi
    awk -v profile=rainbrand -v allowed_url="$review_recording_url" \
      -v allow_compatibility="$allow_compatibility" \
      -f "$repo_root/scripts/validate-branding.awk" "$repo_root/$file" || \
      fail "Unexpected branding or endpoint in package source: $file"
  done

  # Read only the canonical frontmatter, with version under metadata. Accept
  # plain, double-quoted, or single-quoted scalar values.
  skill_metadata="$(read_skill_metadata "$repo_root/skills/rainbrand/SKILL.md" rainbrand Rainbrand \
    https://docs.rainbrand.com/mcp/getting-started)"
  skill_name="${skill_metadata%%$'\n'*}"
  skill_version="${skill_metadata#*$'\n'}"
  [[ "$skill_name" == rainbrand ]] || fail "Skill name must match its directory: rainbrand"
  [[ "$skill_version" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]] || fail "Expected a stable semantic Skill version"

  release_version="$(awk '
    /^## \[[0-9]/ {
      sub(/^## \[/, "")
      sub(/\].*$/, "")
      print
      exit
    }
  ' "$repo_root/CHANGELOG.md")"
  [[ "$release_version" == "$skill_version" ]] || fail "Latest changelog release must match Skill version $skill_version"

  awk -v kind=plugin -v expected_name="$skill_name" -v expected_version="$skill_version" \
    -v has_artwork="$( [[ -f "$repo_root/assets/rainbrand-logo.png" ]] && echo 1 || echo 0 )" \
    -v allowed_legacy_url="$review_recording_url" \
    -v submission="${submission:-0}" \
    -f "$repo_root/scripts/validate-manifests.awk" "$repo_root/plugin.json"
  awk -v kind=mcp -v expected_name="$skill_name" \
    -f "$repo_root/scripts/validate-manifests.awk" "$repo_root/mcp.json"
  if [[ "${1:-}" == --claude ]]; then
    awk -v kind=claude-plugin -v expected_name="$skill_name" -v expected_version="$skill_version" \
      -f "$repo_root/scripts/validate-manifests.awk" "$repo_root/.claude-plugin/plugin.json"
    awk -v kind=claude-mcp -v expected_name="$skill_name" \
      -f "$repo_root/scripts/validate-manifests.awk" "$repo_root/.mcp.json"
  fi
}

build_deterministic_zip() {
  local source_root="$1" stage_dir="$2" candidate="$3" file
  shift 3
  for file in "$@"; do
    mkdir -p "$stage_dir/$(dirname "$file")"
    cp "$source_root/$file" "$stage_dir/$file"
    chmod 644 "$stage_dir/$file"
    touch -t 198001010000 "$stage_dir/$file"
  done
  (
    cd "$stage_dir"
    zip -X -q "$candidate" "$@"
  )
}

validate_zip_contents() {
  local archive="$1" source_root="$2" validation_dir="$3" file
  shift 3
  [[ -f "$archive" && ! -L "$archive" ]] || fail "Missing regular archive: $archive"
  unzip -tq "$archive" >/dev/null || fail "Invalid or corrupt ZIP: $archive"
  printf '%s\n' "$@" | sort > "$validation_dir/expected"
  unzip -Z1 "$archive" > "$validation_dir/entries"
  sort "$validation_dir/entries" > "$validation_dir/actual"
  cmp -s "$validation_dir/expected" "$validation_dir/actual" || \
    fail "Archive must contain exactly the allowed files (no wrapper, duplicates, or extras): $archive"
  validate_regular_zip_members "$archive" "$#"
  # Stream only allowlisted members; never extract paths from an untrusted ZIP.
  for file in "$@"; do
    unzip -p "$archive" "$file" > "$validation_dir/member"
    cmp -s "$source_root/$file" "$validation_dir/member" || fail "Archive differs from source: $file"
  done
}

# Generate a transient branded variant; there is no second maintained Skill.
render_bloom_skill() {
  local source_root="$1" canonical_metadata bloom_metadata
  mkdir -p "$source_root/bloom"
  awk -f "$repo_root/scripts/brand-bloom-skill.awk" "$repo_root/skills/rainbrand/SKILL.md" > "$source_root/bloom/SKILL.md"
  awk -v profile=bloom -f "$repo_root/scripts/validate-branding.awk" "$source_root/bloom/SKILL.md" || \
    fail "Rainbrand identity remains in generated Bloom Skill"
  canonical_metadata="$(read_skill_metadata "$repo_root/skills/rainbrand/SKILL.md" rainbrand Rainbrand https://docs.rainbrand.com/mcp/getting-started)"
  bloom_metadata="$(read_skill_metadata "$source_root/bloom/SKILL.md" bloom Bloom https://docs.trybloom.ai/mcp/getting-started)"
  [[ "${canonical_metadata#*$'\n'}" == "${bloom_metadata#*$'\n'}" ]] || fail "Bloom Skill version must match canonical Skill"
}

validate_skill_archives() {
  local archive_dir="$1" validation_dir="$2"
  validate_zip_contents "$archive_dir/rainbrand.skill.zip" "$repo_root/skills" "$validation_dir" "${skill_files[@]}"
  render_bloom_skill "$validation_dir/bloom-source"
  validate_zip_contents "$archive_dir/bloom.skill.zip" "$validation_dir/bloom-source" "$validation_dir" "${bloom_skill_files[@]}"
}
