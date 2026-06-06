# Read the Floor

## What This Is

Read the Floor is a computer-vision + machine-learning system that watches basketball footage and renders the value of the floor — who guards whom, the gap, the best read, and its risk — as a broadcast-grade X-ray overlay. It is the flagship build inside the "Talent Between the Lines" portfolio piece: built on a forked Roboflow/Skalski "sports" vision pipeline plus an original value-and-risk brain trained on open tracking data. The audience is anyone reading the portfolio (recruiters, collaborators) — the proof is a real broadcast clip rendered with the X-ray read, not just coordinates.

## Core Value

A real broadcast clip flows end-to-end (video → coordinates → value/risk brain → X-ray overlay GIF) and is wired as the portfolio's Work-face flagship — the thesis ("read the floor, find the gap, price the risk") made executable on actual footage.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. The Tier-0 foundation: built, reviewed, validated on SportVU coordinates. -->

- ✓ **REQ-tracking-schema** — single tracking-table schema (`schema.py`) every source adapts into — Phase 0
- ✓ **REQ-matchup-engine** — who-guards-whom via optimal defender-assignment (bijection ~0.997, swap ~0.004) — Phase 0
- ✓ **REQ-beaten-index** — per-matchup 0–100 likelihood the defender is about to be beaten — Phase 0
- ✓ **REQ-possession-hoop-detection** — control-based possession + attacking-hoop inference (inversion fixed 0.09→0.99) — Phase 0
- ✓ **REQ-shot-quality-value** — "shoot now" expected-points model (leave-game-out AUC 0.63, calibrated) — Phase 0
- ✓ **REQ-anthro-join** — Combine anthropometrics joined to players by identity (`anthro.py`) — Phase 0
- ✓ **REQ-top-down-render** — top-down / broadcast X-ray overlay, orientation-aware, local CPU runner — Phase 0

### Active

<!-- Current scope. Building toward these. -->

- [ ] **REQ-video-to-coords** — Skalski video→coordinates adapter proven end-to-end on one real clip (Phase 1)
- [ ] **REQ-points-left / REQ-decision-grade** — running tally of expected points lost + decision grade vs optimal read (Phase 2)
- [ ] **REQ-epv-surface** — full EPV surface (shot / pass-success / drive / turnover as spatial functions) (Phase 2)
- [ ] **REQ-set-perfectionist** — recognize the set being run and grade execution vs ideal (Phase 3)
- [ ] **REQ-tell-snitch** — mine telegraphed tendencies → auto one-page scouting report (Phase 3)
- [ ] **REQ-moneyball-vision** — court-vision percentile from Decision Grade across prospect film (Phase 3)
- [ ] **REQ-body-angles-layer** — biomechanics: pose-derived angles + Combine-joined anthropometrics → scoring/finishing/defense metrics (Phase 4)
- [ ] **REQ-portfolio-integration** — Read the Floor wired onto the cube Work face as the flagship project card (Phase 5)

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Stats dashboard — the flagship renders a spatial X-ray read, not tables/charts; dashboards are the anti-thesis
- Hard-coded rules as the flagship — every flagship piece must learn from data, not encode if/else heuristics
- Tutorial reskin — must add the layer no one else has (reading the floor + pricing the risk), not re-run a stock pipeline
- Foot-length as a feature — not in Combine data and not reliably measurable from broadcast (per BODY_AND_ANGLES.md)
- Video-measured body lengths — 2D foreshortening makes single-camera length measurement unreliable; lengths come from Combine join only
- **REQ-reads-suite** (Open Man, Gravity, Skip, Hot Zones, Spacing Grade, Mismatch Finder, etc.) — deferred backlog; most depend on the full EPV surface, surfaced after Phase 2 lands (tracked as v2)

## Context

- **Build reality (per the narrative SoT at `../STATE.md`):** the brain works end-to-end on open SportVU 2015-16 coordinates — identifies who guards whom, prices the floor in expected points, renders the read. It does NOT yet run on video; the value model is "shoot now," not full EPV.
- **Two run tracks (per `read_the_floor/SETUP.md`):**
  - Track A — local, CPU-only, ~10 min: `python run_sportvu.py <clip>.7z --auto` → `matchup_engine.gif`. Proven path.
  - Track B — Colab GPU (T4): the video pipeline (RF-DETR, SAM2, SigLIP/UMAP/KMeans teams, SmolVLM2 jersey OCR, keypoints→homography). Colab cell 3 is currently a fill-in stub — the critical unlock.
