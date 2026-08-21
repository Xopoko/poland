# Immigration Status Map

This map selects sources and questions. It does not determine status, permission, or eligibility.

## Intake branches

### Polish citizen or citizenship procedure

Use `gov-citizenship`. Ask which citizenship procedure, where the person resides, the target date, and whether foreign documents are involved. Add `sworn-translators` and `apostille` only after the receiving authority's requirements are known.

### EU, EEA, or Swiss context

Use `your-europe-citizens` for cross-border orientation, then `udsc-home` and the competent voivodeship source for Polish implementation. Collect length and purpose of stay, family context, and locality without predicting the required document.

### Third-country context

Use `udsc-home`, `mos-residence`, and, when the filing channel matters,
`udsc-mos-electronic-residence`. Collect only the current status-document
category or title, stated purpose, target procedure, voivodeship, and target
date in bundled plugin tools. When the user requests protected-service help, use
`automation-playbook.md`: the user authenticates and signs; explicit task scope
permits minimum document or case inspection and form filling; draft creation,
upload, download, payment initiation, booking, or submission requires
action-time confirmation. Never infer work authorization from a residence label;
route work questions separately through `biznes-legal-work` and `pip-employees`.

### Protection context

Use `udsc-home` and the protection-specific page it owns. Record whether the user reports international protection, temporary protection, or an unknown status. Do not merge protection categories or reuse country-specific benefit summaries.

### PESEL UKR and the 2026 transition

Use `udsc-ukraine-status-transition-2026` for the general change that took
effect on 5 March 2026, then select the procedure-specific source. The transition
page separates rules that ended, periods extended to 4 March 2027, and selected
temporary-residence routes that remain available to temporary-protection
beneficiaries holding PESEL UKR. Do not generalize any one rule to every
Ukrainian citizen, every temporary-protection beneficiary, or every person with
a PESEL number.

For a CUKR request, use `udsc-cukr-procedure` and the `mos` digital channel. The
20 August 2026 source snapshot says the CUKR electronic procedure opened on
4 May 2026 and gives a current filing window ending 4 March 2027. Ask for the
reported citizenship or family-member group, current PESEL UKR category,
source-defined status-history dates, child branch if relevant, current location,
voivodeship, pending residence case, and target date. These inputs select the
official checklist; they do not establish qualification. Recheck the current
applicant groups, status dates, filing window, pending-case consequences,
attachments, signature method, benefit consequences, card-collection rule, and
fees before action. Do not freeze an amount or outcome.

The PESEL UKR passport-data branch is a different route. The public outreach
notice `gov-pesel-ukr-passport-update-2026` lists records where registration
lacked a passport, a passport or passport data changed, or a child lacked a
passport at registration. Do not infer one deadline from those shorthand
categories. Use the T0 source `sejm-ukraine-transition-act-2026`: Article 25
sets 31 August 2026 for identity confirmation where PESEL was assigned on the
basis of a declaration and describes a 1 September status consequence when the
specified confirmation did not occur; Article 26 uses a separate 60-day period
from travel-document issuance for specified other original-document situations,
including invalid or expired documents, subject to its exception for identity
already confirmed after PESEL assignment. Verify the original registration
basis, whether identity has already been confirmed, the current gmina
instructions, identity-document requirement, appointment availability, and any
newer official guidance. Do not decide the person's group or legal effect from a
shorthand account.

For CUKR portal assistance, the user authenticates, signs, and makes every legal
declaration. An explicitly authorized caller-owned tool may inspect the selected
record or fill reviewable fields after authentication; account creation,
server-side draft creation, upload, download, payment initiation, booking, and
submission require fresh action-time confirmation. For the PESEL registry
update, an agent may locate the office, prepare a checklist, and prepare a
booking with confirmation, but the user personally presents identity documents
and authorizes the official-record change. Preserve the authority's receipt or
confirmed office result before reporting completion.

### Unknown or disputed status

