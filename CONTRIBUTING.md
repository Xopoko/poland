# Contributing to Poland

Contributions should strengthen a reusable Poland workflow while preserving
official-source provenance, privacy, portability, and the no-external-action
boundary.

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

Do not add login, authenticated-session reading, personal-record inspection,
submission, sending, booking, cancellation, payment, upload, download, signing,
calling, credentialed APIs, telemetry, hidden installation, background services,
or any other external mutation. Consent does not expand this boundary.

## Validation

```bash
python scripts/validate_package.py
python scripts/poland.py validate --as-of 2026-08-20
python -m unittest discover -s tests
python scripts/token_report.py
```

Also inspect the final diff for secrets, private paths, personal data,
unsupported capability claims, generated artifacts, and unreviewed source
changes. Publication and installation remain separate explicit actions.
