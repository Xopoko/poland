# Life Events and Services Map

Use this map when a resident's request is broader than one institution. It
connects ordinary-language life events to focused skills, scenario IDs,
official-source IDs, local ownership, and protected channels. It is a routing
map, not a statement that a person qualifies or that every listed step applies.

Always resolve the current locality and exact outcome. National guidance does
not prove which gmina, powiat, city with powiat rights, voivode, court, provider,
or local programme owns an individual step. Apply `automation-playbook.md` and
`portal-operator-playbooks.md` for hands-on portal work.

## Birth, parenthood, and civil records

- Owner: `poland-civil-life-events`; compose with `poland-family-education`,
  `poland-identity`, and `poland-benefits-support` only when those outcomes are
  requested.
- Scenarios: `birth-registration`, `family-childcare-benefits`, and
  `first-address-and-pesel`.
- Sources: `gov-birth-registration`, `gov-civil-record-copy`, `gov-pesel-foreigners`,
  `active-parent`, and the relevant local civil-registry or gmina source.
- Separate birth registration, obtaining a record copy, parentage, PESEL,
  address registration, health coverage, benefits, and consular registration.
  One event does not make them a universal sequence.
- The person who may report the birth, foreign-document route, parentage
  question, deadline, and local office need live verification. Legal parentage
  or family-status disputes require qualified help.

## Marriage, name, and foreign civil status

- Owner: `poland-civil-life-events`; compose with `poland-foreign-documents`.
- Scenario: `civil-marriage-and-name-change`.
- Sources: `gov-civil-marriage`, `gov-name-change`, `gov-civil-record-copy`,
  `apostille`, and `sworn-translator-list`.
- Separate the capacity-to-marry evidence, ceremony, foreign-record use,
  translation/legalization, name effect, and later record or document changes.
- Verify citizenship categories, event country, civil status, receiving
  authority, interpreter need, and whether personal appearance or original
  documents are required.

## Death, funeral, survivor support, and succession

- Owner: `poland-civil-life-events`; compose with `poland-pensions-seniors`,
  `poland-social-insurance`, `poland-tax`, and `poland-justice-legal-aid`.
- Scenarios: `death-and-funeral-route`, `retirement-survivor-pension`, and
  `inheritance-and-donation-tax`.
- Sources: `gov-death-registration`, `zus-funeral-benefit`,
  `zus-disability-survivor-pensions`, `tax-inheritance-donations`, and
  `gov-sd-z2`.
- Registration, burial, funeral-cost support, survivor pension, inheritance
  title, debt, notarial or court succession, and tax reporting have different
  owners and clocks.
- Never infer heirs, ownership, debt acceptance, tax treatment, or benefit
  entitlement. Preserve exact user-stated dates and escalate individualized
  succession choices.

## Disability, accessibility, and care

- Owner: `poland-disability-accessibility`; compose with `poland-healthcare`,
  `poland-benefits-support`, `poland-social-insurance`,
  `poland-family-education`, or `poland-local-services` as needed.
- Scenarios: `adult-disability-route`, `child-disability-route`,
  `disability-support-and-pfron`, and `education-support-needs`.
- Sources: `gov-disability-determination-adult`,
  `gov-disability-determination-child`, `gov-disability-parking-card`,
  `gov-supporting-benefit`, `pfron-sow`, and `education-psychological-counselling`.
- Keep disability-status determination, ZUS incapacity, medical treatment,
  education support, parking card, accessibility complaint, local care, and
  PFRON programme funding separate.
- Programme calls, budgets, evidence, medical decisions, and competent local
  teams change. Never diagnose or decide degree, capacity, support level, or
  entitlement.

## Pensions, sickness, maternity, care, and senior support

- Owners: `poland-pensions-seniors`, `poland-social-insurance`, and
  `poland-benefits-support`.
- Scenarios: `retirement-survivor-pension`,
  `sickness-maternity-care-benefit`, and `senior-or-home-care-support`.
