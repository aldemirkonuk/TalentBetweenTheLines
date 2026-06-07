# Project State

> GSD workflow state only. The hand-maintained narrative source-of-truth lives at the repo root: `../STATE.md` (do not duplicate it here).

## Project Reference

See: .planning/PROJECT.md (updated 2026-06-06)

**Core value:** A real broadcast clip flows end-to-end (video → coords → value/risk brain → X-ray overlay GIF) and is wired as the portfolio's Work-face flagship.
**Current focus:** Phase 1 — Video → Coordinates

## Current Position

Phase: 1 of 5 (Video → Coordinates) — Phase 0 foundation complete
Plan: 3 of 3 code-complete (waves 1–2 executed; wave 3 cell-3 filled & verified, GPU render pending)
Status: Wave 3 Task 2 (auto) DONE & verified — full Skalski/SAM2 + jersey OCR notebook; Task 3 (Colab GPU render + SC4 + artifacts) pending user run; phase verification deferred until then
Last activity: 2026-06-07 — Wave 3: rebuilt colab_read_the_floor.ipynb as a faithful Skalski/SAM2 port, then RECONCILED it line-by-line against the authoritative Skalski notebooks in Skalski_Colab/ (detect-track-identify is the reference). Fixed 3 fidelity gaps: added `sv.filter_segments_by_distance` to SAM2Tracker.propagate (was missing — affects masks/coords), matched SAM2 checkpoint strings, made homography Skalski-verbatim (`np.array(config.vertices)[mask]`). Verbatim now: installs, model ids/thresholds, SAM2Tracker, team fit, jersey OCR (IoS match + ConsecutiveValueTracker vote), CourtConfiguration(NBA,FEET), court map. Our additions kept + labeled: ball detection (class 0), frames_out contract, inline asserts, brain/render. THEN wired Skalski extras per user request: clean_paths (Savitzky-Golay cleaned court map, cell 9c) + ShotEventTracker make/miss (cell 12), both verbatim params. Still NOT wired: RichLabelAnnotator roster names (clip-specific). All Task-2 checks green (incl filter_segments_by_distance, clean_paths, ShotEventTracker).

Progress: [██████░░░░] Phase 0 done; Phase 1 waves 1–2 done + wave 3 code-complete (GPU render pending); Phases 2–5 not started

## Performance Metrics

**Velocity:**
- Total plans completed: 2 (this milestone)
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

- [Phase 1]: Colab cell 3 is now FILLED (full Skalski/SAM2 + jersey OCR) and structurally verified, but no real clip has rendered end-to-end yet — the GPU render (Task 3) is the remaining critical unlock. SAM2 `large` + SmolVLM2 needs ~A100; on T4 use SAM2 `tiny` + `RUN_OCR=False`.
- [Phase 2]: Value model is "shoot now" only (CON-value-model-scope); full EPV is required to lift it.
- [Phase 1+]: Beaten Index should not ship as a trustworthy per-possession metric until PBP-anchored possession is in place (CON-possession-edge-cases).
- [Phase 3]: The Tell/Snitch is data-volume constrained; Moneyball-for-Vision risks failing NBA→HS/college transfer (CON-data-availability).

## Deferred Items

| Category | Item | Status | Deferred At |
|----------|------|--------|-------------|
| Reads suite | REQ-reads-suite (Open Man, Gravity, Skip, Hot Zones, Spacing Grade, etc.) | v2 — most depend on EPV surface | 2026-06-06 |

## Session Continuity

Last session: 2026-06-07
Stopped at: Wave 3 Task 2 (auto) complete & verified — colab_read_the_floor.ipynb is the full Skalski/SAM2 + jersey-OCR pipeline emitting frames_out into the unchanged adapter→brain→render path; 01-03-SUMMARY written; STATE/ROADMAP updated. Next (Task 3, GPU): run the notebook top-to-bottom on the Colab clip, confirm the Skalski court-map GIF matches Skalski + the inline asserts pass, download frames_out.pkl, then locally render prototypes/video_matchup.gif + stills and run validate_video.py for SC4. Phase verification runs after that.
Resume file: None
