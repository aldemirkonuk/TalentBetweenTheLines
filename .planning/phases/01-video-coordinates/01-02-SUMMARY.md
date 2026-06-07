---
phase: 01-video-coordinates
plan: 02
subsystem: testing
tags: [cli, runner, validator, robustness, sportvu-baseline, gif, stills]

requires:
  - phase: 01-video-coordinates (plan 01)
    provides: synthetic frames_out fixture, skalski adapter spine, BasketballCourtConfig
provides:
  - run_video.py — frames_out -> X-ray GIF + N evenly-spaced overlay stills (GPU-free)
  - validate_video.py — robustness report (validate.py metrics + SC4 sanity verdicts)
affects: [01-03 (Colab cell 3 pickles a frames_out that these two scripts consume)]

tech-stack:
  added: []
  patterns:
    - "Runner/validator consume a pickled frames_out so the GPU step and the read step are decoupled"
    - "Robustness recomputed from PUBLIC symbols only (brain.POSSESSION_R) — no private-helper reach-in"

key-files:
  created:
    - read_the_floor/run_video.py
    - read_the_floor/validate_video.py
  modified: []

key-decisions:
  - "Control share recomputed inline from brain.POSSESSION_R + schema columns (plan-checker warning fix) instead of calling brain._control_frames"
  - "validate_video is report-only (always exit 0); SC4 verdicts are printed PASS/WARN text, not a gate"
  - "frames_out is delivered via pickle; both scripts warn that only self-generated pickles should be loaded (untrusted-pickle threat)"

patterns-established:
  - "Track-B (video) scripts mirror Track-A (SportVU) run_sportvu.py / validate.py 1:1 so the brain output is comparable across data sources"

requirements-completed: [REQ-video-to-coords]

duration: ~15min
completed: 2026-06-06
---

# Phase 01 (Plan 02): Video runner + validator Summary

**run_video.py turns a saved frames_out into the X-ray GIF + stills, and validate_video.py reports the SportVU-comparable robustness metrics + SC4 sanity verdicts — both GPU-free, on the synthetic fixture.**

## Performance

- **Duration:** ~15 min
- **Tasks:** 2
- **Files created:** 2

## Accomplishments
- `run_video.py` — loads a pickled frames_out, runs the unchanged `skalski -> schema -> brain -> render` spine, prints the `run_sportvu`-style line (`frames {n} | offense {team} | peak Beaten Index {x}`), writes the GIF and N evenly-spaced PNG stills. On the 24-frame fixture: offense=100, peak Beaten Index=37, GIF + 3 stills.
- `validate_video.py` — prints `validate.py`'s metrics (valid_rate, swap_rate, beaten_mean/std, contain_rate) plus an `SC4` line with PASS/WARN verdicts. On the 40-frame fixture: valid_rate=1.0, swap_rate=0.0, contain_rate=1.0, and all SC4 PASS (hoop_dist_median=16.8 ft vs SportVU's ~18, control_share=1.00, beaten_std=6.3).

## Task Commits

1. **Task 1: run_video.py** — `caa119c` (feat)
2. **Task 2: validate_video.py** — `97e9047` (feat)

## Files Created/Modified
- `read_the_floor/run_video.py` — CLI runner: frames_out pickle -> GIF + stills
- `read_the_floor/validate_video.py` — CLI robustness report + SC4 sanity verdicts

## Decisions Made
- See `key-decisions` frontmatter.

## Deviations from Plan
None — plan executed as written. The plan-checker's prior substantive warning (avoid the private `brain._control_frames`) was honored by design: control share is recomputed inline from `brain.POSSESSION_R` and schema columns, and no private helper is referenced.

## Issues Encountered
None. (The `render.render_gif` imageio `fps` DeprecationWarning is pre-existing in `render.py` and does not affect output.)

## User Setup Required
None — pure-local, GPU-free.

## Next Phase Readiness
- Both scripts consume a pickled frames_out of the exact shape plan 03's Colab cell 3 must emit. Once a real clip produces `frames_out.pkl`, `python run_video.py --frames-out frames_out.pkl` and `python validate_video.py --frames-out frames_out.pkl` work with zero code changes.
- **Wave 3 (plan 03) is GPU-gated and intentionally NOT executed here** (autonomous: false — needs a real clip, Colab GPU, and a Roboflow API key). Phase verification/completion is deliberately deferred until wave 3 runs.

---
*Phase: 01-video-coordinates*
*Completed: 2026-06-06*
