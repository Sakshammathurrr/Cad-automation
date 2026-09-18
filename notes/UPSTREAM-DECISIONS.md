# Declined / deferred upstream features

Local fork decision log. We track gaps versus public text-to-cad without
pulling foreign branding or release automation into this tree.

## implicit-cad (declined)

Upstream’s public docs list an experimental **Implicit CAD** skill (GLSL
signed-distance fields + Viewer raymarch). This checkout has no
`skills/implicit-cad/` and we are **not** cherry-picking it.

Reasons:

- saksham day-to-day work is STEP / DXF handoff, not browser SDF sculpting
- Raymarch viewer hooks would expand `packages/cadgen-js` and the Viewer
  without a clear engineering deliverable
- Keeping surface area small beats matching every upstream demo skill

Revisit only if a project explicitly needs implicit/SDF modeling in-browser.

## Other upstream items we also skip for now

| Item | Decision |
| --- | --- |
| PyPI `cadgen` publish / OIDC release workflows | Frozen — editable install only |
| Vercel docs deploy | Ignore until we own a docs host |
| Hobby skills (Bambu, G-code, DfAM, SendCutSend) | Remain in tree; not linked by `install-skills-bmcd.sh` |
| Robot stack (URDF / SRDF / SDF) | Remain in tree; enable only if a robotics job needs them |

## How to re-check later

Compare skill folders against a fresh upstream archive offline; do not set a
permanent `upstream` remote that reintroduces third-party identity into
day-to-day `git remote -v` unless you intentionally want sync.
