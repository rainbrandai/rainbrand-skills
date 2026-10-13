# Changelog

Notable changes to the Rainbrand Skill and Agent Plugin. This project follows
[Semantic Versioning](https://semver.org).

## [Unreleased]

## [1.1.7] - 2026-10-13

### Changed

- Search the connected Rainbrand tool catalog again when the task changes or a
  needed tool is not loaded. A loaded subset does not represent the full
  connection; public docs remain reference material.
- Route brand creation and onboarding from websites, Instagram, or files to
  `onboard_brand`, with a controlled review case after account lookup.
- Update generation guidance to use current model tools and completed Briefs
  for supported image generation. Preserve the distinction between Brief-based
  image generation and requests where the caller supplies brand context.
- Document the six positive review cases, three negative cases, and the release
  order for keeping Hero's Skill copies aligned with this public source.
- Rebuild both distribution archives with the updated Skill and plugin metadata.

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
