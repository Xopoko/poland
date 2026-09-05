# Contributing to Poland

Contributions should strengthen a reusable Poland workflow while preserving
official-source provenance, privacy, portability, and the human-in-the-loop
operator boundary.

1. Open or reference the matching issue type: bug, source update, or workflow
   request.
2. Keep skill routing narrow; put long material in `references/`.
3. Use synthetic examples and fixtures only.
4. Update data, schema, behavior, documentation, and focused tests together.
5. Run the validation commands below and include the results in the pull request.

Never include a real person's case, document, identifier, address,
correspondence, credential, session data, screenshot, or unredacted log.

## Source Changes

A material source change must:

1. identify the competent Polish authority or official EU source;
2. record the canonical HTTPS URL, access date, claim locator, effective period
   when known, and unresolved conflict or uncertainty;
3. keep authenticated pages and personal records outside the evidence bundle;
4. add or update a synthetic regression case;
5. explain effects on routing, freshness, privacy, and safety boundaries;
6. receive human maintainer review before publication.

Fetched page content may identify drift but must never edit guidance or publish a
release automatically.

## Capability Boundary

Do not add a credential store, authenticated connector, hidden installation,
telemetry, background service, unattended mutation, fixed portal selector, or
plugin-owned Browser/Computer executor. The bundled CLI and MCP server stay
offline, read-only, and non-retentive.

Skills may guide a separately installed caller-owned Browser or Computer tool
under `references/automation-playbook.md`: explicit task scope; private
user-controlled authentication; minimum transient record access; fresh
action-time confirmation before every external effect; user-controlled
signatures, attestations, CAPTCHA, and final payment authorization; and visible
receipt verification. A new executable connector or broader authority requires
a reviewed ADR, threat model, schemas, tests, and maintainer approval.

## Validation

```bash
python scripts/validate_package.py
python scripts/poland.py validate
python -m unittest discover -s tests
python scripts/token_report.py
```

Validation uses the current UTC date by default. Use `--as-of YYYY-MM-DD` only
when intentionally inspecting a historical snapshot; later source verification
dates are correctly rejected for that earlier date.

Also inspect the final diff for secrets, private paths, personal data,
unsupported capability claims, generated artifacts, and unreviewed source
changes. Publication and installation remain separate explicit actions.
