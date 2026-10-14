# Changelog

Notable changes to the Rainbrand Skill and Agent Plugin. This project follows
[Semantic Versioning](https://semver.org).

## [Unreleased]

## [1.1.9] - 2026-10-14

### Added

- Add provider-native Codex/OpenAI and Cursor plugin archives alongside the
  Claude-native archive. All three copy the canonical Rainbrand Skill and use
  the same hosted MCP endpoint.
- Include the current OpenAI listing, review, and publication metadata in the
  Codex manifest for directory submission.

### Changed

- Align Claude and Cursor manifests with their current native plugin contracts
  and streamline installation guidance around the archive for each client.
- Generate provider manifests and MCP configurations from canonical Skill
  metadata, shared plugin copy, and one MCP endpoint constant so package files
  cannot drift.
- Validate exact provider archive members, manifest contracts, MCP parity,
  source bytes, release assets, and reproducible output.

### Removed

- Retire the root `plugin.json` manifest and `rainbrand.plugin.zip` portable
  distribution.

## [1.1.8] - 2026-10-13

### Added

- Restore `bloom.skill.zip` as a Bloom compatibility standalone Skill archive,
  generated from the canonical Skill with identity and domain substitutions.
  Both standalone variants carry the same current guidance and version.
- Package and validate both standalone archives as required release assets.
- Add `rainbrand.claude-plugin.zip` as a separate Claude-native distribution,
  with `.claude-plugin/plugin.json`, root `.mcp.json`, and the hosted Rainbrand
  MCP endpoint using transport `http`.
- Include the Rainbrand image in the native archive and reference it through
  the manifest's top-level `icon`. This fixes a non-behavioral presentation
  defect in the first native candidate.
- Add deterministic native packaging and validation for closed manifest fields,
  malformed MCP configs, exact archive members, Skill and image byte parity,
  and reproducible builds.

### Changed

- Clarify provider-specific installation: Claude-native plugin, ChatGPT Plugins
  Directory when listed, direct MCP for other clients or accounts without plugin
  support, and standalone Skill as an optional advanced fallback.
- Reserve portable/OpenAI ZIP upload/import for publishers, testers, and eligible
  workspace admins. Document the Desktop-only restriction for imported MCP
  plugins and the separate account authorization step after plugin installation.
- Preserve the portable Agent Plugins 1.0 layout and standalone Skill archive.
  All three distributions copy the single canonical Skill.
- Bump Skill metadata to 1.1.8 to maintain package version invariants; Skill
  guidance is unchanged.

## [1.1.7] - 2026-10-13

### Changed

- Search the connected Rainbrand tool catalog again when the task changes or a
  needed tool is not loaded. A loaded subset does not represent the full
  connection; public docs remain reference material.
- Route brand creation and onboarding from websites, Instagram, or files to
  `onboard_brand`.
- Keep the packaged Skill account-neutral: stable product context, connected
  discovery, and universal brand workflows. The live tools, descriptions, and
  schemas own available capabilities and their execution instructions.
- Keep plugin descriptions capability-neutral. Packaging does not infer the
  consuming account or encode account-specific generation workflows.
- Remove internal review, submission, and cross-repository release instructions
  from the public and bundled README.
- Generate both distribution archives from the canonical Skill and validate
  exact Skill-byte agreement between the source and both archives.

### Validation

- Package validation passes. Controlled live-client verification remains
  pending; package checks do not establish client behavior.

## [1.1.3] - 2026-10-13

### Changed

- Replace the temporary logo with the final Rainbrand icon.
- Update repository and download links to `trybloomai/rainbrand-skills`.
- Document direct ChatGPT workspace ZIP upload and manual updates, separately
  from optional public-directory publication.
- Rebuild both distribution archives.

## [1.1.2] - 2026-10-08

### Changed

- Add the Rainbrand icon and review walkthrough.

## [1.1.1] - 2026-10-07

### Changed

- Remove the placeholder asset README and allow the assets directory to remain absent until approved artwork is added, retaining validation for `assets/rainbrand-logo.png`.
- Restore the Skill's original documentation links and contract guidance with Rainbrand domains.
- Rebuild both distribution archives.

## [1.1.0] - 2026-10-07

### Changed

- Migrate the distribution identity from the preceding 1.0.6 release to
  Rainbrand: the plugin, MCP server, canonical Skill, install commands, and
  distribution archives now use `rainbrand`.
- Connect to `https://mcp.rainbrand.com/mcp` and use Rainbrand website, support,
  and legal URLs. Preserve the Skill's existing workflow guidance.
- Align review cases with live MCP tool names and document the account setup
  and conversation sequence needed to supply their IDs.
- Make both archives reproducible across time zones and umasks, with shared
  validation of source contents and metadata.
- Separate draft package validation from submission readiness. Approved artwork
  and a new walkthrough are still required before OpenAI submission.
- Support staged rollout with local install and archive paths, omitting optional
  repository metadata and unpublished download links. A later repository rename
  is optional housekeeping, not a submission gate.
- Document provider testing and Claude's native plugin compatibility limits.

### Removed

- Retire the preceding distribution's visual assets from the new package.
  Approved Rainbrand artwork is pending; no substitute icon is bundled.

## Earlier releases

History through 1.0.6 remains in the changelog at the v1.0.6 tag. Earlier tags,
releases, and their assets remain unchanged; 1.1.0 starts the Rainbrand
distribution history.
