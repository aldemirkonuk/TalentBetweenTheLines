# Project State

> GSD workflow state only. The hand-maintained narrative source-of-truth lives at the repo root: `../STATE.md` (do not duplicate it here).

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-06)

**Core value:** A real broadcast clip flows end-to-end (video → coords → value/risk brain → X-ray overlay GIF) and is wired as the portfolio's Work-face flagship.
**Current focus:** Phase 1 — Video → Coordinates

## Current Position

Phase: 1 of 5 (Video → Coordinates) — Phase 0 foundation complete
Plan: 3 of 3 planned (3 waves) — verified
Status: Planned & verified (plan-checker PASS, 0 blockers) — ready to execute (`/gsd-execute-phase 1`)
Last activity: 2026-06-06 — Planned Phase 1 (research → 3 plans → verify); resolved plan-checker blockers/warnings; re-verified PASS

Progress: [███░░░░░░░] Phase 0 done; Phase 1 planned+verified; Phases 2–5 not started

## Performance Metrics

**Velocity:**
- Total plans completed: 0 (this milestone)
- Average duration: —
- Total execution time: —

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: —
- Trend: —

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table (LOCKED, spec-derived):

- DEC-pipeline-fork: vision pipeline forks the Skalski/Roboflow "sports" stack; proprietary layer = value + risk + X-ray render
- DEC-tracking-schema-contract: one `schema.py` tracking table is the single contract every source adapts into
- DEC-matchup-method: who-guards-whom via optimal defender-assignment (Franks/Bornn 2015) + Hungarian + temporal smoothing
- DEC-anthro-join-not-measure: lengths from Combine join by identity; pose for angles only; foot-length dropped
- DEC-possession-by-control: possession from ball control; attacking hoop = hoop nearest controlled-ball median

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 1]: Colab cell 3 (Skalski models) is a fill-in stub and no real clip has run end-to-end — this is the critical unlock; RF-DETR/SAM2 need a Colab T4 GPU (CON-pipeline-stack).
- [Phase 2]: Value model is "shoot now" only (CON-value-model-scope); full EPV is required to lift it.
- [Phase 1+]: Beaten Index should not ship as a trustworthy per-possession metric until PBP-anchored possession is in place (CON-possession-edge-cases).
- [Phase 3]: The Tell/Snitch is data-volume constrained; Moneyball-for-Vision risks failing NBA→HS/college transfer (CON-data-availability).

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Reads suite | REQ-reads-suite (Open Man, Gravity, Skip, Hot Zones, Spacing Grade, etc.) | v2 — most depend on EPV surface | 2026-06-06 |

## Session Continuity

Last session: 2026-06-06
Stopped at: Phase 1 planned (01-01/02/03) and verified by gsd-plan-checker (PASS, 0 blockers). Next: `/gsd-execute-phase 1` — waves run 01 → 02 → 03; plan 03 is GPU-gated (Colab T4 + clip + ROBOFLOW_API_KEY) and autonomous:false.
Resume file: None
