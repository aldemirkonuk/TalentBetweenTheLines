# Roadmap: Read the Floor

## Overview

Read the Floor already has a validated brain: on open SportVU 2015-16 coordinates it identifies who guards whom, prices the floor in expected points, and renders the read as a broadcast X-ray (Phase 0, done). The flagship milestone now drives that proven brain onto real footage and grows the read. Phase 1 is the critical unlock — prove video→coordinates on one real clip so everything portfolio-facing has a real-footage render to show. Phase 2 deepens the value model on the proven SportVU path (Points Left / Decision Grade, then the full EPV surface), removing the biggest honest limitation. Phase 3 adds the research-backed differentiators (Set Perfectionist, The Tell→Snitch, Moneyball for Vision). Phase 4 layers in biomechanics (pose angles + Combine anthropometrics) as a parallelizable track. Phase 5 wires the flagship onto the portfolio cube's Work face. The headline proof is a real clip rendered with the X-ray read — not just coordinates.

## Phases

**Phase Numbering:**
- Phase 0: completed foundation (built & validated before this milestone)
- Integer phases (1, 2, 3): planned milestone work
- Decimal phases (2.1, 2.2): urgent insertions (marked INSERTED)

- [x] **Phase 0: Foundation (Done)** - Validated brain on SportVU coords: schema, matchup, beaten index, possession/hoop, value, anthro join, X-ray render
- [ ] **Phase 1: Video → Coordinates** - Prove the Skalski video pipeline on one real clip → brain → broadcast X-ray overlay GIF (the critical unlock)
- [ ] **Phase 2: Points Left + EPV Surface** - Decision Grade then full EPV surface (pass/drive/turnover) on the proven SportVU path
- [ ] **Phase 3: Differentiators** - Set Perfectionist, The Tell→Snitch, and Moneyball for Vision (research-backed, higher risk)
- [ ] **Phase 4: Body & Angles Layer** - Biomechanics: pose-derived angles + Combine anthropometrics → scoring/finishing/defense metrics
- [ ] **Phase 5: Portfolio Integration** - Wire Read the Floor onto the cube's Work face as the flagship project card

## Phase Details

### Phase 0: Foundation (Done)
**Goal**: A validated value-and-risk brain runs end-to-end on open SportVU 2015-16 coordinates and renders the read.
**Depends on**: Nothing (pre-milestone foundation)
**Requirements**: REQ-tracking-schema, REQ-matchup-engine, REQ-beaten-index, REQ-possession-hoop-detection, REQ-shot-quality-value, REQ-anthro-join, REQ-top-down-render
**Success Criteria** (what was made TRUE — all verified):
  1. A SportVU `.7z` clip runs `run_sportvu.py --auto` locally (CPU-only) and produces `matchup_engine.gif`
  2. The engine assigns each defender to his man with near-perfect bijection (~0.997) and low swap (~0.004)
  3. Possession and attacking hoop are inferred from ball control (inversion fixed: 0.09→0.99 on the bad possession)
  4. Every shot is graded in expected points (leave-game-out AUC 0.63, calibrated) and colors the floor render
  5. The read renders as an orientation-aware top-down X-ray overlay (mirrors for left-hoop possessions)
**Plans**: Complete (no new plans — recorded as foundation)
**Status**: Complete

### Phase 1: Video → Coordinates
**Goal**: A real broadcast clip flows video → coordinates → brain → broadcast X-ray overlay GIF — the critical unlock that gives the portfolio a real-footage render.
**Depends on**: Phase 0
**Requirements**: REQ-video-to-coords
**Success Criteria** (what must be TRUE):
  1. The Skalski Colab cell 3 is filled (RF-DETR detection + SAM2 tracking + SigLIP/UMAP/KMeans teams + SmolVLM2 jersey numbers + keypoints→homography) and runs on one real clip producing `frames_out` per frame
  2. The Skalski adapter converts `frames_out` into the shared `schema.py` tracking table with no schema fork
  3. The existing brain (matchup + Beaten Index + value + render) runs on the video-derived coordinates and produces a broadcast X-ray overlay GIF
  4. The video-path numbers are sanity-checked against the SportVU baseline, with stills saved to `frames/` and the GIF to `prototypes/`
