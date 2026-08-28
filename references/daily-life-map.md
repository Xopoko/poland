# Daily-Life Map

## First weeks in Poland

A newcomer checklist is a composition, not a single universal procedure. First
stabilize urgent safety, lawful-stay deadlines, and housing. Then route only the
branches that fit the user's facts: local identity or address matters,
healthcare and insurance, work authorization and employment, tax and ZUS,
school or childcare, banking and consumer safety, driving, and language or
document support. Each branch keeps its own owner, source IDs, locality, and
action-time verification.

Do not imply that every newcomer needs PESEL, meldunek, a bank account, Trusted
Profile, a residence permit application, or a driving-licence exchange in the
same order. Ask only non-identifying categories and return parallel user-owned
next actions. The plugin does not create a durable newcomer profile. When the
user asks for execution help, caller-owned tools may assist under
`automation-playbook.md`: user-only authentication and attestations, explicit
scope for personal data, action-time confirmation for external effects, and
manual fallback when no suitable tool is installed.

## Health

Use `nfz-patient` for public system and provider information. For `ikp`, the user
authenticates and explicitly scopes the minimum health-record access; a
caller-owned tool may then assist with the relevant administrative task. Do not
decide individual entitlement or diagnose from records. Booking, declaration,
send, upload, or download requires action-time confirmation. An urgent health
situation routes to `emergency-112` without waiting for automation.

## Family and education

Use `family-benefits`, `good-start`, and `empatia` for the named benefit and current benefit period. Use `education-foreign-children` for school routing. Capture residence status, child and school context, gmina, school year, and target date. Never reuse an old amount, deadline, or foreigner condition.

Use `nawa-recognition` for foreign education recognition questions, not ordinary school placement unless the authority points there.

For work in a regulated profession, use
`professional-qualification-recognition`. Determine regulated status,
qualification country, sector and profession-specific authority; do not merge
academic recognition with permission to practise or work.

## Housing and social support

Use `gov-social-assistance` for local social-assistance routing and `free-legal-aid` for individual tenancy disputes. Before using `uokik-consumer`, establish whether the counterparty acts as a business. Do not assume a private landlord dispute is a consumer matter.

Eviction, lockout, homelessness risk, violence, or document seizure requires prompt human escalation.

## Consumer sectors

- general business-to-consumer matter: `uokik-consumer`;
- telecom or postal matter: `uke-consumer`;
- bank, insurer, or financial provider: `financial-ombudsman`.

Use only non-identifying categories in bundled tools. In caller-owned operator
mode, explicit task scope permits minimum relevant record access and a reviewable
draft. Sending, upload, download, or account change requires action-time
confirmation. Contract termination, settlement acceptance, money movement,
signature, and final payment authorization remain user-controlled.

## Driving and transport

Use `drivers-act-consolidated` for the legal recognition and ordinary-residence
distinction, `gov-driving-licence-exchange` for the public exchange route, and
`utk-passenger-rights` for rail passenger matters. Local transport rules require
the owning city or operator source.

Keep two driving clocks distinct. Under the current Act on Vehicle Drivers, a
six-month recognition period applies to the Convention-based foreign licences
identified by that Act and runs from the start of permanent or temporary stay.
Separately, the Gov.pl exchange route asks whether the person has lived in Poland
for at least 185 days. These are different legal tests, not interchangeable date
labels and not a six-month countdown from issue of a residence card or EU Blue
Card. EU/EEA/Swiss licences and certain UK licences follow separate branches.
Verify the issuing country, document type, validity, applicable convention or
special rule, residence facts, and current official law before stating whether
the person may drive or must exchange the licence.

Use `vehicle-roadworthiness-and-oc` for inspections and OC checks,
`road-tolls-and-local-parking` for exact route/date/vehicle classification, and
`imported-vehicle-customs-and-excise` for PUESC/customs/excise separation. The
known e-TOLL transition date is 2026-09-21, so `target_date` is mandatory. Do
not freeze a fee, select an insurer, buy a policy, or infer roadworthiness,
coverage, toll liability, customs classification, valuation or exemption.

## Resident lifecycle and service map

This is an operational ontology, not a claim that one national checklist covers
every person. Start from the life event, collect only route-changing facts, bind
the route to source IDs, identify the competent local owner, and verify the
current deadline, appointment or online availability before acting.

