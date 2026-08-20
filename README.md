<p align="center">
  <img src="assets/icon.png" width="144" alt="Poland plugin logo">
</p>

<h1 align="center">Poland</h1>

<p align="center">
  Official sources. Clear next steps. You stay in control.
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

Poland is a public skill and tool pack that helps an AI agent navigate life and
administration in Poland. It is designed for residents, immigrants, expats,
citizens, families, students, employees, and people helping them.

The plugin gives the agent focused workflows, dated official-source metadata,
plain-language terminology, locality-aware routing, an offline CLI, and a
read-only MCP server. It can explain the landscape, build a checklist, show what
is still unknown, and point to the responsible official source. It does not
pretend to make a legal decision or act as you.

## Quick Start

### Easiest: Ask Your Agent

Paste this into an agent that can install local plugins:

> Install Poland from https://github.com/Xopoko/poland on this computer.
> Validate the source first, preserve the complete repository so its skills can
> reach bundled data, references, schemas, scripts, and MCP server, configure it
> only for the agent you are currently running, and report exactly what changed.
> Do not request credentials, enable authenticated integrations, or perform any
> external action.

### Codex

```bash
codex plugin marketplace add Xopoko/poland
codex plugin add poland@poland
codex plugin list --marketplace poland
```

### Claude Code

Run these slash commands inside Claude Code:

```text
/plugin marketplace add Xopoko/poland
/plugin install poland@poland
/reload-plugins
```

### Cursor

Clone the complete repository as one local plugin. On Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME/.cursor/plugins/local" | Out-Null
git clone https://github.com/Xopoko/poland.git "$HOME/.cursor/plugins/local/poland"
Set-Location "$HOME/.cursor/plugins/local/poland"
python scripts/validate_package.py
```

Then restart Cursor or run **Developer: Reload Window**. Do not copy only the
`skills/` directories: the workflows also use repository-level data,
references, schemas, scripts, and the MCP server.

See the [complete installation guide](docs/INSTALL.md) for macOS/Linux, updates,
removal, local-checkout review, and troubleshooting.

## What It Can Help With

| Area | Examples |
| --- | --- |
| Stay and status | EU mobility, visas, temporary residence, permanent residence, EU long-term residence, citizenship orientation |
| Work and business | Work authorization, employer routes, employment rights, CEIDG/KRS orientation |
| Identity and documents | PESEL, meldunek, civil records, apostille, legalization, sworn translation, recognition routes |
| Money and protection | PIT orientation, ZUS, benefits, consumer complaints, banking and telecom escalation |
| Everyday life | NFZ and healthcare routing, housing, education, transport, driving licences, local services |
| Difficult situations | Delays, supplementation requests, refusals, appeals, protection referral, emergency escalation |
| Digital government | Trusted Profile, ePUAP, MOS, praca.gov.pl, mObywatel, e-Tax Office, and eZUS boundaries |

The agent should use `poland` for a broad or multi-stage question and route a
clear task to one of the 23 focused skills.

## Prompts You Can Try

- "I am moving to Poland for work. Build a first-weeks checklist and mark every
  fact that must be checked today."
- "Explain PESEL and meldunek in plain language. Do not assume I need either."
- "Which authority owns this residence step, and which official source supports
  the answer?"
- "Compare the roles of MOS, ePUAP, Trusted Profile, and the voivodeship office."
- "Give me a document-preparation checklist using placeholders only."
- "Explain this Polish administrative term and show related terms."
- "My case is delayed. Help me separate a status check, a request to supplement,
  a complaint about inactivity, and an appeal."
- "Check whether the packaged sources for this route are still fresh as of
  today. Leave the result undetermined if the evidence is stale or conflicting."

Do not paste names, addresses, PESEL numbers, document or case numbers,
credentials, tax or health records, correspondence, screenshots, or personal
documents into plugin inputs or public issues. Describe the situation with
non-identifying categories.

## How It Works

1. The agent captures only the minimum non-identifying categories needed to
   distinguish candidate routes.
2. Deterministic routing produces `candidate`, `not_applicable`, or
   `undetermined`; missing facts stay visible.
3. Claims link to packaged official-source records with access dates, locators,
   jurisdiction, and freshness windows.
4. Dynamic facts such as forms, fees, deadlines, portal behavior, and office
   practice are rechecked with the competent authority at action time.
5. The agent may open an exact official landing page and then stops. You perform
   every account interaction and external action yourself.

## Trust Boundary

The bundled CLI and MCP server are offline, read-only, standard-library Python.
They do not browse, write files, or retain a case. A separate optional source
probe can make one bounded, unauthenticated request to an exact public HTTPS
origin already declared in the dataset; it returns metadata, not a saved page.

The plugin never logs in, chooses an identity provider, reads an authenticated
session or personal record, enters personal data, starts or saves a server-side
draft, submits, sends, books, cancels, pays, uploads, downloads, signs, calls,
uses a credentialed API, or changes external state. User consent does not unlock
those actions.

This is general source-linked navigation, not legal, tax, medical, financial,
or immigration advice. See the [Disclaimer](DISCLAIMER.md), [Privacy](PRIVACY.md),
[Security](SECURITY.md), and [Terms](TERMS.md).

## What Is Included

- 24 focused Agent Skills behind one router;
- versioned official-source, digital-channel, scenario, term, region, and action
  datasets with strict schemas;
- 51 official source records, 19 digital channels, 23 scenarios, and 47 terms in
  the initial release;
- a deterministic CLI with stable response envelopes;
- a networkless, read-only stdio MCP server;
- an isolated allowlisted public-source probe;
- synthetic regression fixtures and cross-platform CI.

## Optional Technical Tools

Most users can ignore this section and simply ask their agent. For inspection or
integration:

```bash
python scripts/poland.py overview
python scripts/poland.py sources --query residence --topic immigration
python scripts/poland.py channels MOS --as-of 2026-08-20
python scripts/poland.py route "moving for work" --citizenship-group third_country
python scripts/poland.py checklist settling-in-first-weeks --citizenship-group third_country
python scripts/poland.py freshness --as-of 2026-08-20
python scripts/poland.py validate
```

The MCP configuration is declared separately for Codex (`.codex-mcp.json`) and
Claude Code (`.mcp.json`) because the hosts resolve plugin-root paths differently.

## Plug'n Skills

[Plug'n Skills](https://github.com/Xopoko/plug-n-skills) advertises a reviewed,
immutable Poland revision. Poland is deliberately **not installed by default**:
it is available only when a user selects it explicitly. The reviewed pin may lag
the newest standalone source while a release is audited.

## Contributing and Support

Source corrections and focused workflow improvements are welcome. Read
[Contributing](CONTRIBUTING.md) and [Sources](SOURCES.md) before proposing a
change. Use only synthetic examples and public official evidence.

GitHub Issues are for plugin defects, public source corrections, and workflow
requests, not personal case advice. Read [Support](SUPPORT.md) before opening an
issue. The project is available under the [MIT License](LICENSE).
