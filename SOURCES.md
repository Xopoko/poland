# Poland sources

## Scope

`data/sources.json` is a registry of first-party authority locations and bounded
metadata. It is not a copied corpus of official pages and not a frozen statement
of law. Each source record names a publisher/authority, official-source tier,
canonical URL, page locator, jurisdiction, languages, topics, access mode,
access and verification dates, effective period when known, and freshness window.

Scenario records contain routing claims only and bind those claims to stable
source IDs. A material fact observed on a live page requires a v2 evidence
receipt with the exact locator, supported field IDs, effective period, access
date, and any unresolved official-source conflict. Narrative observations are
not accepted as claim records.

`data/digital-channels.json` is a routing catalog layered on the source registry.
It records public and protected surfaces, responsible access category, likely
authentication class, agent mode, hard stop points, and fields that must be
verified live. A channel record is descriptive metadata, not authority to enter
the service or evidence that a route applies to a particular person.

Tier meanings are narrow: `T0` is official legal text, `T1` is the competent
authority's own guidance, service, or registry, and `T2` is another official
institution's supporting explanation. A tier ranks provenance for a specific
claim; it does not prove that the claim applies to an individual.

The initial registry access date is 2026-08-20. A verification date records an
observation, not a guarantee that the page or procedure remains unchanged.

## Source contribution rules

A source change must:

1. use the competent authority or an official EU source for the matter it owns;
2. use a canonical HTTPS URL and explicit exact origin entries;
3. state the authority, jurisdiction, locality, languages, and access boundary;
4. record the date on which the source was checked;
5. avoid session URLs, personal query parameters, authenticated deep links, and
   copied personal examples;
6. include a synthetic validation case when routing or safety behavior changes;
7. receive human maintainer review before publication.

Fetched page content may produce a change report, but it must never edit legal or
procedural guidance, source records, manifests, or releases automatically. A
maintainer compares authority, dates, scope, transitions, and conflicts before
making a structured change.

## Reuse and licensing

Plugin-authored code, schemas, metadata structure, and explanatory text are
released under the repository MIT license. Linked official pages, authority
names, third-party marks, and external content remain subject to their publishers'
rights and terms. The plugin stores links and concise provenance metadata; it does
not grant a licence to reproduce an external page.

Do not add a full-page scrape, form corpus, translation corpus, image, logo, or
other substantial external content without a documented reuse right and review.

## Runtime behavior

Lookup uses packaged data offline. The optional source probe performs a bounded,
unauthenticated check of a packaged public source ID. It does not crawl, discover
new origins, update data, save a page body, or access a protected service.

Fast-changing channel facts include accepted filing route, actor, login and
signature method, attachments, exceptions, service availability, and transition
date. Recheck them on the channel's competent first-party source. Public
navigation pages may be evidence; authenticated dashboards, inboxes, drafts,
receipts, and personal records must never enter the evidence bundle.
