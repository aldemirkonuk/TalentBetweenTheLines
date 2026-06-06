# Requirements (PRD intel)

No PRD-type documents were present in this ingest set. Requirements below are derived
from the SPEC feature sets (READ_THE_FLOOR.md "LOCKED features", v2 additions, FOCUS
FIVE; BODY_AND_ANGLES.md metrics) so downstream roadmapping has a requirement-shaped
view. Build status is cross-referenced from STATE.md (DOC) — SPEC defines the
requirement, DOC reports its current implementation state.

No competing acceptance variants were found: the two SPECs cover disjoint scopes
(floor-value/reads vs. biomechanics) and STATE.md agrees with both on status.

---

## Tier 0 — Built & validated (per STATE.md)

### REQ-tracking-schema
- Source: READ_THE_FLOOR.md, STATE.md
- Description: A single tracking-table schema every source adapts into.
- Acceptance: `schema.py` contract used by SportVU adapter; partial rosters handled.
- Status: built & verified.

### REQ-matchup-engine
- Source: READ_THE_FLOOR.md (FOCUS FIVE #1, v2 "The Matchup")
- Description: Assign each defender to his man live (who-guards-whom).
- Acceptance: assignment bijection ~0.997, swap ~0.004; Hungarian + temporal smoothing.
- Status: built & validated.

### REQ-beaten-index
- Source: READ_THE_FLOOR.md (FOCUS FIVE #1, v2 "Beaten Likelihood")
- Description: Per-matchup 0–100 likelihood the defender is about to get beaten
  (separation spike + off the man-hoop line).
- Acceptance: 0–100 range, non-degenerate (mean ~55, std ~26); geometry sane after
  possession/hoop fix.
- Status: built; VALIDATION.md flags it needs PBP-anchored possession before it
  ships as a trustworthy metric on every possession (transition/inbound edges).

### REQ-possession-hoop-detection
- Source: STATE.md, VALIDATION.md
- Description: Detect possession and attacking hoop robustly.
- Acceptance: control-based inference; possession-52 contain_rate 0.09 → 0.99,
  game aggregate 0.80 → 0.89.
- Status: built & verified (inversion fixed).

### REQ-shot-quality-value
- Source: READ_THE_FLOOR.md ("Shot Quality"), STATE.md
- Description: Grade every shot attempt in expected points ("shoot now" value model).
- Acceptance: leave-game-out AUC 0.63, calibrated; open-3 > open-mid; wired into the
  read and the colored floor render.
- Status: built & verified.

### REQ-anthro-join
- Source: BODY_AND_ANGLES.md, STATE.md
- Description: Join Combine anthropometrics to players by identity.
- Acceptance: name-match join + report, verified on real rosters (`anthro.py`).
- Status: built & verified.

### REQ-top-down-render
- Source: READ_THE_FLOOR.md, STATE.md
- Description: Render the read as a top-down / broadcast X-ray overlay.
- Acceptance: locked palette, orientation-aware (mirrors when attacking left hoop);
  local CPU-only runner `.7z` → GIF.
- Status: built & verified.

## Tier 1 — Written but not proven end-to-end (per STATE.md)

### REQ-video-to-coords
- Source: READ_THE_FLOOR.md (pipeline), STATE.md, SETUP.md (Track B)
- Description: Skalski video → coordinates adapter feeding the shared schema.
- Acceptance: a real clip runs end-to-end through cell 3 (RF-DETR + SAM2 + team +
  homography) into `frames_out` → brain → render.
- Status: adapter written; Colab cell 3 is a fill-in stub; no real clip run yet.
- Note: STATE.md lists this as the #1 next step.

## Tier 2 — Spec-only (designed, not built; per STATE.md)

### REQ-epv-surface
- Source: READ_THE_FLOOR.md (FOCUS FIVE #2)
- Description: Full EPV surface (shot prob, pass-success, turnover prob as functions
  of spatial config), beyond "shoot now."
- Acceptance: approximate EPV (Cervone/Fernández) on labeled possessions; heatmap +
  running counter.
- Status: spec-only.

### REQ-points-left / REQ-decision-grade
- Source: READ_THE_FLOOR.md (FOCUS FIVE #2, v2)
- Description: Running tally of expected points lost (EV(best) − EV(chosen)); grade
  actual decision vs optimal read.
- Acceptance: per-decision delta cumulated; Decision Grade output.
- Status: spec-only. STATE.md lists Points Left as the #2 next step (SportVU path).

### REQ-set-perfectionist
- Source: READ_THE_FLOOR.md (FOCUS FIVE #3, v2)
- Description: Recognize the set being run and grade execution vs ideal template.
- Acceptance: HoopTransformer-style trajectory encoder → classify + grade.
- Status: spec-only.

### REQ-tell-snitch
- Source: READ_THE_FLOOR.md (FOCUS FIVE #4, v2)
- Description: Mine telegraphed tendencies (The Tell) → auto one-page scouting
  report (The Snitch).
- Acceptance: pre-decision micro-feature mining + sequence model → report.
- Status: spec-only; data-volume bottleneck for current players.

### REQ-moneyball-vision
- Source: READ_THE_FLOOR.md (FOCUS FIVE #5, v2)
- Description: Court-IQ scout — Decision Grade across a prospect's film →
  Court-Vision percentile independent of scoring.
- Acceptance: vision score + clip reel; needs cross-level domain adaptation.
- Status: spec-only; transfer is the named risk.

### REQ-body-angles-layer
- Source: BODY_AND_ANGLES.md, READ_THE_FLOOR.md, STATE.md
- Description: Biomechanics layer — pose-derived angles (Square-Up Score, Stance
  Read) + Combine-joined anthropometrics → scoring/finishing/passing/defense metrics.
- Acceptance: new schema columns (`foot_angle`, `hip_angle`, `shoulder_angle`,
  `knee_bend`) from a pose adapter; brain modules `square_up.py`, `stance.py`,
  `anthro_corr.py`; `players_anthro.csv` join.
- Status: spec-only (anthro join itself is built; the angle/pose modules are not).

### REQ-reads-suite (offense/defense reads)
- Source: READ_THE_FLOOR.md ("LOCKED features")
- Description: The Read, Open Man, Gravity, Skip, Extra Pass, Hot Zones, Spacing
  Grade, The Gap, Help Is Late, Mismatch Finder, Coverage Read, Rim Pressure,
  Transition Math.
- Acceptance: each priced by reward-vs-risk and surfaced on the overlay.
- Status: spec-only (most depend on REQ-epv-surface). Recorded as a grouped backlog.
