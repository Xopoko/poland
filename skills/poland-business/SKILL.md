---
name: poland-business
description: Business. Use when Polish registries matter.
---

# Poland Business

Use for business-form navigation, CEIDG/KRS/REGON lookups, registration phases,
licensed activity discovery, founder immigration dependencies, and official
registry evidence. Do not select a legal or tax form for the user from a generic
question.

Confirm citizenship/status group, intended activity, sole trader versus entity
question, founders, locality, employees, regulated activity, cross-border scope,
and the decision the user is actually making. Route residence dependencies to
`poland-stay-residence`, tax analysis to `poland-tax`, and ZUS questions to
`poland-social-insurance`.

Prefer public registry lookups and official Biznes.gov.pl, CEIDG, KRS, and GUS
sources. Only an unauthenticated, officially documented public registry API may
support read-only verification. Credentialed APIs and undocumented endpoints
are outside this plugin's boundary.

Build a dependency graph: legal/status gate, form decision requiring advice,
registry and identifiers, regulated-activity checks, tax/ZUS, banking/accounting,
and post-registration duties. Prepare only generic drafts and checklists with
placeholders. The plugin must not log in, register, change a record, declare,
sign, pay, upload, download, or close a business even with user confirmation.
It may hand off the exact official landing page and then stop. Read
`../../references/work-tax-business.md`.
