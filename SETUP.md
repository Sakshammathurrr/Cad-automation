# Local setup (sakshammathurrr)

One-page guide to run this checkout on a workstation. Everything stays local:
editable `cadgen`, local skill links, no PyPI publish, no remote deploy required.

## Requirements

- Python 3.11+ (3.12 recommended)
- Node.js 22+ (for the packaged JS runtime and Viewer client)
- Git for Windows (provides Git Bash for `scripts/*.sh`)
- Prefer **WSL2** on Windows 11 if Smart App Control is on — the unsigned OCP
  DLL is blocked by SAC with no per-app exception (see README)

## Bootstrap

PowerShell (native Windows):

```powershell
git lfs install
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$gitBash = 'C:\Program Files\Git\bin\bash.exe'
& $gitBash scripts/bundle/bundle.sh
```

If `bundle.sh` stops on missing `rsync` (common on native Windows without
Git/rsync on PATH), build the Viewer client directly:

```powershell
npm --prefix apps/viewer install
npm --prefix apps/viewer run build
```

Node/browser stages from an earlier partial `bundle.sh` may already exist under
`packages/cadgen/src/cadgen/_runtime/`; `apps/viewer/dist` is what a checkout
Viewer needs when the packaged viewer stage is incomplete.

WSL / Linux / macOS:

```bash
git lfs install
python3.12 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements-dev.txt
scripts/bundle/bundle.sh
```

Do **not** `pip install -r skills/*/requirements.txt` alone — that pulls a
published `cadgen` wheel instead of this checkout.

## Smoke test

```powershell
.\.venv\Scripts\python.exe -m cadgen.cli doctor
.\.venv\Scripts\python.exe -m cadgen.cli viewer --help
```

`doctor` must print the installed version (matches `VERSION`). If `import OCP`
fails on Windows with `DLL load failed`, disable Smart App Control or move the
venv into WSL and reinstall there.

Optional Viewer smoke (needs a built client — `bundle.sh` or
`npm --prefix apps/viewer run build`):

```powershell
cd $env:TEMP
# from a directory that contains a .step file, or the repo after LFS checkout
& <repo>\.venv\Scripts\python.exe -m cadgen.cli viewer --host 127.0.0.1 --json
```

Stop with `viewer stop` or Ctrl+C.

## Local skills for Cursor / agents

From this repo (no GitHub install required):

```powershell
$gitBash = 'C:\Program Files\Git\bin\bash.exe'
& $gitBash scripts/install/install-skills-saksham.sh --agent project
```

That links only the saksham-supported subset (`cad`, `cad-viewer`, `dxf`,
`step-parts`). See [README.md](README.md).

## Cursor MCP (local)

```powershell
.\.venv\Scripts\python.exe -m pip install -e .\packages\cadgen-mcp
```

Copy [mcp.local.json.example](mcp.local.json.example) into your Cursor MCP
config and point `command` at this checkout’s `.venv` Python. Tools wrap the
local `cadgen` CLI only.

## What we do not do in this fork

- Do not bump `VERSION` or run upstream release / PyPI workflows
- Do not publish under the public `cadgen` PyPI name
- Do not deploy docs to Vercel unless you intentionally add secrets later
