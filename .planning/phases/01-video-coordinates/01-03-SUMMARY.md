---
phase: 01-video-coordinates
plan: 03
subsystem: vision-pipeline
tags: [colab, rf-detr, sam2, siglip, smolvlm2, homography, jersey-ocr, frames_out]

requires:
  - phase: 01-video-coordinates (plan 01)
    provides: skalski adapter contract, BasketballCourtConfig (feet), schema.py
  - phase: 01-video-coordinates (plan 02)
    provides: run_video.py + validate_video.py (consume the pickled frames_out)
provides:
  - colab_read_the_floor.ipynb — full Skalski/SAM2 pipeline producing frames_out
affects: [phase verification — runs after the GPU render lands]

tech-stack:
  added:
    - "segment-anything-2-real-time (Gy920 fork) — SAM2 camera predictor"
    - "inference-gpu — local GPU model inference (get_model)"
    - "sports@feat/basketball — CourtConfiguration(NBA, FEET), TeamClassifier, ViewTransformer, ConsecutiveValueTracker"
  patterns:
    - "Teams classified once on the first SAM2 prompt frame, frozen, keyed by tracker_id"
    - "Jersey numbers matched to tracks by mask-IoS (>0.9), voted with ConsecutiveValueTracker(3), filled into a shared number_by_id dict"
    - "Per-frame homography reuses the last good ViewTransformer when keypoints are sparse"

key-files:
  created: []
  modified:
    - read_the_floor/colab_read_the_floor.ipynb

key-decisions:
  - "DEVIATION: homography target is the sports CourtConfiguration(NBA, FEET) 33-vertex array, NOT our basketball_court_config.vertices_ft() (16 pts). The live keypoint model (basketball-court-detection-2/14) emits 33 points; our 16-pt file cannot index-align to it. The sports config is already in FEET (0..94 x 0..50), so the schema contract is preserved. Our file is kept as our own reference court."
  - "DEVIATION: local get_model + inference-gpu (ONNXRUNTIME CUDA provider), NOT the hosted InferenceHTTPClient. The earlier pycuda error came from plain `inference`; Skalski's `inference-gpu` is the correct, faster fix and is exactly what the reference uses."
  - "Tracking is SAM2 (Skalski-faithful), not ByteTrack — per explicit instruction to mirror Skalski exactly."
  - "Jersey OCR is gated behind RUN_OCR (default True) so it can be disabled on low-VRAM (T4) runs."

requirements-completed: []   # REQ-video-to-coords closes when Task 3 (GPU render) lands

duration: ~code-complete
completed: pending-gpu-render
---

# Phase 01 (Plan 03): Colab video pipeline (Skalski / SAM2) — Summary

**The Colab notebook is a faithful port of Roboflow's open-source basketball pipeline
(RF-DETR -> SAM2 real-time -> SigLIP/UMAP/K-means teams -> SmolVLM2 jersey OCR ->
court-keypoint homography to FEET), emitting our `frames_out` contract straight into the
UNCHANGED skalski adapter -> schema -> brain -> render path.**

## Status

- **Task 1 (human checkpoint — clip/GPU/key/keypoint order):** satisfied operationally —
  clip on Drive, GPU runtime, working `ROBOFLOW_API_KEY`, and the keypoint model confirmed
  emitting **33 points (~12 high-confidence on the test clip)**. This is what forced the
  33-vertex sports config decision below.
- **Task 2 (auto — fill cell 3 + jersey OCR + inline asserts):** **DONE & VERIFIED.**
- **Task 3 (human-verify — run on real clip, render GIFs, SC4 sanity, persist artifacts):**
  **PENDING** — GPU-gated; runs in the user's Colab session.

## What landed (Task 2)

- Full SAM2 pipeline cells: install (`Gy920/segment-anything-2-real-time` + checkpoints),
  `inference-gpu` stack, `sports@feat/basketball`, model loads, `SAM2Tracker`, team fit.
- Cell 9 produces `frames_out` = `(players, ball, transformer, team_by_id, number_by_id)`:
  SAM2 stable ids, low-confidence ball re-detection (0.2), per-frame feet homography with
  last-good reuse, frozen teams, and **jersey OCR** (mask-IoS match + 3-vote validator).
- Cell 9b renders a **Skalski-identical court map** (`draw_court` + `draw_points_on_court`)
  for a direct side-by-side comparison to Skalski's output, before our brain layer.
- Cell 10 adds the plan's inline asserts (FEET trap `between(0,94)`, rows/frame, ball
  presence, >=2 stable tracks) right after `schema.validate(df)`.

## Verification (all green, agent-side)

- Notebook structure check: `frames_out`, feet target, `tracker_id`, `TeamClassifier`,
  `ViewTransformer`, `between(0,94)` assert, `skalski.frame_to_rows`, `render.render_gif` — **OK**.
- No hardcoded key literal (grep == 0); secret read via `userdata.get`/`os.environ` (== 2).
- `skalski.py`, `schema.py`, `brain.py`, `render.py` — **UNCHANGED** (`git diff --quiet` exit 0).

## Deviations from Plan

1. **Feet target = sports 33-pt `CourtConfiguration(NBA, FEET)`** instead of our 16-pt
   `vertices_ft()` — required by the live model's 33-keypoint output; units unchanged (feet).
2. **`inference-gpu` + `get_model`** instead of hosted `InferenceHTTPClient` — the correct
   fix for the pycuda error and exactly Skalski's approach.
3. Added a **Skalski court-map comparison GIF** (cell 9b) beyond the plan, to validate the
   pipeline reproduces Skalski's coordinate mapping before the brain layer.

## Pending (Task 3 — to close REQ-video-to-coords)

Run cells top to bottom on the Colab GPU. Then locally:
`python3 validate_video.py --frames-out frames_out.pkl` (expect SC4 PASS) and
`python3 run_video.py --frames-out frames_out.pkl --out prototypes/video_matchup.gif
--stills 5 --frames-dir read_the_floor/frames`. Persist `prototypes/video_matchup.gif`
and `read_the_floor/frames/still_*.png`, then phase verification can run.

---
*Phase: 01-video-coordinates*
*Status: code-complete; GPU render pending*
