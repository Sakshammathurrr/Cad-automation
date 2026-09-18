# Security Policy

## Scope

This repository is a local-filesystem development tool. The CAD Viewer backend
binds to loopback (`127.0.0.1`) by default and serves **unauthenticated**. Any
local process can read files under the directory the viewer opens, trigger STEP
builds/exports, and activate directories.

**Loopback binding is the trust boundary.** Non-loopback `--host` values are
refused unless you pass `--allow-remote-host` (explicit opt-in). Even then there
is no authentication — do not expose the server on a shared network.

## Reporting a Vulnerability

If you discover a security vulnerability, report it privately to your internal
security contact. Do **not** open a public issue for a security vulnerability.

Include a description, reproduction steps, and potential impact.

## Supported Versions

Only the latest checkout on this fork is supported for internal use.

| Version | Supported |
|---------|-----------|
| latest local checkout | Yes |
| older | No |
