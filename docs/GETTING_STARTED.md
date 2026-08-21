# Getting Started with Poland

You do not need to know Python or MCP to use Poland. Install the complete plugin,
start a new agent conversation, and describe your goal without identifiers.

Before the first conversation, ask the installing agent to run the telemetry-free
preflight for the host you use:

```text
python scripts/poland.py doctor --host <codex|claude|cursor|pi>
```

`valid: true` proves the package checks listed in the receipt and the local MCP
launcher on that computer. It does not prove that the host loaded the plugin.
The agent must still show the host's own plugin inventory and, for Codex, Claude
Code, or Cursor, the Poland MCP server. pi installs the 33 skills but does not
register the bundled MCP server. See `docs/INSTALL.md` for the host matrix and
launcher-repair flow.

## Describe a Situation Safely

Useful categories include:

- citizenship group: Polish, EU/EEA/Swiss, third-country, or unknown;
- broad basis: work, study, family, business, protection, or another category;
- current location: outside Poland, in Poland, or unknown;
- voivodeship or municipality when office ownership matters;
- target date or known deadline;
- the administrative goal and the official term you encountered.

Do not put a name, address, PESEL number, document number, case number,
credential, personal record, screenshot, correspondence, tax or health record,
or full personal narrative into chat, the bundled CLI/MCP, a public search, or a
durable agent file. If an explicitly selected caller-owned Browser or Computer
operator is needed, enter secrets only into the official site's own UI and
authorize the minimum record access for that task. The operator must not retain,
log, or copy that material beyond the live task.

## A Good First Request

> I am a third-country national already in Poland on a work-related basis. I
> need a source-backed orientation for residence and work steps in Mazowieckie.
> Ask only non-identifying questions, separate candidate routes from unknowns,
> cite the competent official sources, and stop before any account interaction.

The plugin should not infer eligibility from that request. It should expose
missing facts, show candidate routes, and identify what needs current official
verification.

If the agent says a tool or host integration is available, ask it to distinguish:

- packaged: the component exists in the Poland checkout;
- preflight passed: the component started locally through the configured launcher;
- discovered: the current agent host actually lists and can call it.

Only the last state proves host discovery. Poland's doctor never invokes the
agent host and never sends telemetry or network traffic.

## Caller-Owned Operator Example

The plugin bundles no Browser, Computer, credentials, or authenticated account.
When the calling host already has an operator and the task needs one, use a
request such as:

> Use my installed Browser or Computer operator for this one official Poland
> task. Show the exact official hostname, then stop while I authenticate in the
> site's own UI. After login, inspect only the record needed for this request and
> prepare the supported fields without retaining or logging personal data. Show
> me a fresh action-time summary of the authority, form, scope, amount if any,
> deadline, and external effect. Wait for my confirmation before the final
> submission, then verify the receipt, report only minimal non-sensitive status,
> and tell me where the receipt remains visible. If the interface or evidence is
> unclear, stop and give me a manual fallback.

Authorization to inspect or fill is task-scoped. It does not authorize another
case, durable storage, background monitoring, or a consequential click without
the fresh confirmation described above.

## Reading the Answer

- `candidate` means a route deserves further verification; it is not approval.
- `not_applicable` means the supplied categories rule out that route under the
  packaged contract.
- `undetermined` means evidence or intake is insufficient, stale, or conflicting.
- A freshness warning means the source should be checked again before relying on
  the material fact.
- A public-only landing-page handoff means the agent stops and you continue.
  In an explicitly authorized operator task, it may instead resume after your
  private authentication, assist within the agreed scope, pause for every
  action-time confirmation, and verify the official receipt.

## When to Use a Professional

Use a qualified professional or the competent authority when a material legal,
tax, medical, financial, or immigration decision depends on facts the plugin
cannot establish. Use the appropriate official emergency or crisis service for
immediate danger; do not wait for an agent response.