- Sources: `zus-pensions`, `zus-disability-survivor-pensions`,
  `zus-cash-benefits`, `gov-social-assistance`, and the relevant EU social-
  security coordination source.
- Identify pension or benefit type, applicant role, insured periods, foreign
  insurance countries, event date, medical-evidence category, and locality.
- A visible eZUS record is not a formal entitlement decision. Cross-border work
  history and care needs may change the competent institution and evidence.

## School, university, and foreign education documents

- Owner: `poland-family-education`; compose with
  `poland-foreign-documents`, `poland-disability-accessibility`, and
  `poland-stay-residence` only when relevant.
- Scenarios: `school-enrolment`, `education-support-needs`, and
  `higher-education-route`.
- Sources: `education-foreign-children`,
  `education-school-certificate-recognition`, `higher-education-foreigners`,
  and `nawa-recognition`.
- Separate ordinary school admission, language/support arrangements, school-
  certificate recognition, higher-education admission, and academic or
  professional recognition.
- Keep recognition undetermined until document country, agreement category,
  recipient, level, and intended use distinguish automatic recognition from an
  education-superintendent, NAWA, university, or professional route.

## Employment office and unemployment services

- Owner: `poland-employment-services`; compose with
  `poland-work-authorization`, `poland-employment-rights`, and
  `poland-social-insurance` when their separate questions arise.
- Scenario: `unemployment-registration`.
- Sources: `gov-unemployment-registration`, `praca-gov-pl`, and the competent
  powiat labour-office source.
- Separate jobseeker or unemployed registration, benefit questions, employer-
  side work authorization, employee claims, training, and vacancy services.
- Verify powiat competence, end-of-work date, insurance history, current work
  authorization basis, and whether the user seeks registration, a benefit, or
  only employment support.

## Housing, property, utilities, and waste

- Owners: `poland-housing` and `poland-utilities-environment`; compose with
  `poland-consumer-banking`, `poland-tax`, or `poland-justice-legal-aid` for
  disputes, tax, or title issues.
- Scenarios: `housing-dispute`, `housing-assistance`,
  `property-register-and-tax`, and `utilities-and-waste`.
- Sources: `gov-social-assistance`, `land-registers`, `ure-household-energy`,
  `ure-consumer-disputes`, `gios-waste-recipients`, and the current gmina,
  provider, territorial URE, or consumer-ombudsman source.
- Separate landlord disputes, housing assistance, ownership or land-register
  questions, local property tax, provider billing, technical outage,
  disconnection, energy dispute, municipal waste declaration, and PSZOK.
- Do not assume URE owns an invoice or contract dispute. Water, district heat,
  waste schedules, charges, housing stock, and local complaint routes require
  live locality discovery.

## Vehicles, licences, and road records

- Owners: `poland-vehicles-road` and `poland-transport-driving`.
- Scenarios: `vehicle-registration-and-transfer`,
  `penalty-points-and-vehicle-records`, `private-transaction-tax`, and
  `driving-or-rail-problem`.
- Sources: `gov-vehicle-registration`, `gov-vehicle-transfer-notice`,
  `cepik-services`, `gov-driving-licence-exchange`, `drivers-act-consolidated`,
  `tax-pcc`, and `gov-pcc-filing`.
- Separate licence validity or exchange, owner registration, acquisition or
  disposal notice, insurance, inspection, vehicle record, penalty record, and
  transaction tax.
- Verify ordinary-residence facts, vehicle origin, transaction date, owner and
  co-owner roles, competent starosta or city, and current local online or
  appointment route. Do not merge the 185-day residence condition with every
  licence-recognition rule.

## Courts, legal aid, public rights, and victim support

- Owner: `poland-justice-legal-aid`; compose with `poland-appeals-review`,
  `poland-emergency-rights`, or the relevant sector skill.
- Scenarios: `court-case-and-electronic-delivery`,
  `criminal-record-certificate`, `privacy-and-data-complaint`,
  `discrimination-and-public-rights`, and `crime-victim-support`.
