# Poland plugin privacy

The Poland plugin has no built-in telemetry, analytics, account system, remote
database, advertising identifier, or user-session log. Its core library, CLI, and
MCP server read packaged public data offline. The MCP server performs no network
requests and writes no files.

## Non-retention boundary

The supported public workflow uses non-identifying categories and public source
IDs. It must not request, retain, inspect, transform, transmit, or echo names,
addresses, PESEL or document numbers, case numbers, credentials, tax or health
records, employment contracts, correspondence, screenshots, uploaded files, or
free-form personal narratives.

Do not put personal data in CLI arguments, MCP calls, receipts, logs, tests, or
GitHub issues. The plugin has no case-file or profile-persistence commands and
must not be used to store personal cases. Consent does not expand
this boundary.

## Public source probe

The optional source probe makes an unauthenticated request only to an exact HTTPS
origin declared for a packaged public source ID. It sends a plugin user agent and
no cookies, credentials, personal identifiers, or case payload. It returns bounded
metadata and does not save response content. The remote authority and ordinary
network providers can still observe connection metadata such as IP address under
their own policies.

## Browser and external tools

The plugin does not bundle a browser adapter or authenticated integration.
Caller-owned Browser or Computer tools may be used only for visible public-page
verification or to open an exact official landing page and stop. Login and every
subsequent interaction belong to the user; the agent must not inspect the session
or a personal record.

External tools retain their own privacy behavior, which this plugin cannot change
or guarantee. Do not transfer personal data from them into Poland plugin inputs or
artifacts.

Report security issues through [SECURITY.md](SECURITY.md). Never put a personal
case, document, screenshot, credential, or unredacted log in a public issue.
