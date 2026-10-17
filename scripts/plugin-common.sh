#!/usr/bin/env bash

# Shared Rainbrand source, archive, and deterministic packaging checks.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export LC_ALL=C
export TZ=UTC

shared_plugin_files=(
  skills/rainbrand/SKILL.md
  README.md
  CHANGELOG.md
  LICENSE
  assets/rainbrand-logo.png
)
codex_plugin_files=(
  .codex-plugin/plugin.json
  .codex-plugin/.mcp.json::.mcp.json
  "${shared_plugin_files[@]}"
)
claude_plugin_files=(
  .claude-plugin/plugin.json
  .mcp.json
  "${shared_plugin_files[@]}"
)
cursor_plugin_files=(
  .cursor-plugin/plugin.json
  mcp.json
  "${shared_plugin_files[@]}"
)
skill_files=(rainbrand/SKILL.md)
bloom_skill_files=(bloom/SKILL.md)
release_files=(
  rainbrand.skill.zip
  bloom.skill.zip
  rainbrand.codex-plugin.zip
  rainbrand.claude-plugin.zip
  rainbrand.cursor-plugin.zip
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

# Skill frontmatter is the canonical source for shared package identity and the
# default package description. Provider-specific listing copy lives in
# plugin-copy.json; validation below rejects any generated file that drifts.
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
      print name "\t" version "\t" description
    }
  ' "$1" || fail "Invalid Skill frontmatter (including the 200-character upload description limit): $1"
}

validate_source_file() {
  [[ -f "$repo_root/$1" && ! -L "$repo_root/$1" ]] || fail "Missing regular source file: $1"
}

validate_source_directory() {
  local directory="$1" file expected allowed
  shift
  [[ -d "$repo_root/$directory" && ! -L "$repo_root/$directory" ]] || fail "Expected a regular source directory: $directory"
  for file in "$repo_root/$directory"/*; do
    [[ -e "$file" ]] || continue
    allowed=0
    for expected in "$@"; do
      if [[ "${file##*/}" == "$expected" ]]; then
        allowed=1
        break
      fi
    done
    [[ "$allowed" == 1 ]] || fail "Unexpected source in $directory: ${file##*/}"
  done
}

render_plugin_manifests() {
  require_commands python3
  validate_source_file skills/rainbrand/SKILL.md
  validate_source_file plugin-copy.json
  validate_source_file plugin-config.json
  validate_source_file scripts/render-plugin-manifests.py
  python3 "$repo_root/scripts/render-plugin-manifests.py" --write
}

validate_rainbrand_branding() {
  local file allow_compatibility
  for file in "$@"; do
    allow_compatibility=0
    if [[ "$file" == README.md || "$file" == CHANGELOG.md ]]; then
      allow_compatibility=1
    fi
    awk -v profile=rainbrand -v allow_compatibility="$allow_compatibility" \
      -f "$repo_root/scripts/validate-branding.awk" "$repo_root/$file" || \
      fail "Unexpected branding or endpoint in package source: $file"
  done
}

validate_bloom_branding() {
  local file
  for file in "$@"; do
    awk -v profile=bloom -f "$repo_root/scripts/validate-branding.awk" "$repo_root/$file" || \
      fail "Unexpected branding or endpoint in Bloom package source: $file"
  done
}

