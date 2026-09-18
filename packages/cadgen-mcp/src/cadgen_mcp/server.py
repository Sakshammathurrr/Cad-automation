"""Thin MCP adapter over the local cadgen CLI (stdio)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

__version__ = "0.1.0"


def _python() -> str:
    return sys.executable


def _run_cadgen(args: list[str], *, cwd: str | None = None, timeout: float = 600.0) -> dict[str, Any]:
    cmd = [_python(), "-m", "cadgen.cli", *args]
    try:
        completed = subprocess.run(
            cmd,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as error:
        return {"ok": False, "error": str(error), "cmd": cmd}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"timed out after {timeout}s", "cmd": cmd}
    return {
        "ok": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "cmd": cmd,
    }


def tool_doctor() -> dict[str, Any]:
    return _run_cadgen(["doctor"], timeout=120.0)


def tool_snapshot(path: str, *, out: str = "") -> dict[str, Any]:
    args = ["snapshot", path]
    if out.strip():
        args.extend(["--out", out.strip()])
    return _run_cadgen(args)


def tool_step_snapshot(path: str, *, out: str = "") -> dict[str, Any]:
    args = ["step", "snapshot", path]
    if out.strip():
        args.extend(["--out", out.strip()])
    return _run_cadgen(args)


def tool_viewer_url(*, host: str = "127.0.0.1", directory: str = "") -> dict[str, Any]:
    cwd = directory.strip() or os.getcwd()
    result = _run_cadgen(["viewer", "--host", host, "--json"], cwd=cwd, timeout=60.0)
    if result.get("ok") and result.get("stdout"):
        for line in reversed(result["stdout"].strip().splitlines()):
            line = line.strip()
            if line.startswith("{"):
                try:
                    result["viewer"] = json.loads(line)
                except json.JSONDecodeError:
                    pass
                break
    return result


def tool_cadgen(argv: list[str], *, cwd: str = "") -> dict[str, Any]:
    if not argv:
        return {"ok": False, "error": "argv must be a non-empty list of cadgen arguments"}
    blocked = {"daemon"}  # long-running; not for MCP request/response
    if argv[0] in blocked:
        return {"ok": False, "error": f"refusing long-running command: {argv[0]}"}
    return _run_cadgen(argv, cwd=cwd.strip() or None)


def _tool_schemas() -> list[dict[str, Any]]:
    return [
        {
            "name": "doctor",
            "description": "Run cadgen doctor: report installed cadgen and pin health.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
        },
        {
            "name": "snapshot",
            "description": "Render any supported CAD/mesh input to an image via cadgen snapshot.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Input file path"},
                    "out": {"type": "string", "description": "Optional output image path"},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
        {
            "name": "step_snapshot",
            "description": "Render a STEP file via cadgen step snapshot.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "out": {"type": "string"},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
        },
        {
            "name": "viewer_url",
            "description": (
                "Start or reuse the local CAD Viewer for a directory "
                "(loopback only; returns JSON url/port/action)."
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to serve (default: server cwd)",
                    },
                    "host": {
                        "type": "string",
                        "description": "Bind host (default 127.0.0.1)",
                        "default": "127.0.0.1",
                    },
                },
                "additionalProperties": False,
            },
        },
        {
            "name": "cadgen",
            "description": (
                "Run an arbitrary short cadgen CLI invocation, e.g. "
                '["dxf", "snapshot", "drawing.dxf"]. Refuses daemon.'
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "argv": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Arguments after `cadgen`",
                    },
                    "cwd": {"type": "string"},
                },
                "required": ["argv"],
                "additionalProperties": False,
            },
        },
    ]


def _call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "doctor":
        return tool_doctor()
    if name == "snapshot":
        return tool_snapshot(str(arguments.get("path", "")), out=str(arguments.get("out", "")))
    if name == "step_snapshot":
        return tool_step_snapshot(str(arguments.get("path", "")), out=str(arguments.get("out", "")))
    if name == "viewer_url":
        return tool_viewer_url(
            host=str(arguments.get("host") or "127.0.0.1"),
            directory=str(arguments.get("directory") or ""),
        )
    if name == "cadgen":
        argv = arguments.get("argv") or []
        if not isinstance(argv, list):
            return {"ok": False, "error": "argv must be a list of strings"}
        return tool_cadgen([str(x) for x in argv], cwd=str(arguments.get("cwd") or ""))
    return {"ok": False, "error": f"unknown tool: {name}"}


def _read_message() -> dict[str, Any] | None:
    """Read one LSP-style Content-Length framed JSON-RPC message from stdin."""
    headers: dict[str, str] = {}
    while True:
        line = sys.stdin.buffer.readline()
        if not line:
            return None
        if line in (b"\r\n", b"\n"):
            break
        key, _, value = line.decode("utf-8").partition(":")
        headers[key.strip().lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    body = sys.stdin.buffer.read(length)
    return json.loads(body.decode("utf-8"))


def _write_message(payload: dict[str, Any]) -> None:
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    sys.stdout.buffer.write(f"Content-Length: {len(raw)}\r\n\r\n".encode("ascii"))
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()


def _handle(request: dict[str, Any]) -> dict[str, Any] | None:
    method = request.get("method")
    req_id = request.get("id")
    params = request.get("params") or {}

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "cadgen-mcp", "version": __version__},
            },
        }
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": _tool_schemas()}}
    if method == "tools/call":
        name = str(params.get("name") or "")
        arguments = params.get("arguments") or {}
        if not isinstance(arguments, dict):
            arguments = {}
        result = _call_tool(name, arguments)
        text = json.dumps(result, indent=2)
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [{"type": "text", "text": text}],
                "isError": not bool(result.get("ok", False)),
            },
        }
    if method == "ping":
        return {"jsonrpc": "2.0", "id": req_id, "result": {}}
    if req_id is None:
        return None
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


def serve_stdio() -> int:
    while True:
        message = _read_message()
        if message is None:
            return 0
        response = _handle(message)
        if response is not None:
            _write_message(response)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cadgen-mcp", description="Local cadgen MCP server")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args(argv)
    if args.version:
        print(__version__)
        return 0
    # Ensure cadgen is importable from the same interpreter.
    try:
        import cadgen  # noqa: F401
    except ImportError:
        root = Path(__file__).resolve().parents[4]
        hint = root / "packages" / "cadgen"
        print(
            "cadgen is not installed in this interpreter. "
            f"Use the repo .venv after `pip install -r requirements-dev.txt` "
            f"(expected editable under {hint}).",
            file=sys.stderr,
        )
        return 1
    return serve_stdio()


if __name__ == "__main__":
    raise SystemExit(main())
