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

Use an API only when it is unauthenticated, officially documented by the responsible authority, and allowlisted in the source registry for public read-only access. Credentialed APIs are prohibited even with user consent. Respect rate limits and never infer that a browser backend is a supported public API.

## Evidence receipts

An evidence receipt should include source ID, exact HTTPS URL, authority, publisher, source tier, access time, structured result, stable locator, supported claim IDs, effective period when known, freshness state, and structured conflicts. Avoid free-form personal observations or inference fields. Hashing is optional; a hash proves captured content identity, not legal accuracy.

## Registry maintenance

When a URL, authority, access method, or effect changes, update the source record and its verification date together. Review references for source-ID drift. Keep superseded procedural claims out of hot guidance.