validate_shared_sources() {
  local file skill_metadata skill_name skill_version skill_description
  local bloom_metadata bloom_name bloom_version bloom_description release_version
  for file in skills/rainbrand/SKILL.md skills/bloom/SKILL.md README.md CHANGELOG.md LICENSE; do
    validate_source_file "$file"
  done
  [[ -d "$repo_root/skills" && ! -L "$repo_root/skills" ]] || \
    fail "Expected a regular source directory: skills"
  validate_source_directory skills/rainbrand SKILL.md
  validate_source_directory skills/bloom SKILL.md
  for file in "$repo_root"/skills/*; do
    case "$file" in
      "$repo_root/skills/rainbrand"|"$repo_root/skills/bloom") ;;
      *) fail "Expected only the Rainbrand and Bloom Skills" ;;
    esac
  done
  [[ ! -e "$repo_root/plugin.json" && ! -L "$repo_root/plugin.json" ]] || fail "Root plugin.json is retired"

  validate_rainbrand_branding skills/rainbrand/SKILL.md README.md CHANGELOG.md LICENSE
  validate_bloom_branding skills/bloom/SKILL.md
  skill_metadata="$(read_skill_metadata "$repo_root/skills/rainbrand/SKILL.md" rainbrand Rainbrand \
    https://docs.rainbrand.com/mcp/getting-started)"
  IFS=$'\t' read -r skill_name skill_version skill_description <<< "$skill_metadata"
  [[ "$skill_name" == rainbrand ]] || fail "Skill name must match its directory: rainbrand"
  [[ "$skill_version" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]] || \
    fail "Expected a stable semantic Rainbrand Skill version"
  bloom_metadata="$(read_skill_metadata "$repo_root/skills/bloom/SKILL.md" bloom Bloom \
    https://docs.trybloom.ai/mcp/getting-started)"
  IFS=$'\t' read -r bloom_name bloom_version bloom_description <<< "$bloom_metadata"
  [[ "$bloom_name" == bloom ]] || fail "Skill name must match its directory: bloom"
  [[ "$bloom_version" =~ ^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$ ]] || \
    fail "Expected a stable semantic Bloom Skill version"

  release_version="$(awk '
    /^## \[[0-9]/ {
      sub(/^## \[/, "")
      sub(/\].*$/, "")
      print
      exit
    }
  ' "$repo_root/CHANGELOG.md")"
  [[ "$release_version" == "$skill_version" ]] || fail "Latest changelog release must match Skill version $skill_version"
}

validate_plugin_sources() {
  local provider="$1" manifest_kind manifest_file mcp_kind mcp_file skill_metadata skill_name skill_version skill_description
  validate_shared_sources
  require_commands od tr python3
  validate_source_file plugin-copy.json
  validate_source_file plugin-config.json
  validate_source_file scripts/render-plugin-manifests.py
  validate_source_directory assets rainbrand-logo.png rainbrand-social-preview.png
  validate_source_directory .codex-plugin plugin.json .mcp.json
  validate_source_directory .claude-plugin plugin.json
  validate_source_directory .cursor-plugin plugin.json
  validate_source_file .codex-plugin/plugin.json
  validate_source_file .codex-plugin/.mcp.json
  validate_source_file .claude-plugin/plugin.json
  validate_source_file .cursor-plugin/plugin.json
  validate_source_file .mcp.json
  validate_source_file mcp.json
  # The bundled image is a 148x148 PNG, comfortably above each provider's
  # 48x48 minimum. Check its signature and IHDR dimensions without image tools.
  [[ "$(od -An -tx1 -N24 "$repo_root/assets/rainbrand-logo.png" | tr -d ' \n')" == \
    89504e470d0a1a0a0000000d494844520000009400000094 ]] || \
    fail "Expected a 148x148 PNG: assets/rainbrand-logo.png"

  case "$provider" in
    codex)
      manifest_kind=codex-plugin
      manifest_file=.codex-plugin/plugin.json
      mcp_kind=codex-mcp
      mcp_file=.codex-plugin/.mcp.json
      ;;
    claude)
      manifest_kind=claude-plugin
      manifest_file=.claude-plugin/plugin.json
      mcp_kind=claude-mcp
      mcp_file=.mcp.json
      ;;
    cursor)
      manifest_kind=cursor-plugin
      manifest_file=.cursor-plugin/plugin.json
      mcp_kind=cursor-mcp
      mcp_file=mcp.json
      ;;
    *) fail "Unknown plugin provider: $provider" ;;
  esac

  validate_rainbrand_branding plugin-copy.json plugin-config.json "$manifest_file" "$mcp_file"
  python3 "$repo_root/scripts/render-plugin-manifests.py" --check
  skill_metadata="$(read_skill_metadata "$repo_root/skills/rainbrand/SKILL.md" rainbrand Rainbrand \
    https://docs.rainbrand.com/mcp/getting-started)"
  IFS=$'\t' read -r skill_name skill_version skill_description <<< "$skill_metadata"
  awk -v kind="$manifest_kind" -v expected_name="$skill_name" -v expected_version="$skill_version" \
    -v expected_description="$skill_description" \
    -f "$repo_root/scripts/validate-manifests.awk" "$repo_root/$manifest_file"
  awk -v kind="$mcp_kind" -v expected_name="$skill_name" \
    -f "$repo_root/scripts/validate-manifests.awk" "$repo_root/$mcp_file"
}

build_deterministic_zip() {
  local source_root="$1" stage_dir="$2" candidate="$3" mapping source_file archive_file
  local archive_files=()
  shift 3
  for mapping in "$@"; do
    source_file="${mapping%%::*}"
    archive_file="${mapping#*::}"
    if [[ "$archive_file" == "$mapping" ]]; then
      archive_file="$source_file"
    fi
    mkdir -p "$stage_dir/$(dirname "$archive_file")"
    cp "$source_root/$source_file" "$stage_dir/$archive_file"
    chmod 644 "$stage_dir/$archive_file"
    touch -t 198001010000 "$stage_dir/$archive_file"
    archive_files+=("$archive_file")
  done
  (
    cd "$stage_dir"
    zip -X -q "$candidate" "${archive_files[@]}"
  )
}

validate_zip_contents() {
  local archive="$1" source_root="$2" validation_dir="$3" mapping source_file archive_file
  shift 3
  [[ -f "$archive" && ! -L "$archive" ]] || fail "Missing regular archive: $archive"
  unzip -tq "$archive" >/dev/null || fail "Invalid or corrupt ZIP: $archive"
  : > "$validation_dir/expected"
  for mapping in "$@"; do
    archive_file="${mapping#*::}"
    if [[ "$archive_file" == "$mapping" ]]; then
      archive_file="${mapping%%::*}"
    fi
    printf '%s\n' "$archive_file" >> "$validation_dir/expected"
  done
  sort -o "$validation_dir/expected" "$validation_dir/expected"
  unzip -Z1 "$archive" > "$validation_dir/entries"
  sort "$validation_dir/entries" > "$validation_dir/actual"
  cmp -s "$validation_dir/expected" "$validation_dir/actual" || \
    fail "Archive must contain exactly the allowed files (no wrapper, duplicates, or extras): $archive"
  validate_regular_zip_members "$archive" "$#"
  # Stream only allowlisted members; never extract paths from an untrusted ZIP.
  for mapping in "$@"; do
    source_file="${mapping%%::*}"
    archive_file="${mapping#*::}"
    if [[ "$archive_file" == "$mapping" ]]; then
      archive_file="$source_file"
    fi
    unzip -p "$archive" "$archive_file" > "$validation_dir/member"
    cmp -s "$source_root/$source_file" "$validation_dir/member" || \
      fail "Archive differs from source: $source_file -> $archive_file"
  done
}

validate_skill_archives() {
  local archive_dir="$1" validation_dir="$2"
  validate_zip_contents "$archive_dir/rainbrand.skill.zip" "$repo_root/skills" "$validation_dir" "${skill_files[@]}"
  validate_zip_contents "$archive_dir/bloom.skill.zip" "$repo_root/skills" "$validation_dir" "${bloom_skill_files[@]}"
}
