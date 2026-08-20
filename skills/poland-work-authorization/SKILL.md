---
name: poland-work-authorization
description: Work authorization. Use for permission to work in Poland, employer permits, declarations, notifications, or labour-market access.
---

# Poland Work Authorization

Use for whether a work-authorization route may be needed, employer-side permits
or declarations, notifications, exemptions, and the interaction between work
access and residence status. Employment contracts and workplace disputes belong
to `poland-employment-rights`.

Confirm citizenship/status group, current stated work-access basis, employer or
worker perspective, broad work type, location, intended start date, and whether
residence depends on the job. Keep unknown branches separate; do not assume that
all foreign workers use one permit or authority.

Use current Office for Foreigners, Gov.pl, Biznes.gov.pl, and public employment
service records. Identify the responsible actor, authority, current channel,
evidence categories, residence dependency, and human filing boundary. Verify
forms, deadlines, and exemptions at action time. Do not conclude that work is
lawful or unlawful from incomplete facts. The plugin must not log in, inspect
personal or employer records, enter data, upload, download, sign, send, or file
an employer notice even with user consent; provide the exact official landing
page and stop.

Treat praca.gov.pl as the public map and protected filing channel for relevant
employer-side permits, declarations, and notifications, not as the worker's
universal portal. Identify whether the foreigner, employer or other entrusting
entity, or voivode owns each step before planning it. Any authenticated
employer-side action belongs to the employer or its authorized human
representative, never the agent.

For EU Blue Card questions, compose this skill with `poland-stay-residence` and
use `mos-eu-blue-card` plus `udsc-mos-electronic-residence`. Live-verify the
salary threshold and reference period, qualification route, contract conditions,
regulated-profession branch, employer-change or notification rule, and mobility
branch. Keep the foreigner's application, the employer's signed attachment, and
the voivode's decision and in-person follow-up distinct; do not conclude
eligibility or operate either party's portal.

Route stay consequences to `poland-stay-residence`, contract rights to
`poland-employment-rights`, tax to `poland-tax`, and ZUS registration or coverage
to `poland-social-insurance`. Read
`../../references/work-tax-business.md` and the Blue Card actor map in
`../../references/immigration-status-map.md`.