- Sources: `justice-court-information-portal`, `free-legal-aid-general`,
  `justice-victim-support`, and the competent court, ombudsman, UODO, police,
  prosecutor, or sector authority source.
- Separate court information, electronic delivery, filing, legal advice,
  administrative appeal, criminal-record certificate, privacy complaint,
  discrimination route, victim support, and immediate safety.
- Do not select legal strategy, admit facts, waive rights, predict a decision,
  or draft individualized pleadings as if acting as counsel. Preserve deadlines
  and escalate when professional judgment is required.

## Elections and civic participation

- Owner: `poland-civic-participation`; compose with
  `poland-digital-government` and `poland-local-services`.
- Scenario: `voter-register-and-polling-place`.
- Sources: `gov-central-voter-register`, `gov-change-voting-place`, and the
  current National Electoral Commission source for the specific election.
- Separate public election information, polling-place lookup, personal voter-
  register inspection, register correction, and voting-place change.
- Citizenship, election type, election date, current register state, and
  temporary location matter. Residence, PESEL, or a displayed address alone
  does not prove eligibility.

## Passports, consular matters, and cross-border travel

- Owner: `poland-consular-travel`; compose with `poland-emergency-rights`,
  `poland-foreign-documents`, `poland-healthcare`, or
  `poland-eu-mobility` when needed.
- Scenarios: `lost-or-stolen-polish-document`,
  `ekuz-cross-border-healthcare`, and `foreign-health-coverage`.
- Sources: `gov-lost-passport`, `gov-ekuz`, the current Polish consular source
  for Polish citizens abroad, or the issuing state's official mission source
  for a foreign passport.
- Separate reporting a Polish document, obtaining a replacement or temporary
  travel document, reporting a foreign passport, police or safety action,
  health cover, and immigration-status consequences.
- Reporting a document can invalidate it irreversibly. The agent may prepare
  and summarize the route, but the user must perform the report. Foreign-passport
  procedures belong to the issuing state, not a Polish universal service.

## Additional source-backed routes for 0.2

- Regulated professions: `professional-qualification-recognition` uses
  `gov-professional-qualifications-incoming` and `nawa-regulated-professions`.
  Separate academic recognition, professional recognition and work
  authorization; never infer eligibility or document sufficiency.
- Civil succession: `civil-succession-route` uses the e-Justice Poland
  factsheet and authority atlas plus `justice-court-finder`. Separate civil
  title/debts, court or notary, tax and cross-border branches. Minors, disputes,
  debts, applicable-law questions and unclear venue require escalation; never
  choose heirs, shares, acceptance/rejection or venue as a legal conclusion.
- Polish passports: `polish-passport-and-consular-appointment` uses the adult,
  temporary-passport, MFA and e-Konsulat sources. An ordinary adult passport
  requires personal attendance and biometrics; the user owns credentials,
  CAPTCHA, attestations and any irreversible invalidation.
- Vehicles: use `vehicle-roadworthiness-and-oc`,
  `road-tolls-and-local-parking`, and
  `imported-vehicle-customs-and-excise`. A registry result is not a safety,
  ownership or coverage conclusion. Exact route, vehicle/trailer combination
  and `target_date` are mandatory for tolls because the packaged e-TOLL change
  takes effect on 2026-09-21. Local parking needs the current BIP resolution,
  road manager and signage. PUESC routing never decides classification,
  valuation, exemption or liability.

## Completion standard

For every routed life event, output:

1. the known category facts and material unknowns;
2. candidate owners and why their roles differ;
3. source IDs and current official links;
4. online, local, professional, third-party, and in-person phases;
5. freshness, conflict, locality, fee, deadline, and appointment checks;
6. the next smallest action and any task-scope or action-time checkpoint;
7. the expected receipt or final-state evidence;
8. a guided manual fallback when interactive operation is unsupported.
