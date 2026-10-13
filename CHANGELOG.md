# Changelog

Notable changes to the Rainbrand Skill and Agent Plugin. This project follows
[Semantic Versioning](https://semver.org).

## [Unreleased]

## [1.1.8] - 2026-10-13

### Added

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

- Define gated plugin-first launch guidance: Claude-native plugin installation,
  ChatGPT Plugins Directory installation once published, direct MCP for other
  clients or accounts without plugin support, and standalone Skill only as an
  optional advanced fallback. Keep the current quickstart direct-MCP-first
  until each provider's artifact and release path pass live validation.
- Restrict portable/OpenAI ZIP upload/import guidance to publishers, testers,
  and eligible workspace admins. Document imported MCP plugins as Desktop-only;
  verify the directory release path's exact surfaces and account requirements
  independently. Installing a plugin does not authorize its MCP connection.
- Preserve the portable Agent Plugins 1.0 layout and standalone Skill archive.
  All three distributions copy the single canonical Skill.
- Bump Skill metadata to 1.1.8 to maintain package version invariants; Skill
  guidance is unchanged. Hero's mirrored Skill copies must be synchronized to
  the canonical 1.1.8 bytes before release.

### Validation

- A live tester reports that the v1.1.8 candidate uploaded successfully in
  Claude as Rainbrand with exactly one Skill and one Connector. That candidate
  omitted the image and showed the generic plug glyph.
- Re-upload the final package to confirm the Rainbrand image. OAuth sign-in
  and connected-tool discovery remain pending; successful upload alone does
  not establish those behaviors.

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
