# Context (DOC intel)

Running notes from the DOC sources (STATE.md, VALIDATION.md, SETUP.md), keyed by
topic and attributed verbatim-in-substance to source. STATE.md is the declared live
build-status source of truth.

---

## Build status (source: STATE.md)
- TL;DR: the brain works end-to-end on open tracking data — identifies who guards
  whom, prices the floor in expected points, renders the read. NOT yet running on
  video; only on SportVU 2015-16 coordinates. Value model is "shoot now," not full EPV.
- Built & verified: schema, SportVU adapter, Matchup Engine (bijection 0.997, swap
  0.004), Beaten Index (0–100), possession/hoop (inversion 0.09→0.99 on the bad
  possession), Shot-Quality model (AUC 0.63, calibrated), value wired into the read,
  Combine anthro join, top-down render, local runner, robustness checks, independent
  review (high-severity bugs fixed).
- Written but not proven: video→coords (Skalski) — adapter targets the schema, Colab
  cell 3 is a fill-in stub, no real clip run.
- Spec-only: full EPV surface, Points Left / Decision Grade, Set Perfectionist,
  Tell→Snitch, Moneyball for Vision, Body & Angles layer.
- Recommended next order: (1) prove video→coords on one clip, (2) Points Left on the
  SportVU path, (3) grow value into the full EPV surface.

## Validation numbers (source: VALIDATION.md)
- CHA @ SAS, 10 possessions: valid_rate 0.996, swap_rate 0.004, beaten_mean 55.4,
  beaten_std 26.2, contain_rate 0.80.
- Assignment is robust: near-perfect bijection + very low swap; Hungarian cost +
  sticky temporal smoothing works.
- Possession/hoop inversion FIXED: was ~1-in-10 misfires (possession 52 contain_rate
  0.09); fix = ball-control-based possession + hoop nearest controlled-ball median;
  result possession-52 0.09→0.99, aggregate 0.80→0.89, assignment stability unchanged.
- `value` now uses the nearest defender as the contest (not just the assigned man).
- Independent review fixes: stable-ID smoothing now votes on `track_id` (not
  positional indices); partial rosters via rectangular Hungarian; graceful empties;
  Skalski adapter None tracker_ids get unique negative ids; orientation-aware render
  mirrors for left-hoop possessions. Post-fix path unchanged (valid 0.995, swap 0.004,
  contain 0.80).
- Honest status: core matchup assignment validated and hardened; Beaten Index correct
  on standard half-court possessions but needs PBP-anchored possession before shipping.

## Runbook (source: SETUP.md)
- Track A (local, no GPU, ~10 min): venv + `requirements-local.txt`, then
  `python run_sportvu.py ../data/tracking/11.07.2015.CHA.at.SAS.7z --auto` →
  `matchup_engine.gif`. `--auto` picks a clean half-court possession.
- Track B (Colab GPU): upload `colab_read_the_floor.ipynb`, T4 GPU, install stack
  (RF-DETR, supervision, SAM2, transformers, umap, scikit-learn, roboflow/sports),
  fill cell 3 with Skalski's model cells using the three Roboflow Universe datasets,
  produce `frames_out` per frame (players, ball, transformer, team_by_id), then cells
  4–5 adapt + run brain + render.
- Data needed: SportVU 2015-16 (have), Draft Combine anthro (hoopR
  `nba_draftcombineplayeranthro` or Kaggle), own video trims. More SportVU games via
  `data/tracking/MANIFEST.txt`.
- Troubleshooting notes: py7zr install, Colab GPU runtime, use SAM2 mask bottom (not
  box bottom) for ground point, `smooth=True` for jittery tracks, team inferred from
  nearest-to-ball.

## Cross-reference note
- READ_THE_FLOOR.md (SPEC) and STATE.md (DOC) cite each other (a documentation
  back-reference, not a dependency loop). Precedence SPEC > DOC resolves any tension
  deterministically: SPEC defines intent, STATE.md reports current build reality.
- STATE.md, BODY_AND_ANGLES.md, READ_THE_FLOOR.md, and SETUP.md all reference code
  files (`schema.py`, `brain.py`, `value.py`, etc.) and data files outside the ingest
  set — these are out-of-scope for synthesis and were not traversed as doc edges.
