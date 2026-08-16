# Changelog

## 0.3.2 - 2026-07-22

### Fixed

- **P0**: Replaced Anthropic/Claude platform documentation references in `official-evidence-map.md` with general AI agent skill engineering best practices, eliminating irrelevant external platform dependency.
- Shortened `SKILL.md` frontmatter `description` from ~80 words to ~30 words for faster Agent match accuracy.

### Added

- Added SDK version baseline (`coze-coding-dev-sdk@0.7.24`) annotation to `capability-map.md` resource routing matrix, with runtime verification guidance.
- Added specific numeric limits (CPU, memory, disk, storage quotas, TTS/ASR constraints, video duration, etc.) to `coze-limit-boundaries.md`, replacing vague descriptions with measured values from the test report.
- Added Mermaid decision flowchart to `agent-routing-rules.md` for visual routing guidance.
- Added 2D selection decision matrix (content type × deployment mode) to `templates/single-html/catalog.md`.
- Added code-level BFF proxy and S3 storage pattern implementations to `SKILL.md` Guardrails section.
- Added bilingual (Chinese/English) annotations to key SKILL.md section headers.

## 0.3.0 - 2026-07-15

### Added

- Added a complete single-HTML and iframe delivery workflow with default output `dist/index.single.html`.
- Added source-mode detection for deployed URL, static build, Vite SPA, and full-stack/Next.js projects.
- Added eight single-HTML templates: full-screen iframe, app-shell iframe, split intro+app, cover-launch app, editorial image-text, visual story, course article, and gallery showcase.
- Added template catalog and JSON config examples so an Agent can present several schemes before implementation.
- Added guidance for generating image assets with the current Coze Coding built-in image integration, while allowing a user-selected Coze image skill/prompt standard to control the image-generation subtask.
- Added iframe security/compatibility checks for CSP `frame-ancestors`, `X-Frame-Options`, HTTPS, authentication cookies, sandbox, and feature permissions.
- Added static-bundling compatibility rules and explicit fallback to iframe wrapping for server-dependent applications.
- Added `single_html_tool.py` with `list-templates`, `inspect`, `render`, `bundle-static`, and `validate` commands.
- Added regression tests and eval cases for URL wrappers, image-text pages, and static bundle fallback behavior.

### Changed

- Expanded Agent trigger matching to include single HTML, iframe, 百宝箱, image-text pages, URL full-screen embeds, and `dist/index.single.html`.
- Strengthened progressive disclosure: single-HTML details live in dedicated docs/templates instead of expanding the core skill indefinitely.
- Updated capability wording to separate official Coze capabilities, PDF-based environment observations, and runtime-dependent wrappers/model IDs.
- Extended package validation to require the single-HTML catalog, templates, tool, tests, and eval coverage.

### Fixed

- Prevented the skill from claiming that Next.js API routes, database/auth, or other server-side functionality can be preserved inside one standalone HTML file.
- Prevented temporary signed object-storage URLs from being treated as durable embedded image assets.
- Added fail-closed checks for unsupported local module imports during generic static inlining.

## 0.2.0 - 2026-07-09

- Added precise trigger conditions, evidence map, limits, routing rules, scope ladder, evals, and project-audit tooling.
