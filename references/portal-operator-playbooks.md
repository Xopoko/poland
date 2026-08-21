# Portal Operator Playbooks

These playbooks help a caller-owned Browser or Computer capability operate a
current official service without pretending that button text, page order, or
CSS selectors are permanent. Apply `automation-playbook.md` and
`browser-safety.md` first. The packaged Poland CLI and MCP server do not execute
these steps.

## Shared live-page loop

For every portal:

1. resolve the competent authority and exact official origin from packaged
   sources;
2. name the task, actor, record categories, and likely external effects;
3. navigate to the official sign-in entry and yield while the user
   authenticates;
4. after the user says the page is ready, re-check origin, visible service, and
   actor context;
5. locate controls by accessible name, visible heading, and surrounding state,
   not by stored coordinates or undocumented endpoints;
6. inspect only the scoped record and prepare only the necessary fields;
7. before each effect, show the action-time summary required by
   `automation-playbook.md`;
8. yield for signatures, attestations, CAPTCHA, and final bank authorization;
9. verify a receipt or other unambiguous final state before reporting success.

If the current page does not expose the expected semantic phase, stop and use a
guided manual fallback. Do not guess a nearby control.

## MOS residence services

Evidence: `udsc-mos-electronic-residence`, `mos-residence`, the matching
purpose-of-stay source, and the competent voivodeship source.

Expected phases:

1. public purpose and exception check;
2. user-controlled `login.gov.pl` authentication;
3. correct applicant account and new or existing case choice;
4. exact residence-purpose branch;
5. applicant details and declarations;
6. purpose-specific evidence and any separately controlled employer,
   university, or organiser attachment;
7. validation and review;
8. user-controlled electronic signature;
9. final send confirmation;
10. official acknowledgment of receipt and later voivode instructions.

Account creation, a server-side draft, each upload, each download, and final
send are separate effects. Authority granted by the foreigner does not authorize
operation of an employer or institution account. Do not report filing complete
until the official acknowledgment is visible. Fingerprints, passport originals,
specimen signatures, or supplementation may still require later personal action.

## ePUAP correspondence

Evidence: `epuap`, `profil-zaufany`, the receiving authority source, and the
underlying procedure source.

Expected phases:

1. decide whether a dedicated service or a general letter is the accepted
   route;
2. user-controlled authentication;
3. verify the sender context and recipient authority;
4. select the service or compose the addressed message;
5. prepare subject, body, and attachments;
6. review delivery effect and signature requirement;
7. user-controlled signature;
8. final send confirmation;
9. sent-item state and official submission confirmation.

Do not treat ePUAP as the owner of the procedure. If the authority now requires
e-Deliveries, MOS, a dedicated form, paper, or in-person filing, stop and reroute.

## e-Deliveries

Evidence: `e-deliveries` and the recipient authority's current delivery
guidance.

Expected phases:

1. verify that both the sender category and recipient use this channel for the
   intended legal effect;
2. user-controlled authentication and mailbox choice;
3. verify the recipient by official identity or delivery address;
4. prepare the message and attachments;
5. review delivery type and effect;
6. user-controlled signature when required;
7. final send confirmation;
8. proof-of-send or proof-of-delivery state.

An email address, ePUAP address, and e-Delivery address are not interchangeable.
Never choose a similar-looking recipient from search results without independent
authority verification.

## e-Tax Office

Evidence: `podatki-home`, `e-tax-office`, and the exact tax or service source.

Expected phases:

1. classify the tax, period, taxpayer role, and intended operation;
2. user-controlled authentication;
3. verify the visible taxpayer or organization context;
4. locate the exact return, message, certificate, payment, or account service;
5. inspect only the scoped period and record;
6. prepare corrections or fields and disclose any auto-calculation;
7. review declarations, amount, account, period, and attachments;
8. user-controlled attestation, signature, or payment authorization;
9. final action confirmation;
10. UPO, payment state, sent message, or other official receipt.

Never transfer an amount or bank account from an old instruction without live
verification. A calculated result is not professional tax advice or proof that
all income and relief facts are complete.

## eZUS

Evidence: `ezus`, the exact ZUS benefit or insurance source, and any EU or
bilateral coordination source.

Expected phases:

1. identify insured person, payer, beneficiary, or representative role;
2. user-controlled authentication and role selection;
3. locate the exact record, certificate, benefit, contribution, message, or
   application;
4. inspect only the authorized period and record category;
5. prepare fields and attachments;
6. review declarations, dates, payer/beneficiary role, and delivery effect;
7. user-controlled signature or attestation;
8. final send or download confirmation;
9. UPO, sent document, generated certificate, or case state.

Do not infer insurance, benefit, pension, or contribution correctness from a
single screen. Preserve the distinction between a visible record and a formal
ZUS decision.

## Internet Patient Account

