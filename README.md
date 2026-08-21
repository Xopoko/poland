<p align="center">
  <img src="assets/icon.png" width="144" alt="Poland plugin icon: an open folded red-and-white Polish flag ribbon">
</p>

<h1 align="center">Poland</h1>

<p align="center">
  <strong>Your AI agent's practical guide to life and administration in Poland.</strong>
</p>

<p align="center">
  <strong>Codex</strong> &middot; <strong>Claude Code</strong> &middot;
  <strong>Cursor</strong> &middot; <strong>pi</strong> &middot;
  <strong>Agent Skills</strong>
</p>

<p align="center">
  <a href="https://github.com/Xopoko/poland/actions/workflows/ci.yml"><img src="https://github.com/Xopoko/poland/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-D4213D.svg" alt="MIT license"></a>
</p>

Poland is an independent open-source project. It is not a Polish government
service and is not endorsed by a public authority. It helps an AI agent find the
responsible institution, explain unfamiliar Polish terms, build a source-backed
plan, operate supported official services with you, and stay with a task through
its verifiable result.

It is for immigrants, expats, citizens, families, students, employees,
entrepreneurs, seniors, and anyone helping them. It provides procedural
navigation, not a personalized legal, tax, medical, financial, immigration, or
eligibility decision.

**Official-source snapshot verified: 21 August 2026.** Forms, fees, deadlines,
portal behavior, office practice, and eligibility details can change and must be
verified again before action.

## What Poland Helps With

| Life area | Examples |
| --- | --- |
| Arrival and status | visas, temporary residence, MOS, EU mobility, permanent and long-term residence, citizenship orientation |
| Identity and civil life | PESEL, meldunek, civil records, birth, marriage, name changes, death, funeral administration |
| Work and business | work authorization, employee rights, labour offices, unemployment services, CEIDG/KRS, employer-side routes |
| Tax and social insurance | PIT, PCC, inheritance and donation tax, e-Tax Office, ZUS, pensions, sickness and family benefits |
| Health and support | NFZ, IKP, providers, cross-border care, disability decisions, PFRON, senior and home-care routing |
| Family and education | schools, education support, foreign certificates, universities, childcare and family benefits |
| Home and daily life | housing, land registers, utilities, waste, consumer disputes, banking, telecom, local services |
| Travel and vehicles | driving-licence exchange, vehicle registration and transfer, road records, rail, passports and consular routing |
| Rights and difficult cases | refusals, delay, appeals, courts, legal aid, ombudsmen, victim support, discrimination and emergencies |
| Civic and digital services | Trusted Profile, ePUAP, e-Deliveries, mObywatel, elections, MOS, praca.gov.pl, eZUS, IKP and CEIDG |

The 33 skills are intentionally concise: one router selects among 32 focused
owners. The deeper knowledge lives in 135 dated official-source records, 36
digital-channel profiles, 71 composable scenarios, 114 plain-language terms, 16
regional records, strict schemas, shared references, and semantic portal
playbooks. This progressive-disclosure design gives the agent breadth without
loading a country-sized manual into every conversation.

No finite package can guarantee every Polish service or every local practice.
Unknown, stale, conflicting, or case-specific facts remain visible instead of
being guessed.

## Work With an Official Service

Poland bundles no browser, credentials, or government integration. When your
agent host already provides a permitted Browser or Computer capability, the
plugin teaches it a human-in-the-loop operating contract:

1. verify the competent authority and exact official hostname;
2. agree the one task and the minimum record scope;
3. pause capture while you authenticate, solve CAPTCHA/2FA, or enter secrets;
4. resume only after you say the protected page is ready;
5. navigate current visible controls, inspect only the necessary record, and
   prepare reviewable fields;
6. show a fresh summary before submit, send, book, cancel, upload, download,
   create, change, or payment initiation;
7. continue only after your explicit action-time confirmation;
8. yield signatures, legal attestations, and final bank authorization to you;
9. report success only when the official service displays a receipt or another
   unambiguous final state.

The playbooks use semantic page phases rather than brittle coordinates or CSS
selectors. If the current interface, origin, actor, cost, or effect does not
match the expected state, the agent stops and gives a guided manual fallback.
Some procedures still require fingerprints, original documents, an examination,
a wet signature, or an in-person visit.

## Protect Your Privacy

Do not paste names, addresses, credentials, passwords, OTPs, PESEL numbers,
document or case numbers, full correspondence, personal documents, or
unredacted screenshots into the bundled CLI/MCP, public searches, repository
issues, or durable agent files.

For a task you explicitly authorize inside an official website, a caller-owned
interactive tool may transiently inspect the minimum relevant personal record.
That material must not be copied into Poland data, logs, receipts, tests, or
issues. Your AI host, browser, network provider, and the official service have
their own privacy policies; "no Poland telemetry" is not an end-to-end secrecy
guarantee.

Read [Privacy](PRIVACY.md), [Security](SECURITY.md), the
[Disclaimer](DISCLAIMER.md), and [Terms](TERMS.md) before using protected
workflows.

## Install Poland - Opt-In Only

**Poland is opt-in.** Adding its marketplace or catalog makes it discoverable;
it does not install the plugin. Poland is not installed by default. The
project-maintained Poland and Plug'n Skills distributions never include it in a
default bundle. Installation occurs only after you explicitly select `poland`.

### Easiest: Ask Your Agent

