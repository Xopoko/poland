---
name: poland-local-services
description: Local services. Use when Polish office ownership varies.
---

# Poland Local Services

Use when a procedure varies by voivodeship, powiat, gmina, city, or specific
office; when the user needs an appointment; or when national guidance must be
mapped to a local executor.

Confirm current or intended voivodeship, gmina/city, whether the address is
already established, procedure, citizenship/status group when relevant, deadline,
accessibility/language needs, and whether the person can attend in person. Do not
infer the competent office from a postal address without verifying the procedure's
territorial rule.

Use `regions` to normalize the voivodeship, then join the national authority's
office directory with the local official site. Verify the office name, department,
territorial competence, service channel, current booking system, opening hours,
form version, accessibility, and contact method at action time. Municipal newcomer
centres can assist but do not replace the authority that owns the decision.

Appointments and cancellations can deny scarce slots or create deadlines. The
plugin may identify the public booking landing page and prepare a generic
placeholder checklist, then it must stop. It must not log in, inspect personal
availability, book, reschedule, cancel, enter data, or preserve a personal
confirmation even with user consent. Never automate CAPTCHA or poll slots.

Read `../../references/locality-and-appointments.md`; hand substantive questions
back to the relevant domain skill.