Evidence: `ikp`, `nfz-patient`, and the exact healthcare-service source.

Expected phases:

1. classify the task as coverage, provider search, referral, prescription,
   appointment, consent, or document access;
2. user-controlled authentication;
3. confirm the requested patient or authorized dependent context;
4. expose only the minimum relevant record;
5. navigate or prepare the requested service;
6. review provider, service, referral, date, location, and cancellation effect;
7. final booking, cancellation, download, or change confirmation;
8. appointment or document result.

Medical consent, treatment choice, prescription decisions, and health
attestations are user- or clinician-controlled. Never copy health records into
plugin receipts, tests, issues, or durable notes.

## CEIDG and business services

Evidence: `biznes-ceidg`, `biznes-home`, and the source for the exact business
operation.

Expected phases:

1. distinguish public registry lookup from owner-controlled registration or
   change;
2. classify the natural-person, representative, or organization role;
3. user-controlled authentication;
4. choose the exact registration, suspension, resumption, change, or closure
   operation;
5. prepare business, address-category, activity, tax, insurance, and effective
   date fields without guessing professional classifications;
6. review cross-system effects and declarations;
7. user-controlled signature;
8. final submission confirmation;
9. official receipt and later registry state.

Business registration can affect tax, VAT, ZUS, licenses, and employment. Stop
for qualified advice when the choice depends on individualized legal or tax
judgment.

## praca.gov.pl and employment-office services

Evidence: `praca-gov-pl`, the exact employment or work-authorization source,
and the competent labour-office source.

Expected phases:

1. identify worker, employer, entrusting entity, or jobseeker actor;
2. verify the competent national, voivodeship, or powiat route;
3. user-controlled authentication in the correct actor's account;
4. locate the exact permit, declaration, notification, registration, benefit,
   or message service;
5. prepare actor-owned fields and attachments;
6. review dates, work basis, authority, declarations, and fee;
7. user-controlled signature or attestation;
8. final send confirmation;
9. official receipt or case state.

Authority from a worker does not authorize an employer account, and employer
filing does not by itself prove the worker's residence or labour right.

## Empatia and local family or social services

Evidence: `empatia`, the exact benefit or assistance source, and the competent
gmina or local institution.

Expected phases:

1. identify the requested benefit or support, period, household role, and
   locality;
2. verify which institution owns the application and whether Empatia is the
   current channel;
3. user-controlled authentication;
4. choose the exact benefit period and application;
5. prepare household-category, income-category, child, care, and attachment
   fields only within the authorized scope;
6. review declarations, coordination questions, recipient account, and
   attachments;
7. user-controlled attestation or signature;
8. final submission confirmation;
9. receipt and later institution decision.

Do not treat a complete form as an entitlement decision. Cross-border family
or insurance facts may require EU coordination rather than an ordinary local
route.

## mObywatel and Central Register of Voters

Evidence: `mobywatel`, `gov-central-voter-register`, and current PKW guidance
for the specific election.

Expected phases:

1. distinguish a public election-information question from personal-register
   access or a change request;
2. identify election type, date, citizenship category, and intended location;
3. user-controlled app or browser authentication;
4. inspect the scoped voter-register or service state;
5. prepare a change or certificate request only after resolving its current
   legal effect;
6. review address category, election, request effect, and deadline;
7. user-controlled attestation or signature;
8. final action confirmation;
9. updated status or official receipt.

Do not infer voting eligibility from residence, PESEL, or a displayed address.
Mobile-only device confirmation remains user-controlled when the host cannot
operate it safely.

## Court and justice portals

Evidence: the exact court or justice source, `court-information-portal`, and
the applicable electronic-delivery source.

Expected phases:

1. identify court system, case type, party role, stage, and deadline;
2. verify whether the portal is for case viewing, correspondence, or filing;
3. user-controlled authentication;
4. inspect only the authorized case and document;
5. prepare a download, message, or filing only if the official route and legal
   owner are clear;
6. show deadline, recipient, attachments, fee, declarations, and irreversible
   effects;
7. yield for legal attestations and signatures;
8. final send, submit, download, or payment confirmation;
9. official delivery, filing, payment, or receipt state.

The agent does not choose legal strategy, waive rights, admit facts, withdraw a
claim, or replace counsel. Stop for a qualified professional when a decision
depends on individualized legal analysis or a deadline is uncertain.

## Guided manual fallback

When an interactive capability is missing or the page fails a safety check:

1. state the verified official hostname and page heading;
2. name the next semantic control and the expected result after the user uses
   it;
3. tell the user what secret or personal step they must complete privately;
4. ask them to report only the non-sensitive page state or provide a redacted
   screenshot when safe;
5. continue from that state under the same scope and confirmation contract.

Manual fallback is not abandonment. Stay with the workflow, but do not ask the
user to reveal credentials, identifiers, medical details, case documents, or
other unnecessary personal content in chat.
