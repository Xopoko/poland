# Source Methodology

## Authority order

Prefer sources in this order for the matter they own:

1. the current public, unauthenticated procedure page of the responsible Polish authority;
2. the competent voivodeship, gmina, school, inspectorate, or branch page;
3. an official EU source for cross-border rights;
4. an official public register or unauthenticated open-data API;
5. secondary material only as a discovery pointer, never as final evidence.

The registry contains first-party sources only. A `gov.pl` page is not automatically the owner of every linked procedure; preserve the named authority.

## Freshness

Compute staleness from `last_verified + freshness_days`. A stale record is a prompt to re-open the official page, not proof that the procedure changed. Use shorter windows for immigration, benefit periods, tax filing, digital-service rollout, and local appointments.

Do not reuse copied fees, processing times, benefit amounts, filing windows, or eligibility summaries. Read them live when the user needs them and attribute them to the exact page and observation date.

## Durable URL policy

Prefer authority landing pages over temporary announcements. Keep a news item only when it describes a current transition that the landing page does not yet explain. Never pin a session URL, search result URL containing personal data, or authenticated deep link.

## API policy

The bundled source probe and public-evidence workflows use only unauthenticated,
officially documented, allowlisted APIs. Respect rate limits and never infer that
a browser backend is a supported public API.

The plugin bundles no credentialed connector. If the host separately provides
an approved authenticated connector, its own policy and
`automation-playbook.md` govern task-scoped operation. The user handles secrets;
personal results stay outside public-source receipts and bundled plugin tools;
consequential mutations require action-time confirmation. Never improvise a
credentialed endpoint or send personal data to an unapproved API.

## Evidence receipts

An evidence receipt should include source ID, exact HTTPS URL, authority, publisher, source tier, access time, structured result, stable locator, supported claim IDs, effective period when known, freshness state, and structured conflicts. Avoid free-form personal observations or inference fields. Hashing is optional; a hash proves captured content identity, not legal accuracy.

Authenticated case data is not public-source evidence. It may inform the current
task after explicit scope authorization, but it must not be copied into an
evidence receipt or used to silently generalize a public rule.

## Registry maintenance

When a URL, authority, access method, or effect changes, update the source record and its verification date together. Review references for source-ID drift. Keep superseded procedural claims out of hot guidance.

## Reality Repair

Use `freshness --summary-only` for the global state, then filter by status or
topic. A repair item names the affected source/scenario, whether current claim
use is blocked, and one verification route. It never selects the legally correct
interpretation or updates `last_verified` automatically.

`source_probe` proves only bounded transport and captured representation state.
Browser/manual review must compare the material claim, authority, applicability,
effective period, and conflict wording. Preserve unresolved official conflicts;
repair the canonical registry and its regression together only after that review.
