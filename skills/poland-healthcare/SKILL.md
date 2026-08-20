---
name: poland-healthcare
description: Healthcare. Use when NFZ or IKP matters.
---

# Poland Healthcare

Use for NFZ coverage navigation, IKP/mojeIKP, primary care, referrals,
prescriptions, insurance confirmation, cross-border documents, and finding the
right public service. Do not diagnose, interpret symptoms, or delay urgent care.

First determine whether the need is an emergency. If immediate danger is possible,
surface 112 and human action through `poland-emergency-rights`; do not continue a
routine portal workflow. Otherwise confirm only broad coverage basis, locality,
`eu_eea_swiss` or `third_country` cross-border context, and whether the request
concerns public access guidance or a medical decision.

Use public NFZ and Pacjent.gov.pl sources. If the route reaches IKP, a login wall,
or personal health information, provide the exact official landing page and stop.
The plugin must not authenticate, inspect records or documents, take screenshots,
upload, download, or enter health data even with user consent. Draft only generic
questions with placeholders, identify evidence categories and the competent
branch, and state what a medical professional or insurer must confirm.

For insurance registration or contributions route to
`poland-social-insurance`; for EU coordination also use
`poland-eu-mobility`. Read
`../../references/daily-life-map.md` and the emergency boundary in
`../../references/emergency-and-escalation.md`.
