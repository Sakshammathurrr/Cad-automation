# cadgen-mcp

Local **stdio MCP** server that wraps this checkout’s `cadgen` CLI. No cloud
services, no third-party CAD MCP stack — one geometry runtime.

## Install (editable, from repo root)

```powershell
.\.venv\Scripts\python.exe -m pip install -e .\packages\cadgen-mcp
```

`cadgen` must already be available in that interpreter (`requirements-dev.txt`).

## Cursor

Copy `mcp.local.json.example` from the repo root into your Cursor MCP settings
and fix the Python path to this checkout’s `.venv`.

## Tools

| Tool | cadgen behind it |
| --- | --- |
| `doctor` | `cadgen doctor` |
| `snapshot` | `cadgen snapshot <path>` |
| `step_snapshot` | `cadgen step snapshot <path>` |
| `viewer_url` | `cadgen viewer --host 127.0.0.1 --json` |
| `cadgen` | arbitrary short CLI argv (refuses `daemon`) |
