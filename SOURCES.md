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
authentication class, agent mode, mandatory pause-and-classify checkpoints, and fields that must be
verified live. A channel record is descriptive metadata, not authority to enter
the service or evidence that a route applies to a particular person.

The 2026-08-28 coverage ledger contains 141 official-source records, 37 digital
channels, 72 source-backed scenarios, 114 Polish terms, and all 16 voivodeships.
Counts are regression anchors, not a completeness score. Coverage is organized
around resident life events: entry and stay; EU mobility and citizenship;
identity and civil status; work, unemployment and business; tax and social
insurance; healthcare; family, education and disability; housing, utilities and
vehicles; consumer and banking protection; courts, legal aid and rights; civic
participation; emergencies, victim support, death and inheritance.

Every scenario preserves uncertainty and names facts needed to select the
current authority. Every added service record is tied to an official source with
access and verification dates. National guidance does not prove the competent
gmina, powiat, voivode, court, provider or appointment system. Those must be
resolved from the current local authority or BIP page at action time.

Tier meanings are narrow: `T0` is official legal text, `T1` is the competent
authority's own guidance, service, or registry, and `T2` is another official
institution's supporting explanation. A tier ranks provenance for a specific
claim; it does not prove that the claim applies to an individual.

The initial registry access date is 2026-08-20. A verification date records an
observation, not a guarantee that the page or procedure remains unchanged.

`human_in_loop_operator` means a caller-owned Browser or Computer capability may
inspect or fill the named protected surface after explicit task authorization.
The plugin bundles no authenticated connector, credential broker or standing
authority. Secret entry, identity-provider confirmation, signatures, legal
declarations, final payment authorization, withdrawals, and irreversible
invalidation stay with the user. Submit, send, book, change an official record,
upload or download, and payment initiation pause for a visible action-time
confirmation. `user_handoff_then_stop` is used where the user must personally
cross the identity, signature or safety boundary. Credentialed APIs remain
prohibited until an approved connector and contract exist.

## Coverage limits and local discovery

Some edges are deliberately live rather than frozen: municipal waste and PSZOK
rules, water and district heating, social-housing stock, childcare recruitment,
local parking and toll systems, provider slots, court calendars and local
programme budgets. The registry records official national ownership evidence
and the BIP discovery route, then requires current locality verification.

Civil succession can involve a notary, civil court and tax office; the bundle
therefore provides `civil-succession-route` as a source-backed classification
path while refusing to claim a single inheritance procedure or choose heirs,
shares, acceptance, rejection, applicable law or venue. Foreign-issued passports
route to their issuing state's current consular authority. Recognition of a foreign school certificate stays
undetermined until document, issuing-country, agreement, recipient and purpose
facts separate automatic recognition from an education-superintendent route.
Energy billing and contract disputes are not assigned to URE merely because URE
publishes consumer guidance; provider, territorial URE, negotiation coordinator
and consumer-ombudsman competence must be classified live.

Vehicle coverage separates technical inspection, public OC lookup, e-TOLL,
concession tolls, local public parking, private parking, non-EU customs,
intra-EU acquisition, excise and registration. Exact route, vehicle combination
and `target_date` stay live facts; the known e-TOLL transition source is
effective from 2026-09-21. No frozen rate, insurer recommendation, customs or
tax classification, valuation, exemption, coverage or roadworthiness conclusion
is stored.

The Ukrainian temporary-protection transition is intentionally split across
procedure-specific records. `udsc-ukraine-status-transition-2026` describes the
general change from 5 March 2026; `udsc-cukr-procedure` owns the CUKR route;
`udsc-pesel-ukr-passport-update-2026` owns the declaration-based UdSC notice and
`gov-pesel-ukr-passport-update-2026` supplies the broader public outreach notice.
Their affected-group scope and legal-effect certainty remain an explicit
scenario conflict, while `sejm-ukraine-transition-act-2026` Articles 25-26 distinguish the
31 August declaration-based identity-confirmation group from a separate 60-day
document route. Neither deadline may be presented as universal for every PESEL
UKR holder. `mos-permanent-residence` separately owns national permanent
residence and must not be replaced by EU long-term-resident or citizenship
guidance. All dates, affected groups, form mechanics, consequences and local
office instructions remain live-verification fields.

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
unauthenticated check only when a packaged source is `public_read_only`.
`public_read_only_handoff` is routed to Browser or manual official-page review.
Neither route crawls, updates registry facts, saves a page body, or treats HTTP
success as semantic or legal revalidation.

Fast-changing channel facts include accepted filing route, actor, login and
signature method, attachments, exceptions, service availability, and transition
date. Recheck them on the channel's competent first-party source. Public
navigation pages may be evidence; authenticated dashboards, inboxes, drafts,
receipts, and personal records must never enter the evidence bundle.
