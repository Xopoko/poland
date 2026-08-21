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
  pages without credentials. It bundles no Browser or Computer adapter,
  authenticated connector, credential store, or external-action executor.
- Skill instructions may orchestrate a caller-owned Browser, Computer tool, or
  approved connector when that capability is installed and its own policy
  permits the task. If none is available, give semantic manual steps and stay
  with the user through each checkpoint.
- Public research may be autonomous. Authentication, account selection, secret
  entry, CAPTCHA, and 2FA are user-only; pause capture and yield control before
  they begin. Resume only after the user says the protected session is ready.
- After explicit task-scoped authorization, inspect only the personal records
  needed for the named task and fill only necessary, reviewable fields. Keep
  personal values out of the bundled CLI, MCP, receipts, tests, logs, and repo.
- Obtain fresh action-time confirmation against a visible summary before any
  submit, send, booking change, payment initiation, upload, download, account or
  record change, or other consequential external effect. A broad instruction at
  task start is not confirmation for every later action.
- Treat scenario and channel `stop_before` values as mandatory pause-and-classify
  checkpoints. Continue only when the concrete action is allowed and its scope
  or action-time checkpoint has completed; user-only and unresolved actions stop.
- The user performs signatures, legal attestations, final payment authorization,
  irreversible destructive actions, and any step whose truth or legal effect
  only the user can accept. Never bypass controls, forge a declaration, obscure
  costs, or claim completion without a visible official receipt or final state.

## Repository Shape

- `skills/` contains focused Agent Skills; `skills/poland/` is the router.
- `data/` and `schemas/` contain versioned public routing contracts.
- `references/` contains longer source and operating guidance.
- `lib/`, `scripts/`, and `mcp/` contain deterministic standard-library tools.
- `tests/` contains public-safe synthetic fixtures and regression coverage.
- `.agents/plugins/marketplace.json` keeps standalone Codex discovery opt-in;
  `.codex-plugin/`, `.claude-plugin/`, `.cursor-plugin/`, and `package.json`
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
python scripts/poland.py validate --as-of 2026-08-21
python -m unittest discover -s tests
python scripts/token_report.py
```

For a release, also validate a clean checkout on Windows and Linux, inspect the
final diff for personal data and secrets, and verify installation separately on
each supported host. Publication never grants installation or external-action
authority.
