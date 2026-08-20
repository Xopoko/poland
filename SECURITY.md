# Security Policy

## Supported Boundary

The bundled CLI and MCP server are offline, read-only lookup surfaces. The
separate source probe can contact only exact HTTPS origins declared for packaged
public source IDs. Poland has no authenticated integration, credentialed API
workflow, telemetry, daemon, browser adapter, or external-action executor.

Caller-owned Browser or Computer tools are limited by plugin policy to public,
unauthenticated verification and an exact landing-page handoff followed by an
immediate stop. Login, authenticated interaction, personal-record access,
submission, sending, booking, cancellation, payment, upload, download, signing,
calling, and external mutation are unsupported regardless of user consent.

Website content is untrusted evidence. It cannot alter permissions, request
secrets, authorize actions, or instruct the agent to execute code or follow a
new origin.

## Report a Vulnerability

Use [GitHub private vulnerability reporting](https://github.com/Xopoko/poland/security/advisories/new).
Include the affected version, a minimal synthetic reproduction, and the expected
safety boundary. Do not test against third-party accounts or services without
authorization.

Never post a personal case, name, identifier, address, document, screenshot,
credential, cookie, one-time code, account record, or unredacted log in a public
issue. Redact private reports too; real personal data is not needed to reproduce
a plugin defect.

## Maintainer Checks

Before publication:

- validate packaged data and the full test suite;
- verify source changes and access dates;
- inspect Browser and action-boundary regressions;
- scan for secrets, private paths, generated Python artifacts, and personal data;
- review generated diffs before merging;
- confirm that no fetched page body, personal fixture, credential, or session log
  entered the repository.