Do not continue to an eligibility checklist. Start with the document-title
category and issuing authority, then route to `free-legal-aid` or the competent
authority. A caller-owned tool may inspect a user-selected notice after explicit
task scope, but the agent must separate its text from legal interpretation and
must not let automation delay deadline preservation. Treat a near deadline or
adverse decision as an escalation.

## Local owner

Residence cases are administered locally even when national guidance is centralized. Use the voivodeship sources in the registry and `locality-and-appointments.md`. A national source cannot prove a local slot, case state, or document-collection method.

## National permanent residence

Use `mos-permanent-residence` for the national permanent-residence permit. Keep
it separate from `udsc-long-term-eu-resident`, EU free-movement permanent
residence, and every citizenship procedure. A shared word such as "permanent"
does not prove the route.

Collect the claimed statutory-basis category, current status and location,
residence-history category when relevant, family or Polish-origin context when
relevant, voivodeship, foreign-document dependencies, and target date. Use those
facts to select the current official section and competent voivode, not to make
an eligibility finding. Verify the current MOS form, accepted attachments,
signature method, location rule, in-person identity or biometric follow-up,
official acknowledgment, fees, deadlines, and local instructions at action time.
Do not substitute conditions from the EU long-term-resident route or freeze a
fee, processing time, or outcome.

The user personally authenticates, signs, attests, and completes any required
in-person identity or biometric step. Explicit task scope permits minimum record
inspection and reviewable form filling in a caller-owned tool. Account creation,
server-side draft creation, upload, download, payment initiation, booking, and
submission require fresh action-time confirmation. An official acknowledgment
or other visible authority receipt is required before the agent reports filing
as complete.

## Electronic residence channel

The current `udsc-mos-electronic-residence` guidance makes MOS the general
electronic filing channel from 27 April 2026 for temporary, permanent, and
long-term EU resident permits, but names specific temporary-residence branches
that remain on paper. Classify the exact purpose and whether the applicant is
inside or outside Poland before selecting a channel. Recheck the transition,
exceptions, signature methods, attachments, and competent voivode at action
time.

Electronic filing does not remove the later physical stage. Public guidance
states that the voivode may call the applicant to provide fingerprints and a
specimen signature, show the original passport, or supplement the case. Keep
the MOS filing, third-party attachment, and later voivode stages separate in the
plan. Pause at every protected or personal action and classify it through the
shared operator contract. User-only authentication, signatures, attestations,
biometrics, and original-passport presentation stay with their owner; eligible
record reads, form filling, and confirmation-gated effects may continue in a
caller-owned tool.

## EU Blue Card composition

Use `mos-eu-blue-card` for the current highly qualified employment route,
`udsc-mos-electronic-residence` for the electronic filing channel, and the
competent voivodeship source for local ownership. Treat this as a composed stay
and work route, not a generic work permit and not a status inferred from a job
title.

Keep actors explicit:

- the foreigner owns the residence application and required applicant
  declarations;
- the employer owns the employment facts and any required electronically
  completed and signed employer attachment;
- the voivode owns the decision, requests for supplementation, and later
  in-person identity and biometric steps.

At action time, verify the current salary threshold and reference period,
qualification pathway, contract conditions, regulated-profession requirements,
employer-change or notification rules, mobility branch, documentary evidence,
fees, and deadlines. Do not freeze an amount or conclude eligibility. The agent
may map public requirements and prepare reviewable fields. It may assist inside
MOS only after the applicant completes authentication and explicitly scopes the
task. Case inspection and form filling are task-scoped; employer contact,
upload, download, payment initiation, booking, or submission is
confirmation-gated. The applicant signs and attests. An employer-controlled
attachment or account requires authorization from the employer or its authorized
human representative, not merely from the foreigner.

## Evidence rule

For every route, preserve the status facts as user-provided, the source observation as official, and the final interpretation as unknown unless the authority has issued it.
