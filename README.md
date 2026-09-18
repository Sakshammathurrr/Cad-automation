<div align="center">

<!-- demo gif omitted: LFS asset not present in this fork -->




Install locally with
[`scripts/install/install-skills-saksham.sh`](scripts/install/install-skills-saksham.sh)
(see [SETUP.md](SETUP.md)).

| Skill        | Summary                                                                                                                                            | Source                                              |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| CAD          | Creates and edits CAD models from plain-language or image requests, with STEP as the main output along with options to export to STL, 3MF and GLB. | [skills/cad](skills/cad/SKILL.md)                   |
| CAD Viewer   | Shows local browser previews for CAD and related files.                                                                                     | [skills/cad-viewer](skills/cad-viewer/SKILL.md)     |
| DXF          | Creates 2D DXF drawings like profiles, templates, gaskets, and cut layouts from Python sources or CAD geometry.                                    | [skills/dxf](skills/dxf/SKILL.md)                   |
| step.parts   | Finds off-the-shelf STEP parts like screws, bearings, motors, and connectors.                                                                      | [skills/step-parts](skills/step-parts/SKILL.md)     |

### Optional (in tree, not linked by default)

| Skill        | Summary                                                                                                                                            | Source                                              |
| ------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| URDF         | Writes robot structure files with links, joints, limits, inertials, and meshes.                                                                    | [skills/urdf](skills/urdf/SKILL.md)                 |
| SRDF         | Adds MoveIt planning groups, end effectors, poses, and collision rules to a URDF.                                                                  | [skills/srdf](skills/srdf/SKILL.md)                 |
| SDF          | Creates simulator models and worlds with frames, physics, sensors, and lights.                                                                     | [skills/sdf](skills/sdf/SKILL.md)                   |
| SendCutSend  | Checks DXF and STEP files before upload to SendCutSend.                                                                                            | [skills/sendcutsend](skills/sendcutsend/SKILL.md)   |
| DfAM Check   | Measures mesh printability per process: wall thickness, overhangs, support volume, and build orientation.                                          | [skills/dfam-check](skills/dfam-check/SKILL.md)     |
| G-code       | Slices supported mesh files into validated, printer-profiled FDM `.gcode` with real slicer CLIs.                                                   | [skills/gcode](skills/gcode/SKILL.md)               |
| Bambu Labs   | Dry-runs, uploads, and cautiously starts local Bambu Lab print jobs from validated `.gcode`.                                                       | [skills/bambu-labs](skills/bambu-labs/SKILL.md)     |

## 💻 Installation

Prefer a **local checkout**. Do not publish under the public `cadgen` PyPI name.

### Local skills (recommended)

```bash
scripts/install/install-skills-saksham.sh --agent project
```

### Cursor MCP (local)

```powershell
.\.venv\Scripts\python.exe -m pip install -e .\packages\cadgen-mcp
```

Copy [mcp.local.json.example](mcp.local.json.example) into Cursor MCP settings and
point `command` at this checkout’s `.venv` Python.

### Windows 11: Smart App Control

The CAD kernel behind the `cad`, `cad-viewer`, `dxf`, `urdf`, `srdf` and `sdf`
skills is `OCP`, OpenCascade's Python binding, and its wheel ships an unsigned
native module. Windows 11's Smart App Control blocks unsigned native code, so
on a machine where it is on (the default on a fresh install) every `cadgen`
command and `import build123d` fails with
`ImportError: DLL load failed while importing OCP`, and Event Viewer records
the refusal as Event ID 3077 under CodeIntegrity › Operational. `cadgen doctor`
names this when it sees it.

Smart App Control has no per-app exception. Either turn it off (Settings ›
Privacy & security › Windows Security › App & browser control › Smart App
Control settings; once off it can only be turned back on by reinstalling
Windows) or run the CAD skills under WSL, where it does not apply. The wheel
is built by the cadquery-ocp project, so signing it is not something this
repository can do.

