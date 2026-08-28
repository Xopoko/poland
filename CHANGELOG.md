# Changelog

All notable public changes to Poland are recorded here. Source records carry
their own access and verification dates; this file describes release behavior.

## [Unreleased]

- Split Polish-citizen address registration from foreigner permanent-residence
  permits with citizenship applicability enforced by the router.
- Refreshed the CUKR and PESEL UKR deadline evidence and preserved the official
  source disagreement as explicit affected-group and legal-effect conflicts.
- Kept the Poland router implicitly discoverable in Codex while making the 32
  focused skills explicit-only catalog entries, reducing startup metadata
  pressure without removing any skill.

## [0.2.0] - 2026-08-21

- Replaced the map-shaped icon with a full-bleed open Polish flag ribbon and
  removed the secondary sparkle; prompt schema, provenance, manifest bindings,
  and small-icon validation now agree.
- Expanded the portfolio to 33 skills total: one router and 32 focused owners,
  adding civil life events, disability and accessibility, pensions and senior
  support, justice and legal aid, civic participation, utilities and
  environment, vehicles and road records, consular travel, and employment
  services.
- Expanded the dated coverage ledger to 135 official sources, 36 digital
  channels, 71 source-backed scenarios, 114 administrative terms, and all 16
  voivodeships. Added current MOS electronic-filing transitions, general free
  legal aid, foreign school-certificate recognition, vehicle, disability,
  pension, voter, court, energy-dispute, and municipal-waste routes.
- Superseded the release-0.1 blanket handoff with a staged human-in-the-loop
  operator contract for caller-owned Browser or Computer tools: explicit task
  scope, private user authentication, minimum transient record access,
  action-time confirmation, user-only signatures/attestations, and visible
  receipt verification.
- Added semantic operator playbooks for MOS, ePUAP, e-Deliveries, e-Tax Office,
  eZUS, IKP, CEIDG, praca.gov.pl, Empatia, mObywatel/voter services, and justice
  portals, with guided manual fallback instead of brittle stored selectors.
- Kept the bundled CLI and MCP server offline, read-only, and non-retentive;
  strict schemas and safety fixtures now distinguish public research,
  task-scoped assistance, confirmation-gated effects, and user-only controls.
- Added a telemetry-free host doctor that validates the full data bundle and
  performs a real MCP initialize/tools-list/ping plus `poland_overview` round
  trip. Added agent-assisted host-local launcher generation without committing
  machine paths.
- Declared all 33 skills and MCP companions for Codex, Claude Code, and Cursor;
  documented that pi installs skills only; tightened the npm package surface to
  exclude bytecode caches and include required runtime files.
- Reworked public onboarding for ordinary users, explicit non-government
  identity, opt-in-only installation, privacy boundaries, host discovery proof,
  updates, removal, and source-drift support.

- Expanded the official-source registry from 51 to 135 records and the life
  ontology from 23 to 71 source-backed scenarios. New coverage includes EU and
  purpose-specific residence, citizenship confirmation, civil status, PESEL
  security, PIT/PCC/inheritance tax, ZUS pensions and cash benefits, family and
  childcare support, disability/PFRON, foreigner healthcare and EKUZ, treatment
  search, school-certificate recognition, higher education, unemployment,
  housing and property, utilities and waste, vehicle administration, elections,
  courts/KRK, privacy/equal treatment, banking safety, legal aid and victim
  support, regulated professions, civil succession, Polish passports,
  technical inspections, vehicle OC, road tolls, local parking, and imported
  vehicle customs and excise.
- Expanded the Polish terminology registry from 47 to 114 terms and the digital
  channel catalog from 19 to 36 channels, including PESEL services, Your e-PIT,
  PFRON SOW, NFZ treatment dates, court and criminal-record services, land
  registers, CEPiK, voter and civil-status services, vehicle services, waste
  search, victim support, free-legal-aid booking, e-Konsulat, e-TOLL, and PUESC.
- Added the general Ministry of Justice free-legal-aid system alongside the
  foreigner-specific page, with current remote, accessibility, language and
  local-appointment facts left for live verification.
- Separated URE competence from provider, consumer-ombudsman and local-utility
  ownership; separated public BDO recipient search from gmina PSZOK rules; and
  separated foreign school-certificate recognition from NAWA higher-education
  recognition.
- Replaced blanket protected-service prohibitions with explicit
  `human_in_loop_operator` and `user_handoff_then_stop` metadata. The plugin
  still bundles no authenticated connector or credentials: user-controlled
  authentication, least-data scope and action-time confirmation remain required.
- Added lifecycle coverage, locality and deferred-edge documentation plus
  focused contract tests for official provenance, scenario ownership, digital
  channel uncertainty and operator-mode schema closure.

## [0.1.0] - 2026-08-20

- Published 24 focused skills for residence, mobility, identity, work, tax,
  social insurance, healthcare, housing, business, family, education, benefits,
  transport, consumer matters, documents, local services, protection, appeals,
  emergencies, digital government, case planning, and source verification.
- Added strict versioned datasets and schemas for 51 official sources, 19
  digital channels, 23 scenarios, 47 terms, 16 regions, and action boundaries.
- Added deterministic `candidate`, `undetermined`, and `not_applicable` routing
  with freshness, effective-period, and conflict gates.
- Added a standard-library CLI and a networkless, read-only stdio MCP server with
  stable response envelopes and input rejection.
- Added an isolated exact-origin public source probe with bounded metadata-only
  responses and no credentials or personal payloads.
- Added current MOS transition, EU Blue Card actor separation, first-weeks
  composition, and driving-licence timing distinctions from official sources.
- Established a strict non-retention and no-external-action contract: no login,
  personal-record access, submit, send, book, pay, upload, download, sign, call,
  or mutation even with consent.
- Added Codex, Claude Code, Cursor, pi, MCP, CI, public onboarding, support,
  security, privacy, source, and contribution surfaces.
