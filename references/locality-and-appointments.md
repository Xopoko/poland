# Locality and Appointments

## Locality resolution

Normalize the voivodeship with `data/regions.json`. Use `mswia-jst-directory`
and `gus-teryt-api` only for territorial-unit identity and contact data; neither
proves procedural competence. First identify the authority level from the
national procedure, then verify the department and service channel in the
current local BIP through `bip-directory`.

Collect, as needed:

- voivodeship;
- powiat or city with powiat rights;
- gmina or Warsaw district;
- residence, employer, school, property, or business location that creates competence;
- the exact matter and case state.

Do not assume that the nearest office is competent.

Treat cities with powiat rights and Warsaw districts explicitly. Powiat labour
offices, vehicle-registration authorities, disability-determination teams and
some PFRON routes need `powiat` as a route fact; keep `gmina` only for genuinely
municipal branches. Local parking additionally needs the current municipal
resolution, road manager and signage, while a private car park is a separate
counterparty branch.

## Voivodeship immigration systems

The registry includes `mazowieckie-foreigners`, `wielkopolskie-foreigners`, `dolnoslaskie-foreigners`, and `malopolskie-foreigners` as examples of materially different local systems. One may expose a general calendar, another a case-state calendar, and another separate preparation and collection channels.

For other voivodeships, begin at the office's official BIP or gov.pl page and create a fresh evidence receipt. Do not reuse a neighboring region's workflow.

## Appointment boundary

Viewing public office topics or publicly visible generic availability is
read-only. A login wall, account state, CAPTCHA, personalized calendar, or form is
a pause-and-classify point. The user authenticates and completes CAPTCHA/2FA.
After explicit task scope, a caller-owned tool may inspect relevant availability
and fill necessary fields. Because booking, rescheduling, and cancellation change
a scarce slot and bind personal details, each requires a fresh visible summary
and action-time confirmation.

For a generic handoff checklist, show:

- authority and location;
- matter and service language if stated;
- date and time;
- required case state or invitation;
- categories of personal data the authority says it requires, without values;
- cancellation or change path.

Open the exact official booking route when a caller-owned tool is available; if
not, give semantic manual steps. Never bypass anti-bot controls, hoard slots, or
poll aggressively. Upload or download requires its own action-time confirmation.
After an appointment change, verify a visible official receipt before reporting
success and do not persist its personal details in plugin artifacts.

## Freshness

Local appointment sources use short freshness windows. Recheck the official page on the target date and treat cached availability as non-authoritative.
