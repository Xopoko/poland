## Outcome

Describe the reusable user outcome and the failure mode this change fixes.

## Evidence

- Competent official source and exact locator:
- Access date and effective period:
- Conflicts, uncertainty, or freshness impact:

## Safety Boundary

Confirm that this change does not add personal-data handling, authentication,
personal-record access, submission, sending, booking, payment, upload, download,
signing, calling, credentialed APIs, or external mutation.

## Validation

- [ ] `python scripts/validate_package.py`
- [ ] `python scripts/poland.py validate --as-of 2026-08-21`
- [ ] `python -m unittest discover -s tests`
- [ ] `python scripts/token_report.py`
- [ ] No personal data, credentials, private paths, generated caches, or copied page bodies are included.
