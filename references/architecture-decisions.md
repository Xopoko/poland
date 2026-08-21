# Poland architecture decisions

## ADR-001: Offline navigation with fail-closed external boundaries

- Contract: `architecture_intelligence.decision.v1`
- Status: superseded by ADR-002
- Owner: Poland plugin maintainers
- Superseded: 2026-08-20

### Context

The first public release deliberately limited all authenticated and
state-changing work to a user handoff. That made the packaged CLI and MCP
surfaces easy to reason about, but it prevented the main product outcome: an
authorized agent helping a person complete ordinary Polish administrative work
through a caller-provided Browser or Computer capability.

### Original decision

Keep the packaged Python data, CLI, MCP server, and source probe offline or
public-read-only. Stop before every authenticated or state-changing step.

### Reason for supersession

The boundary confused two different runtimes. The plugin-owned CLI and MCP
processes should remain local and non-retentive, but the calling agent may
already have a separately installed interactive browser with its own consent
and security controls. A blanket prohibition made the product materially less
useful without reducing the authority of those caller-owned tools.

The retained parts of ADR-001 are the official-source-first data model,
deterministic offline core, strict schemas, provenance, freshness gates, and
separation of the bounded public-source probe.

## ADR-002: Layered life-service knowledge with an authorized human-in-the-loop operator

- Contract: `architecture_intelligence.decision.v1`
- Status: accepted
- Owner: Poland plugin maintainers
- Review path: maintainer review of every policy, data, interface, and release
  change; security review for any new executable connector
- Decision date: 2026-08-20

### Context and forces

Polish public services span national authorities, voivodeships, powiats,
gminas, courts, social-insurance institutions, healthcare, schools, utilities,
and EU channels. Rules, forms, fees, deadlines, office practice, and portal
labels change. A useful agent must cover far more than immigration while still
distinguishing general orientation from a legal, medical, tax, or eligibility
decision.

Most users should be able to say what they need in ordinary language. They
should not have to understand the repository, run a CLI, or know which agency
owns the problem. When a supported host supplies Browser or Computer use, the
agent should be able to continue through a user-authorized session instead of
abandoning the user at the first login page.

At the same time, the plugin must not collect credentials, silently widen a
task, retain personal records, guess at irreversible effects, or claim that a
volatile web interface has permanent exact click coordinates.

### Considered options

1. Preserve the release-0.1 blanket handoff before every authenticated or
   external action.
2. Bundle a browser driver, credentials, fixed selectors, and direct service
   integrations in the plugin.
3. Keep plugin-owned tools offline and non-retentive, but teach a caller-owned
   interactive agent a staged human-in-the-loop operating contract, semantic
   live-page navigation, official channel ownership, and action checkpoints.
4. Put the entire country guide into one very large hot-path skill.

### Decision and rationale

Option 3 is accepted. Option 1 does not meet the product outcome. Option 2
would create an unnecessary credential, maintenance, and supply-chain surface.
Option 4 would waste context and make routing less reliable.

The product uses progressive disclosure:

- one router recognizes a broad life event and selects a focused owner skill;
- focused skills contain short operating guidance and route to deeper
  references only when needed;
- structured source, channel, scenario, terminology, region, and action-policy
  datasets provide repeatable lookup and validation;
- shared references explain cross-domain procedures and escalation paths;
- the local CLI and MCP server expose deterministic, non-identifying planning
  data without browsing, authentication, persistence, or external effects;
- an independently installed Browser or Computer capability may operate the
  visible official service only under the staged contract below.

The interactive contract has four gates:

1. **Scope.** The user authorizes a concrete task and target service. The agent
   may research public official pages and prepare non-secret material.
2. **Authentication handoff.** Capture and interaction pause while the user
   enters credentials, OTPs, PINs, identity-provider choices, CAPTCHAs, or
   signatures. The agent never asks for those values in chat.
