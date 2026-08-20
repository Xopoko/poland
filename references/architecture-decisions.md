# Poland architecture decisions

## ADR-001: Offline navigation with fail-closed external boundaries

- Contract: `architecture_intelligence.decision.v1`
- Status: accepted
- Owner: Poland plugin maintainers
- Review path: human review of every data, policy, interface, and publication
  change

### Context and forces

Poland procedures are time-sensitive, locally variable, and high consequence.
The plugin must help an agent route questions quickly without turning packaged
metadata into legal conclusions, collecting personal data, or gaining authority
over a government or commercial service. It must remain portable across Codex,
Claude Code, and Cursor and fit this repository's source/runtime separation.

### Considered options

1. Keep deterministic Python data, CLI, and a local read-only stdio MCP server;
   isolate the optional public-source probe and treat Browser use as caller-owned
   policy-limited verification.
2. Rewrite the runtime in Go and make a fixed MCP tool count an architecture
   target.
3. Add a full legal rules engine, six new legal datasets, signed data bundles,
   full interface localization, authenticated adapters, and a root Cursor
   manifest in the first release.

### Decision and rationale

Option 1 is accepted. The shared core and strict JSON contracts own deterministic
routing, freshness gates, provenance, and interface parity. CLI and MCP surfaces
use packaged data offline; the MCP process performs no network requests or file
writes. The source probe is a separate, bounded process for packaged public
source IDs and exact declared HTTPS origins.

No plugin surface may request or retain personal data. The plugin never logs in,
reads an authenticated session or personal record, submits, sends, books, pays,
uploads, downloads, signs, calls, uses a credentialed API, or changes external
state, even with consent. A caller-owned Browser or Computer tool may verify a
visible public, unauthenticated official page or open one exact official landing
page and then must stop. Website content remains untrusted evidence.

The following review suggestions are deliberately not release gates:

- a Go rewrite is deferred until measured reliability, packaging, or performance
  evidence shows that Python is the limiting factor;
- an exact MCP tool count is rejected as an architecture goal; semantic coverage,
  strict contracts, parity, and least authority are the fitness criteria;
- a root Cursor manifest is rejected because this repository's supported Cursor
  integration consumes `skills/` directly through its installer;
- a complete legal rules engine and six-dataset expansion are deferred until
  authoritative scope, update ownership, and regression evidence exist;
- signed bundles and full interface localization are deferred until a concrete
  distribution threat or supported locale contract justifies their cost.

### Consequences

The plugin can provide bounded navigation, checklists, freshness status, and
claim-level provenance with low runtime authority. It cannot complete a personal
workflow, inspect an account, decide eligibility, or guarantee current law.
Callers must perform final authority interactions themselves. Network freshness
verification is explicit and separated from offline planning.

### Affected components and migration

This decision governs manifests, skills, packaged data and schemas, the shared
core, CLI, MCP server, source probe, privacy/security terms, and host guidance.
Legacy case-file commands, authenticated-read guidance, confirmation-gated
effects, and Browser/Computer executor claims are removed rather than migrated.
No global install or runtime cache is changed by the source migration.

### Fitness functions

- schema tests reject unknown fields, wrong types, personal-data-shaped inputs,
  stale evidence, and unresolved conflicts;
- CLI and MCP contract tests prove equivalent results and stable error codes;
- static tests prove that MCP imports cannot perform network or file writes;
- safety tests reject every prohibited external effect regardless of consent;
- source-probe tests cover exact origin, IDNA normalization, redirects, final URL,
  response bounds, and download responses;
- repository validation proves manifest parity, source routing, ASCII/public-safe
  content, and cross-host packaging.

### Ownership exception and revisit triggers

There is no runtime exception to the no-personal-data or no-external-action
boundary. A proposal to expand it requires a new ADR, explicit owner approval,
an isolated threat model, host-specific enforcement, and tests before any public
claim.

Revisit the deferred items only when measured failures, a supported host contract,
a maintained authoritative dataset, a verified distribution threat, or an
approved locale requirement supplies new evidence. Review this ADR before every
major version and whenever runtime topology, data ownership, or host integration
changes.
