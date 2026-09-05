# Install Poland

Poland is a repository-root plugin and Agent Skills pack. A correct installation
preserves the complete repository because skills resolve shared data, references,
schemas, scripts, and the MCP server through the plugin root. Python executable
names differ across operating systems, so the bundled doctor must prove the
actual local MCP launcher before an agent claims the MCP tools are ready.

Do not install by copying individual `skills/` directories. A partial copy may
look discoverable and then fail when a workflow needs its evidence or tools.

## Before You Install

- Git is required for a local checkout.
- Python 3.11 or newer is required for validation, the CLI, and MCP server.
- Installation grants no access to government accounts, browsers, documents,
  credentials, or personal records.
- Use non-identifying categories in plugin inputs.
- Prefer a published release tag or exact commit over mutable `main`.
- Install at user scope unless you intentionally want project or team scope.

To delegate installation safely, give an agent this complete prompt:

> Install Poland from https://github.com/Xopoko/poland for the agent host I am
> using now, at user scope only. Resolve a published release tag or exact commit,
> preserve the complete repository, and run `scripts/poland.py doctor --host`
> for this host before registration. Show one change plan for approval. After
> installation, verify 33 skills and the local MCP server separately, then report
> the version, commit, scope, changed paths, update path, removal path, and any
> host discovery that remains unverified. Do not request credentials or personal
> records, install for another host, or perform an external action.

## Host Capability Matrix

| Host | Packaged skills | Bundled CLI | MCP package binding | Proof required |
| --- | --- | --- | --- | --- |
| Codex | 33 declared | Manual local command | `.codex-mcp.json` declared | `doctor --host codex`, then Codex plugin/MCP visibility |
| Claude Code | 33 packaged | Manual local command | `.mcp.json` declared; `POLAND_PYTHON` may override the launcher | `doctor --host claude`, then `/mcp` after reload |
| Cursor | 33 declared by `.cursor-plugin/plugin.json` | Manual local command | Manifest declares `.codex-mcp.json` | `doctor --host cursor`, then Customize/MCP visibility |
| pi | 33 declared by `package.json` | Manual local command | Not registered by the pi package | `doctor --host pi`; configure MCP separately if the pi host supports it |

`doctor` validates package versions, Python 3.11+, skill inventory, the offline
data contract, source freshness, and a real initialize/tools-list/ping plus
read-only `poland_overview` round trip against the bundled stdio MCP server. It
does not call Codex, Claude Code, Cursor, or pi, so its receipt always reports
native host discovery as `not_checked` until you verify it in that host. The
command makes no network requests and emits no Poland telemetry.

For a release or support claim, retain a receipt bound to the immutable release
commit and record the host version, operating system, installation scope,
host-loaded skill count, host-visible MCP status, test date, and result. Doctor
supplies the package commit when Git metadata is present, runtime OS, packaged
count, MCP preflight, and UTC check time. It deliberately leaves host version,
scope, loaded count, and native discovery as `not_checked`/`null`; fill those
only from a clean-install check in the actual host.

The current dated evidence is published in `docs/SUPPORT_MATRIX.md`.

## Run Preflight Before Registration

From the complete checkout, use the Python 3.11+ command available on that
computer:

```bash
python scripts/poland.py doctor --host codex
python scripts/poland.py doctor --host claude
python scripts/poland.py doctor --host cursor
python scripts/poland.py doctor --host pi
```

Run only the line for the host being installed. A `valid: true` receipt proves
the package checks listed in that receipt and the configured launcher on the
current machine; it does not prove that the host has discovered the installed
plugin.

The public configs use the conventional `python3` launcher. Claude Code also
accepts a host-local `POLAND_PYTHON` override. The launcher uses Python isolated
mode and suppresses bytecode writes; the MCP server uses only the Python
standard library and bundled files. If the selected host preflight reports
`launcher_not_found`, ask the installing agent to generate a replacement
companion file outside the source checkout:

```text
python scripts/poland.py doctor --host <codex|claude|cursor> \
  --write-mcp-config <temporary-directory>/<expected-companion-filename>
```

The generated file contains the resolved local interpreter path. It is private
host configuration, not a secret, and must not be committed. The command never
merges host settings or installs anything. It writes only after the generated
configuration itself passes the MCP round trip; the receipt keeps the public
companion and generated-companion results separate. The agent must show the
file, copy it only into a separate local installation copy (`.codex-mcp.json`
for Codex or Cursor, `.mcp.json` for Claude Code), rerun doctor there, and
request approval before registering that copy. Existing output is not replaced
unless `--force` is explicitly supplied.

## Codex

Add the GitHub repository as a marketplace, install the `poland` plugin, and
inspect its entry:

```bash
codex plugin marketplace add Xopoko/poland --ref v0.2.0
codex plugin add poland@poland
codex plugin list --marketplace poland
```

The repository-native `.agents/plugins/marketplace.json` exposes Poland as
`AVAILABLE`, never `INSTALLED_BY_DEFAULT`. Registering the marketplace only
makes it discoverable; the separate `plugin add` command is the opt-in install.

To inspect and validate before registering:

```bash
git clone --branch v0.2.0 --depth 1 https://github.com/Xopoko/poland.git
cd poland
python scripts/validate_package.py
python -m unittest discover -s tests
python scripts/poland.py doctor --host codex
codex plugin marketplace add .
codex plugin add poland@poland
```

Refresh the Git marketplace snapshot with:

```bash
codex plugin marketplace upgrade poland
```

Codex currently has no separate `plugin update` command. After refreshing the
marketplace, inspect the listed and installed version; if needed, remove and
reinstall the plugin explicitly.

Remove the plugin and marketplace with:

```bash
codex plugin remove poland@poland
codex plugin marketplace remove poland
```

## Claude Code

Inside an interactive Claude Code session:

```text
/plugin marketplace add Xopoko/poland@v0.2.0
/plugin install poland@poland
/reload-plugins
```

Command-line equivalent:

```bash
claude plugin marketplace add Xopoko/poland@v0.2.0
claude plugin install poland@poland
claude plugin list
```

For ordinary personal use, choose **User** scope in the install UI. Run
`python scripts/poland.py doctor --host claude` before registration. If the
machine uses a Python executable other than `python3`, set `POLAND_PYTHON` for
the Claude process or use the reviewed host-local companion-file flow above.
After installation and `/reload-plugins`, open `/mcp` and verify the Poland
server separately from the skill inventory.

Update or remove explicitly:

```bash
claude plugin marketplace update poland
claude plugin update poland@poland
claude plugin uninstall poland@poland
claude plugin marketplace remove poland
```

## Cursor

Keep the complete checkout under Cursor's local plugin directory.

macOS or Linux:

```bash
mkdir -p "$HOME/.cursor/plugins/local"
git clone --branch v0.2.0 --depth 1 https://github.com/Xopoko/poland.git "$HOME/.cursor/plugins/local/poland"
cd "$HOME/.cursor/plugins/local/poland"
python3 scripts/validate_package.py
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME/.cursor/plugins/local" | Out-Null
git clone --branch v0.2.0 --depth 1 https://github.com/Xopoko/poland.git "$HOME/.cursor/plugins/local/poland"
Set-Location "$HOME/.cursor/plugins/local/poland"
python scripts/validate_package.py
python scripts/poland.py doctor --host cursor
```

Restart Cursor or run **Developer: Reload Window**, then confirm **Poland** under
**Customize**. The Cursor manifest explicitly declares all 33 skills and the
bundled MCP companion file. Confirm both the skill inventory and Poland MCP
server; repository validation alone is not native Cursor discovery proof. To
update, compare the current and proposed release commits, check out the reviewed
tag, rerun validation and doctor, and only then reload Cursor.

## pi

The package declares every skill through `package.json`:

```bash
pi install git:github.com/Xopoko/poland@v0.2.0
```

The pi package declares the 33 skills only. It includes the CLI and MCP server
files in the repository, but does not register the MCP server with pi. Do not
claim MCP availability in pi without separate host-specific configuration and a
real discovery check.

## Validate a Checkout

From the repository root:

```bash
python scripts/validate_package.py
python scripts/poland.py validate
python scripts/poland.py doctor --host package
python -m unittest discover -s tests
python scripts/token_report.py
npm pack --dry-run --json
```

Validation and doctor use the current UTC date by default. Reserve `--as-of`
for intentional historical checks, where later verification dates are invalid.

All default validation is network-free. The npm dry run is needed only when
checking the pi/package archive surface; it must show all 33 skills, both MCP
companion files, the Python runtime, and no bytecode caches. Do not run
`scripts/source_probe.py` unless you intentionally want a bounded check of one
packaged public URL.

## Troubleshooting

- **Plugin is not listed:** verify the marketplace name `poland`, then reload or
  restart the host.
- **A skill cannot open a bundled file:** remove the partial install and keep the
  complete repository together.
- **Python is missing:** install Python 3.11 or newer, then rerun the selected
  host's doctor command.
- **`launcher_not_found`:** use the agent-assisted host-local companion-file
  flow above. Never commit the generated absolute interpreter path.
- **Doctor passes but MCP is absent:** doctor did not inspect the agent host.
  Reload the host and use its plugin/MCP inventory before claiming discovery.
- **A public page changed:** leave the answer undetermined, verify the competent
  authority, and report the source drift without personal case data.