3. **Protected assistance.** After the user says the session is ready, the
   agent may inspect only records needed for the scoped task, navigate by
   current visible labels and page state, and fill reviewable fields. It does
   not retain personal content in plugin data or logs.
4. **Action-time confirmation.** Immediately before submit, send, book, cancel,
   upload, download, create, change, or payment initiation, the agent shows the
   target, material fields, effect, and known cost or deadline and obtains a
   fresh explicit confirmation. A prior broad instruction is not that final
   confirmation.

Legally meaningful attestations and signatures, final payment authorization,
CAPTCHAs, emergency calls, and any action that a service explicitly reserves
to the person remain user-only. The agent verifies the visible receipt or
final state before reporting completion.

The plugin does not promise fixed click sequences. Playbooks name the official
landing page, expected semantic phases, fields to verify, checkpoints, and
success evidence. The agent re-discovers controls from the live page and stops
when the page, authority, identity, cost, or effect differs materially from the
source-backed expectation.

### Consequences and tradeoffs

The agent can serve as a practical home-administration assistant instead of a
link directory. It can reduce repeated research and help complete many online
workflows without taking custody of credentials or granting unattended
authority.

This model depends on the calling host's interactive-tool security and on a
present user for protected steps. Some procedures still require biometrics,
original documents, a medical examination, a wet signature, an official
appointment, or another in-person act. Coverage is broad but never represented
as a guarantee that every Polish service or every local practice is captured.

Semantic live navigation is more resilient than fixed selectors, but it may be
slower and must fail closed when the page is ambiguous. Adding more structured
coverage increases maintenance work, so every claim needs an owner, official
source, verification date, and freshness rule.

### Affected components and migration

This decision governs manifests, README and legal notices, all skills and
references, action boundaries, digital-channel metadata, scenario checkpoints,
the shared core, CLI/MCP response contracts, host guidance, and tests.

Migration from 0.1 replaces blanket prohibition language with the staged
operator model. Existing `stop_before` scenario values become mandatory
pause-and-classify checkpoints: continue only when the action policy permits it
and the required task-scope or action-time confirmation is present. Otherwise
hand control to the user or a qualified professional.

No credential store, browser binary, Computer adapter, authenticated API token,
or personal case database is added. A future executable connector requires a
separate ADR and threat model.

### Fitness functions

- schema and contract tests reject unknown fields, wrong types, unresolved
  source references, stale decisive evidence, and personal-data-shaped inputs
  to packaged tools;
- policy fixtures cover public research, authentication handoff, scoped record
  access, field preparation, action-time confirmation, user-only actions, and
  receipt verification;
- every protected digital channel declares an agent mode, authentication
  boundary, stop conditions, live-verification fields, and official sources;
- scenario and source coverage tests require every focused owner skill to be
  reachable and every claim to resolve to a dated official source;
- CLI and MCP tests prove stable envelopes, parity, bounded outputs, no
  persistence, and no network access from the MCP process;
- the source probe remains exact-origin, unauthenticated, bounded, and separate
  from protected browsing;
- host doctor checks prove the configured MCP launcher can complete a real
  handshake on each advertised host path;
- release validation scans public files for credentials, personal examples,
  local paths, stale blanket-denial wording, and unsupported completeness
  claims;
- scenario-based evaluation exercises ordinary-language tasks across residence,
  family, work, health, benefits, tax, housing, vehicles, civil events,
  disability, senior support, justice, civic life, utilities, and emergencies.

### Ownership exceptions and revisit triggers

Only maintainers may change the action taxonomy or introduce a connector.
Cross-owned host integration needs review from that host adapter's owner.
Source corrections require an official primary source and a verification date;
case-specific professional advice is never encoded as a universal rule.

Revisit this ADR when a supported host changes its confirmation or secret-entry
contract, a service publishes a stable machine interface, a recurring workflow
cannot be expressed by semantic phases, measured routing failures show that the
portfolio split is wrong, or a new threat invalidates the current separation.
Review it before every major release.