- **Validation base:** SportVU 2015-16 tracking (~55 games local, 636 on GitHub) + PBP outcomes (90,524 possessions). Matchup assignment validated and hardened (independent review, high-severity bugs fixed).
- **Recommended next order (from STATE.md):** (1) prove video→coords on one clip, (2) Points Left on the SportVU path, (3) grow value into the full EPV surface.
- **Portfolio embedding target:** the existing Next.js 14 cube site in the parent repo (Work face leads with Read the Floor per the parent `CLAUDE.md` chapter map).
- **Source-of-truth note:** a hand-maintained narrative SoT lives at the repo root `../STATE.md`. This is GSD workflow state only — see `.planning/STATE.md`.

## Constraints

- **Dependency (pipeline stack)** [CON-pipeline-stack]: vision pipeline depends on the Roboflow/Skalski stack — RF-DETR, SAM2, SigLIP→UMAP→K-Means, SmolVLM2, keypoints+homography — and three Roboflow Universe datasets (`basketball-player-detection-3-ycjdo`, `basketball-court-detection-2`, `basketball-jersey-numbers-ocr`). RF-DETR / SAM2 require a GPU (Colab T4).
- **Data / dependency** [CON-data-availability]: SportVU 2015-16 + PBP (90,524 possessions) is the training/validation base. The Tell/Snitch and Moneyball-for-Vision are data-volume / cross-level-transfer constrained (thin tracking volume for current players; NBA-trained value may not transfer to HS/college spacing).
- **Schema contract** [CON-schema-contract]: every adapter (SportVU, Skalski, pose) MUST emit the single `read_the_floor/schema.py` tracking-table schema. Body & Angles adds optional columns + a one-row-per-player `players_anthro.csv` merge — same contract, more columns, no fork.
- **Data sourcing (NFR)** [CON-anthro-source]: absolute body lengths (wingspan, reach, hand size, vertical) MUST come from published Draft Combine data joined by identity, never measured from video. Angles ARE inferred from pose.
- **Pose feasibility (NFR)** [CON-pose-feasibility]: pose foot keypoints are noisy on wide broadcast angles, cleaner on tight shots; angles (orientation) are the robust signal, not absolute segment lengths. Dunk-event detection from video is amber-feasibility.
- **Value-model scope (NFR)** [CON-value-model-scope]: the value model is "shoot now" only (nearest-defender contest + distance to attacking hoop); it does NOT yet weigh passing/driving alternatives. Full EPV is required to lift this.
- **Season mismatch (NFR)** [CON-season-mismatch]: value trains on 2014-15 shot logs while the matchup brain runs on 2015-16 tracking — acceptable for a model, but not a single unified game.
- **Possession edge cases (NFR)** [CON-possession-edge-cases]: control-based possession/hoop is validated on standard half-court possessions; PBP-anchored possession remains the gold standard for transition/inbound edges. Beaten Index should not ship as a trustworthy per-possession metric until PBP-anchored possession is in place.

## Key Decisions

<!-- LOCKED spec-derived decisions. These constrain all future work. -->

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **DEC-pipeline-fork** — vision pipeline is a fork of the Skalski/Roboflow "sports" stack (RF-DETR → SAM2 → SigLIP/UMAP/KMeans teams → SmolVLM2 jersey → keypoints/homography); proprietary layer = value surface + risk + X-ray render | Best open-source pipeline as the base; the unique value is the layer on top, not the detection | ✓ Locked (spec) |
| **DEC-tracking-schema-contract** — one tracking-table interface (`schema.py`) is the single contract every source adapts into; pose adapter extends it with columns, not a new schema | Decouples data sources from the brain; lets SportVU, video, and pose feed the same engine | ✓ Built & verified |
| **DEC-matchup-method** — who-guards-whom uses optimal defender-assignment (Franks/Bornn 2015): weighted man/ball/hoop anchor + Hungarian assignment + HMM/temporal smoothing | Principled, validated method for stable assignment over time | ✓ Built & validated |
| **DEC-anthro-join-not-measure** — anthropometrics are JOINED from Combine data by identity, NOT measured from video; pose is used for angles only; foot-length dropped | 2D foreshortening makes video length-measurement unreliable; Combine data is authoritative | ✓ Locked (spec) |
| **DEC-possession-by-control** — possession is inferred from actual ball control (~4 ft), attacking hoop = hoop nearest the controlled ball's median position | Replaces nearest-player heuristic that inverted geometry on ~1-in-10 possessions | ✓ Built & verified |

---
*Last updated: 2026-06-06 after initial ingest bootstrap (gsd-roadmapper)*
