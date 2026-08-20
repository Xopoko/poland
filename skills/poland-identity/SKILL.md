---
name: poland-identity
description: Identity. Use when PESEL or meldunek matters.
---

# Poland Identity and Registration

Use for PESEL, residence registration (`meldunek`), civil records, identity
documents, trusted digital identity prerequisites, and municipality-owned
registration workflows. Do not assume PESEL proves immigration status or that one
office issues every identifier.

Confirm the person's citizenship/status group, whether they are registering a
stay or applying on another legal basis, current gmina/city, housing evidence
available, and the exact downstream service that needs the identifier. Distinguish
PESEL, NIP, REGON, KRS, and document-number categories; never request or put a
real identifier, address, or record content in plugin input or output.

Search current Gov.pl and municipal sources, then verify the local office,
booking channel, form version, required evidence, and whether a representative is
allowed. Build only a generic field and evidence-category checklist with
placeholders. The plugin must not inspect identity documents, log in, book,
enter personal data, upload or download a file, sign, or submit a declaration.
For a public e-government landing page use `poland-digital-government`; for
foreign certificates, apostille, or sworn translation use
`poland-foreign-documents`; for local offices use
`poland-local-services`.

Read `../../references/digital-government-map.md` and
`../../references/locality-and-appointments.md` when the procedure crosses those
boundaries.
