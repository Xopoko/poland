# Install Poland

Poland is a repository-root plugin and Agent Skills pack. A correct installation
preserves the complete repository because skills resolve shared data, references,
schemas, scripts, and the MCP server through the plugin root.

Do not install by copying individual `skills/` directories. A partial copy may
look discoverable and then fail when a workflow needs its evidence or tools.

## Before You Install

- Git is required for a local checkout.
- Python 3.11 or newer is required for validation, the CLI, and MCP server.
- Installation grants no access to government accounts, browsers, documents,
  credentials, or personal records.
- Use non-identifying categories in plugin inputs.

To delegate installation safely, give an agent this complete prompt:

> Install Poland from https://github.com/Xopoko/poland on this computer.
> Validate the source first, preserve the complete repository so its skills can
> reach bundled data, references, schemas, scripts, and MCP server, configure it
> only for the agent you are currently running, and report exactly what changed.
> Do not request credentials, enable authenticated integrations, or perform any
> external action.

## Codex

Add the GitHub repository as a marketplace, install the `poland` plugin, and
inspect its entry:

```bash
codex plugin marketplace add Xopoko/poland
codex plugin add poland@poland
codex plugin list --marketplace poland
```

To inspect and validate before registering:

```bash
git clone https://github.com/Xopoko/poland.git
cd poland
python scripts/validate_package.py
python -m unittest discover -s tests
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
/plugin marketplace add Xopoko/poland
/plugin install poland@poland
/reload-plugins
```

Command-line equivalent:

```bash
claude plugin marketplace add Xopoko/poland
claude plugin install poland@poland
claude plugin list
```

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
git clone https://github.com/Xopoko/poland.git "$HOME/.cursor/plugins/local/poland"
cd "$HOME/.cursor/plugins/local/poland"
python3 scripts/validate_package.py
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force "$HOME/.cursor/plugins/local" | Out-Null
git clone https://github.com/Xopoko/poland.git "$HOME/.cursor/plugins/local/poland"
Set-Location "$HOME/.cursor/plugins/local/poland"
python scripts/validate_package.py
```

Restart Cursor or run **Developer: Reload Window**, then confirm **Poland** under
**Customize**. To update, review the new source, pull the repository, rerun the
validator, and reload Cursor.

## pi

The package declares every skill through `package.json`:

```bash
pi install https://github.com/Xopoko/poland
```

## Plug'n Skills

The [Plug'n Skills](https://github.com/Xopoko/plug-n-skills) catalog carries a
reviewed immutable Poland pin. It never installs Poland in a default or
`--include-first-party` run. Select it explicitly:

```bash
python scripts/install-codex-plugins.py --plugin poland
```

Use this standalone repository for the newest source. Use Plug'n Skills when you
want the catalog's reviewed commit and receipt.

## Validate a Checkout

From the repository root:

```bash
python scripts/validate_package.py
python scripts/poland.py validate --as-of 2026-08-20
python -m unittest discover -s tests
python scripts/token_report.py
```

All default validation is network-free. Do not run `scripts/source_probe.py`
unless you intentionally want a bounded check of one packaged public URL.

## Troubleshooting

- **Plugin is not listed:** verify the marketplace name `poland`, then reload or
  restart the host.
- **A skill cannot open a bundled file:** remove the partial install and keep the
  complete repository together.
- **Python is missing:** install Python 3.11 or newer; use `python3` where that is
  the platform command.
- **MCP does not start on Windows:** if the host cannot resolve `python3`, point
  the local MCP command at the installed Python executable without committing a
  machine-specific path.
- **A public page changed:** leave the answer undetermined, verify the competent
  authority, and report the source drift without personal case data.
