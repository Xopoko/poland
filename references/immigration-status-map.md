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
date. Do not ask to inspect the document, enter MOS, authenticate, or use an
electronic signature. Never infer work authorization from a residence label;
route work questions separately through `biznes-legal-work` and
`pip-employees`.

### Protection context

Use `udsc-home` and the protection-specific page it owns. Record whether the user reports international protection, temporary protection, or an unknown status. Do not merge protection categories or reuse country-specific benefit summaries.

### Unknown or disputed status

Do not continue to an eligibility checklist. Ask only for the document-title category and issuing authority, without receiving or inspecting the notice, then route to `free-legal-aid` or the competent authority. Treat a near deadline or adverse decision as an escalation.

## Local owner

Residence cases are administered locally even when national guidance is centralized. Use the voivodeship sources in the registry and `locality-and-appointments.md`. A national source cannot prove a local slot, case state, or document-collection method.

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
plan. The plugin stops before every protected or personal action.

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
may map public requirements and placeholders only; it must not enter MOS,
contact the employer through the portal, upload evidence, sign, submit, inspect
a case, or book the physical follow-up.

## Evidence rule

For every route, preserve the status facts as user-provided, the source observation as official, and the final interpretation as unknown unless the authority has issued it.