**Plans**: TBD
**UI hint**: no

### Phase 2: Points Left + EPV Surface
**Goal**: The read prices not just "shoot now" but the full decision — quantifying expected points lost vs the optimal read across pass / drive / turnover options — removing the biggest honest limitation.
**Depends on**: Phase 1 (renders on the proven SportVU path; no new pipeline required)
**Requirements**: REQ-points-left / REQ-decision-grade, REQ-epv-surface
**Success Criteria** (what must be TRUE):
  1. Each decision shows a Points-Left delta (EV(best read) − EV(chosen)) and these cumulate into a running tally over a possession
  2. A Decision Grade is emitted comparing the actual chosen action to the optimal read
  3. The value model grows from "shoot now" into a full EPV surface with pass-success, drive, and turnover probabilities as spatial functions
  4. The EPV surface renders as a heatmap with a running expected-points counter on the overlay
**Plans**: TBD
**UI hint**: no

### Phase 3: Differentiators
**Goal**: Read the Floor carries capabilities no stock pipeline has — recognizing and grading sets, mining telegraphed tendencies into a scouting report, and scoring court vision independent of scoring.
**Depends on**: Phase 2 (Decision Grade feeds Moneyball; EPV/value feeds the reads)
**Requirements**: REQ-set-perfectionist, REQ-tell-snitch, REQ-moneyball-vision
**Success Criteria** (what must be TRUE):
  1. The system classifies the set being run and grades execution against an ideal template (HoopTransformer-style trajectory encoder)
  2. Pre-decision micro-features are mined into tendency patterns and compiled into a one-page scouting report (The Tell → The Snitch)
  3. Decision Grade is applied across a prospect's film to produce a Court-Vision percentile with a supporting clip reel (cross-level NBA→HS/college transfer is the named risk)
**Plans**: TBD
**UI hint**: no

### Phase 4: Body & Angles Layer
**Goal**: A biomechanics layer enriches the read with pose-derived orientation and Combine-joined anthropometrics, linking body to scoring, finishing, passing, and defense.
**Depends on**: Phase 1 (needs the pose adapter on the video path); parallelizable with Phases 2–3
**Requirements**: REQ-body-angles-layer
**Success Criteria** (what must be TRUE):
  1. A pose adapter emits per-player per-frame angle columns (`foot_angle`, `hip_angle`, `shoulder_angle`, `knee_bend`) extending the same `schema.py` contract — no schema fork
  2. Combine anthropometrics merge via `players_anthro.csv` by identity (lengths from Combine, angles from pose — never measured from video)
  3. Brain modules (`square_up.py`, `stance.py`, `anthro_corr.py`) turn angles + anthropometrics into Square-Up Score, Stance Read, and defense/finishing metrics surfaced on the overlay
**Plans**: TBD
**UI hint**: no

### Phase 5: Portfolio Integration
**Goal**: Read the Floor appears as the flagship project card on the portfolio cube's Work face, presenting the real-clip X-ray overlay as the thesis made executable.
**Depends on**: Phase 1 (needs a real-clip overlay GIF/stills to show); benefits from Phases 2–4 but ships on the Phase 1 render
**Requirements**: REQ-portfolio-integration
**Success Criteria** (what must be TRUE):
  1. A visitor on the cube's Work face sees Read the Floor as the leading flagship project card per the parent `CLAUDE.md` chapter map
  2. The card links/displays the overlay GIF and stills produced by the pipeline (the real-clip render is the headline proof)
  3. The card honors the locked Stone Dust × Pine Teal design system and the cube's Work-face spatial mode (frosted-glass clarify-on-cursor, depth-layered cards)
**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 0 (done) → 1 → 2 → 3 → 4 → 5. Phase 4 (Body & Angles) is a parallelizable track and may run alongside Phases 2–3 once Phase 1 lands.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 0. Foundation (Done) | — | Complete | pre-milestone |
| 1. Video → Coordinates | 0/TBD | Not started | - |
| 2. Points Left + EPV Surface | 0/TBD | Not started | - |
| 3. Differentiators | 0/TBD | Not started | - |
| 4. Body & Angles Layer | 0/TBD | Not started | - |
| 5. Portfolio Integration | 0/TBD | Not started | - |