| Life event or need | Primary official evidence | Digital or local handoff | Packaged scenario |
| --- | --- | --- | --- |
| EU citizen or family residence | `udsc-eu-citizens-family`, `your-europe-citizens` | voivode and current local appointment route | `eu-citizen-and-family-residence` |
| Family, study, research, business or other temporary stay | `mos-stay-purposes`, `mos-temporary-stay-checklists` | `mos`, then voivodeship follow-up | `purpose-specific-residence` |
| Long-term residence or citizenship status | `udsc-long-term-eu-resident`, `gov-citizenship-recognition`, `gov-citizenship-confirmation` | voivode, USC or consular route selected from facts | `long-term-resident-route`, `citizenship-recognition-or-confirmation` |
| PESEL record, identity fraud, lost Polish document | `gov-pesel-register-data`, `gov-pesel-reservation`, `gov-lost-id-card`, `gov-lost-passport` | `pesel-services`, `mobywatel-web`, `mobywatel-mobile`, competent gmina or issuer | `pesel-record-and-fraud-protection`, `lost-or-stolen-polish-document` |
| Birth, marriage, name or death | `gov-birth-registration`, `gov-civil-marriage`, `gov-name-change`, `gov-death-registration` | `civil-status-services` and the competent USC | `birth-registration`, `civil-marriage-and-name-change`, `death-and-funeral-route` |
| Annual income, private transaction, inheritance or donation tax | `tax-pit`, `tax-pcc`, `tax-inheritance-donations` and their service records | `your-e-pit`, `e-tax-office`, current tax office or appointment | `annual-pit-route`, `private-transaction-tax`, `inheritance-and-donation-tax` |
| Sickness, maternity, care, retirement or survivor benefit | `zus-cash-benefits`, `zus-pensions`, `zus-disability-survivor-pensions` | `ezus` or competent local ZUS unit | `sickness-maternity-care-benefit`, `retirement-survivor-pension` |
| Child and childcare support | `family-800-plus`, `active-parent`, `family-benefits`, `good-start` | `empatia`, `ezus` or named local owner | `family-childcare-benefits` |
| Adult or child disability and PFRON support | adult/child determination sources, `gov-supporting-benefit`, `pfron-sow` | powiat team, `pfron-sow`, ZUS and local BIP | adult, child and PFRON disability scenarios |
| Healthcare financing, provider search or EKUZ | `healthcare-foreigners`, `nfz-treatment-dates`, `gov-ekuz` | `ikp`, public NFZ search or local NFZ branch | `foreign-health-coverage`, `treatment-provider-search`, `ekuz-cross-border-healthcare` |
| School support, foreign school certificate or higher education | `education-psychological-counselling`, `education-school-certificate-recognition`, `higher-education-foreigners`, `nawa-recognition` | school, education superintendent, institution or voivode | education support, school-certificate and higher-education scenarios |
| Jobseeker or unemployment registration | `gov-unemployment-registration`, `praca-gov-pl` | `praca-gov-pl` and competent powiat labour office | `unemployment-registration` |
| Housing assistance or property administration | `gov-housing-allowance`, `gov-land-registers`, `gov-property-tax` | gmina, `land-registers`, court or notary route | `housing-assistance`, `property-register-and-tax` |
| Energy, telecom, water, heating or waste | `ure-household-energy`, `ure-consumer-disputes`, `gios-waste-recipients`, `uke-consumer`, `bip-directory` | provider, regulator, `waste-recipient-search` or municipal BIP selected by locality | `utilities-and-waste` |
| Vehicle registration, transfer, inspection, OC, toll, parking or import | vehicle, OC, e-TOLL and PUESC source sets | `vehicle-services`, `cepik`, `etoll`, `puesc`, starosta/city or current local BIP | vehicle registration, roadworthiness/OC, toll/parking and import scenarios |
| Voting register or polling place | `gov-central-voter-register`, `gov-change-voting-place` | `central-voter-register` and competent gmina | `voter-register-and-polling-place` |
| Court case, criminal-record certificate or legal aid | `justice-court-information-portal`, `gov-criminal-record-certificate`, `free-legal-aid-general` | court portal, certificate service or local legal-aid booking | court, KRK and legal-aid scenarios |
| Civil succession | e-Justice succession factsheet and authority atlas, `justice-court-finder` | current court, notary, tax or professional route selected from facts | `civil-succession-route` |
| Polish passport or consular appointment | `gov-passport-adult`, `gov-temporary-passport`, `mfa-passports-abroad` | `e-konsulat` plus mandatory personal/biometric phase | `polish-passport-and-consular-appointment` |
| Privacy, discrimination, banking or victim support | `uodo-complaints`, RPO sources, `bfg-deposit-guarantee`, `justice-victim-support` | regulator, ombudsman or current local support centre | privacy, rights, banking and victim-support scenarios |

## Composition and action contract

One event commonly creates parallel cases. A birth can require a civil record,
identity follow-up, residence analysis and benefits; a death can require USC,
funeral allowance, tax and civil-succession work; buying a vehicle can create
registration, notification, insurance and tax questions. Keep separate owners,
deadlines, evidence and receipts. Never collapse them into a single presumed
application.

`human_in_loop_operator` means a caller-owned Browser or Computer tool may
resume after the user authorizes the named task. It does not mean this plugin
ships an authenticated connector. The user enters secrets and confirms identity
providers and signatures. Before send, submit, book, change an official record,
pay, or disclose sensitive attachments, show the selected authority, locality,
form or service, deadline, material fields, attachments and expected effect and
obtain action-time confirmation.

Locality is evidence, not decoration. A national Gov.pl page does not prove the
competent gmina, powiat, voivode, court, school, provider or appointment system.
Use `bip-directory`, the packaged region map and the authority's current page;
if ownership or appointment availability remains unclear, keep the route
undetermined and give a manual fallback.

## Deliberately live or deferred edges

The bundle does not freeze municipal waste declarations, water and district-
heating rules, social-housing stock, local childcare recruitment, local parking
zones, court calendars, provider appointment slots or programme budgets. It
routes those to the current owner. Civil inheritance ownership can split among
notary, civil court and tax office, so the plugin covers the tax and legal-help
edges but does not invent a universal succession workflow. A passport issued by
another state routes to that state's current consular authority. Private bank,
insurer, telecom, landlord and utility portals are not treated as government
systems merely because an official regulator describes the complaint route.
