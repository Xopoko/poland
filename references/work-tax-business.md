# Work, Tax, and Business

## Work

Start with status and work context, not the contract label alone. Use:

- `biznes-legal-work` for current official orientation on work by foreign nationals;
- `praca-gov-pl` for public employment-service forms and channels;
- `pip-employees` for labour rights, safety, and complaint routing.

Do not conclude that work is permitted, that a document is sufficient, or that an employer is compliant. The plugin must not send complaints or contact an employer even with user confirmation. Coercion, threats, withheld documents, or unsafe work route immediately to `anti-trafficking-kcik` or `emergency-112` as appropriate.

## Tax

Use `podatki-home` for public guidance. `e-tax-office` is an exact official landing-page handoff only; stop before login, records, or filings. Capture only tax period, residence category, income category, business-status category, and whether an authority notice exists. Do not inspect the notice, choose a tax treatment, file or correct a return, or initiate payment.

Appointments through `tax-office-appointments` consume a scarce slot. Show the public office, topic, and official landing page, then stop. The plugin must not inspect personal availability, book, reschedule, or cancel.

## Social insurance

Use `zus-home` for public information. `ezus` is an exact official landing-page handoff only; the plugin must not authenticate, inspect account records or documents, book, file, pay, upload, download, or change a record. Do not treat tax registration, business registration, health insurance, and social-insurance enrolment as interchangeable.

## Business

Use `biznes-ceidg` to distinguish public search from registration or record changes. Use only allowlisted, unauthenticated public access to `krs-search` and `gus-regon-api` for official registry evidence. Collect the proposed legal-form category, current-status category, and intended effect, not identifier values.

Never select a legal form, tax method, insurance title, or accounting treatment as an automated outcome. Route those choices to a qualified human adviser when they are material.
