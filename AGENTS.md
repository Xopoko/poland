# Agent Guidance

Poland is the canonical public source for an official-source-first skill system
for life and administration in Poland. Keep it useful to ordinary agent users,
portable across Codex, Claude Code, Cursor, pi, and compatible Agent Skills
hosts, and safe for public collaboration.

## Repository Role

- This repository owns the editable plugin source and releases.
- `https://github.com/Xopoko/plug-n-skills` may advertise and install an
  immutable reviewed revision, but must not maintain a second editable copy.
- Personal cases, documents, credentials, screenshots, and account data never
  belong in this repository.

## Product Boundary

- Use only non-identifying categories and public source IDs in plugin inputs.
- Prefer the competent Polish authority or an official EU source, record access
  and verification dates, and preserve uncertainty and conflicts.
- The plugin may inspect packaged data offline and probe allowlisted public
  pages without credentials. It does not bundle an authenticated connector.
- Never log in, read a personal record, enter personal data, submit, send, book,
  cancel, pay, upload, download, sign, call, or change external state. Consent
  and confirmation do not expand this boundary.
- An exact official landing page may be opened for the user; stop immediately
  after the handoff.

## Repository Shape

- `skills/` contains focused Agent Skills; `skills/poland/` is the router.
- `data/` and `schemas/` contain versioned public routing contracts.
- `references/` contains longer source and operating guidance.
- `lib/`, `scripts/`, and `mcp/` contain deterministic standard-library tools.
- `tests/` contains public-safe synthetic fixtures and regression coverage.
- `.codex-plugin/`, `.claude-plugin/`, `.cursor-plugin/`, and `package.json`
  describe the same release for supported hosts.

## Authoring Rules

- Keep repository text in English and ASCII unless exact official terminology
  requires another script.
- Never copy a personal case or a full official webpage into tracked fixtures.
- Keep skill entrypoints concise and route deeper material to plugin files via
  `$PLUGIN_ROOT`; do not assume a working directory.
- A material source change needs a locator, access date, scope, effective period
  when known, conflict review, synthetic regression coverage, and human review.
- Keep the CLI and MCP server networkless and read-only. Keep the optional
  source probe separate, allowlisted, bounded, and unauthenticated.
- Align versions and shared metadata across every package surface.

## Validation

Run before committing:

```bash
python scripts/validate_package.py
python scripts/poland.py validate --as-of 2026-08-20
python -m unittest discover -s tests
python scripts/token_report.py
```

For a release, also validate a clean checkout on Windows and Linux, inspect the
final diff for personal data and secrets, and verify installation separately on
each supported host. Publication never grants installation or external-action
authority.