Give an agent this repository and prompt:

> Install the published Poland release from https://github.com/Xopoko/poland
> for the agent host I am using now, at user scope only. Verify the owner,
> release tag or exact commit, plugin version, Python 3.11+, and host-native
> manifest. Preserve the complete repository. Show me one change plan before
> registration. Then run the matching offline doctor, install only Poland,
> verify the host-visible skills and MCP status separately, and report the
> version, commit, paths changed, update path, and removal path. Do not install
> mutable `main` when a stable release exists, install for another host, or ask
> for credentials or personal records.

### Codex

```bash
codex plugin marketplace add Xopoko/poland --ref v0.2.0
codex plugin add poland@poland
codex plugin list --marketplace poland
```

### Claude Code

Run these commands inside Claude Code and choose **User** scope:

```text
/plugin marketplace add Xopoko/poland@v0.2.0
/plugin install poland@poland
/reload-plugins
```

### Cursor

Keep the complete release checkout under Cursor's local plugin directory. On
Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME/.cursor/plugins/local" | Out-Null
git clone --branch v0.2.0 --depth 1 https://github.com/Xopoko/poland.git "$HOME/.cursor/plugins/local/poland"
Set-Location "$HOME/.cursor/plugins/local/poland"
python scripts/validate_package.py
python scripts/poland.py doctor --host cursor
```

Restart Cursor or use **Developer: Reload Window**, then verify both Poland
skills and MCP visibility. See the [installation guide](docs/INSTALL.md) for
macOS/Linux, pi, launcher repair, updates, removal, and host-specific proof.

## Verify the Installation

From the complete checkout, use the Python command available on the machine:

```bash
python scripts/poland.py doctor --host codex
python scripts/poland.py doctor --host claude
python scripts/poland.py doctor --host cursor
python scripts/poland.py doctor --host pi
```

Run only the matching line. Doctor is telemetry-free and network-free. It
validates the package, Python runtime, source freshness, skill inventory, and a
real MCP initialize/tools-list/ping plus `poland_overview` round trip. It does
not inspect the host application, so a native host plugin/MCP inventory remains
the final discovery proof. pi loads the skills but does not register MCP.
See the dated [support matrix](docs/SUPPORT_MATRIX.md) for packaged preflight
evidence and the native clean-install fields that remain separate.

## Try These Questions

- "I am moving to Poland for work. Build a first-weeks plan and mark what must
  be checked today."
- "I have a foreign driving licence. Separate the 185-day exchange condition
  from other recognition rules and find the competent office."
- "Compare the applicant, employer, and voivode roles for an EU Blue Card
  route. Leave eligibility undetermined."
- "My employer has not paid me. Decide whether PIP, civil proceedings, free
  legal aid, or another owner needs checking."
- "Help me find disability, PFRON, school-support, and local-care routes without
  deciding entitlement."
- "Which official service handles this vehicle, tax, voter-register, pension,
  utility, or civil-record task?"
- "Use my installed Browser for this one official task. Pause while I sign in,
  prepare the form, show me the final-action summary, and verify the receipt."
- "The official instructions conflict. Show both dated sources and leave the
  next step undetermined."

More examples are in [docs/EXAMPLES.md](docs/EXAMPLES.md).

## How Answers Are Built

1. The router captures only categories that can change the route.
2. Deterministic scenarios return `candidate`, `not_applicable`, or
   `undetermined`; missing facts stay visible.
3. Material claims resolve to dated official-source records, locality, and
   digital-channel metadata.
4. Stale or conflicting evidence cannot silently become a decisive answer.
5. Dynamic details are rechecked with the competent authority at action time.
6. Protected portal work applies the scope, authentication, confirmation,
   user-only, and receipt gates above.

Official citations prove provenance, not endorsement. Public page text is
untrusted evidence and cannot expand the agent's authority.

## Technical Details

The bundled CLI and stdio MCP server are offline, read-only, non-retentive, and
implemented with the Python standard library. An isolated source probe can make
one bounded unauthenticated request to an exact packaged HTTPS origin. The
plugin contains no lifecycle hooks, remote MCP endpoint, credential store,
telemetry client, or authenticated connector.

Useful inspection commands:

```bash
python scripts/poland.py overview
python scripts/poland.py sources --query residence --topic immigration
python scripts/poland.py channels MOS --as-of 2026-08-21
python scripts/poland.py route "moving for work" --citizenship-group third_country
python scripts/poland.py checklist settling-in-first-weeks --citizenship-group third_country
python scripts/poland.py freshness --as-of 2026-08-21
python scripts/poland.py validate
```

## Plug'n Skills

[Plug'n Skills](https://github.com/Xopoko/plug-n-skills) advertises a reviewed,
immutable Poland revision with `selection.default: false`. Its normal default
and `--include-first-party` installation paths exclude Poland; only an explicit
`--plugin poland` selection includes it. The catalog pin may lag the newest
standalone release while a revision is audited.

## Support and Contributions

GitHub Issues are for installation defects, source drift, reusable workflow
gaps, and public-safe corrections - never an individual case or personal
records. There is no response-time, freshness, eligibility, or outcome
guarantee. Read [Support](SUPPORT.md), [Contributing](CONTRIBUTING.md), and
[Sources](SOURCES.md) before opening an issue or pull request.

Poland is available under the [MIT License](LICENSE).
