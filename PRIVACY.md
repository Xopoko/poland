# Poland plugin privacy

The Poland plugin has no built-in telemetry, analytics, account system, remote
database, advertising identifier, or user-session log. Its core library, CLI, and
MCP server read packaged public data offline. The MCP server performs no network
requests and writes no files.

## Non-retention boundary

The bundled CLI, MCP server, source probe, datasets, receipts, and repository use
non-identifying categories and public source IDs. Never put names, addresses,
PESEL or document numbers, case numbers, credentials, tax or health records,
employment contracts, correspondence, screenshots, uploaded files, or free-form
personal narratives into those surfaces.

Do not put personal data in CLI arguments, MCP calls, receipts, logs, tests, or
GitHub issues. The plugin has no case-file or profile-persistence commands and
must not be used to store personal cases.

## Public source probe

The optional source probe makes an unauthenticated request only to an exact HTTPS
origin declared for a packaged public source ID. It sends a plugin user agent and
no cookies, credentials, personal identifiers, or case payload. It returns bounded
metadata and does not save response content. The remote authority and ordinary
network providers can still observe connection metadata such as IP address under
their own policies.

## Browser and external tools

The plugin does not bundle a Browser or Computer adapter, authenticated
integration, credential store, or session recorder. Its skill instructions may
guide an installed caller-owned Browser, Computer tool, or approved connector.
Those tools have their own privacy behavior and permissions.

Authentication and secret entry are user-only. Capture must be paused or control
yielded before passwords, passkeys, OTPs, identity-provider choices, or payment
credentials appear. After the user says the session is ready and explicitly
authorizes the named task, the agent may inspect only the minimum relevant
personal record and fill only necessary reviewable fields. It must not copy that
content into Poland CLI/MCP calls, source receipts, repository files, tests,
public issues, or unrelated services. Prefer on-screen use over copying, redact
summaries, and drop private working context when the task ends.

Before an upload or download, show the exact file or document, origin,
destination, and purpose and obtain fresh action-time confirmation. Never browse
unrelated local files, clipboard contents, account areas, or records merely
because a session is open.

External tools and official services may retain data under their own policies,
which this plugin cannot change or guarantee. If the host cannot provide a
capture-safe handoff, the agent must use a guided manual fallback for secret or
sensitive steps.

Report security issues through [SECURITY.md](SECURITY.md). Never put a personal
case, document, screenshot, credential, or unredacted log in a public issue.
