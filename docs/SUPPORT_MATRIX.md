# Support Matrix

This matrix separates packaged capability from native host discovery. A green
repository or doctor result does not prove that an agent application loaded the
plugin. Native discovery must be checked in that application after an explicit
user-scope installation.

## Release 0.2.0 pre-publication evidence

Test date: 2026-08-21. The evidence below was collected from the complete
0.2.0 release candidate. The immutable Git tag and GitHub checks bind the
published release to its final commit.

| Runtime | Python | Host profile | Skills packaged | Offline bundle | MCP round trip | Native host discovery | Result |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| Windows NT 10.0.26200 AMD64 | CPython 3.11.9; configured launcher 3.12.10 | Codex | 33 | pass | 11 tools plus `poland_overview` pass | not checked | package preflight pass |
| Windows NT 10.0.26200 AMD64 | CPython 3.11.9; configured launcher 3.12.10 | Claude Code | 33 | pass | 11 tools plus `poland_overview` pass | not checked | package preflight pass |
| Windows NT 10.0.26200 AMD64 | CPython 3.11.9; configured launcher 3.12.10 | Cursor | 33 | pass | 11 tools plus `poland_overview` pass | not checked | package preflight pass |
| Windows NT 10.0.26200 AMD64 | CPython 3.11.9 | pi | 33 | pass | bundled server pass; not registered by pi package | not checked | skills-package preflight pass |
| Ubuntu 24.04.4 LTS x86_64 under WSL | CPython 3.12.3 | Codex | 33 | pass | 11 tools plus `poland_overview` pass | not checked | package preflight pass |
| Ubuntu 24.04.4 LTS x86_64 under WSL | CPython 3.12.3 | Claude Code | 33 | pass | 11 tools plus `poland_overview` pass | not checked | package preflight pass |
| Ubuntu 24.04.4 LTS x86_64 under WSL | CPython 3.12.3 | Cursor | 33 | pass | 11 tools plus `poland_overview` pass | not checked | package preflight pass |
| Ubuntu 24.04.4 LTS x86_64 under WSL | CPython 3.12.3 | pi | 33 | pass | bundled server pass; not registered by pi package | not checked | skills-package preflight pass |

All doctor runs used `--as-of 2026-08-21`, made no network request, reported no
Poland telemetry, validated 134 fresh source records plus one documented
future-effective source, and matched version 0.2.0
across Codex, Claude, Cursor, package metadata, and the MCP server.

## Native clean-install receipt fields

Before claiming a host is supported for a published release, record:

- immutable release tag, commit, Git tree, and manifest hashes;
- host application and exact version;
- operating system and architecture;
- installation scope and changed paths;
- host-loaded skill count;
- host-visible MCP server and a read-only tool result;
- update and removal procedure;
- test date and result.

The release CI and an immutable clean-checkout validation must also pass. A
future row may move native discovery from `not checked` to `pass` only when the
host's own inventory supplies that evidence.
