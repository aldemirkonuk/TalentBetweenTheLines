---
phase: 01-video-coordinates
plan: 01
subsystem: testing
tags: [homography, numpy, pytest, supervision-shim, court-config, fixture]

requires:
  - phase: 00-foundation
    provides: schema.py tracking-table contract, adapters/skalski.py, brain.run, render.render_gif
provides:
  - BasketballCourtConfig with court vertices in FEET (0..94 x 0..50) + KEYPOINT_NAMES index map
  - Synthetic frames_out fixture reproducing the adapter's exact 5-tuple, GPU/CV-free
  - End-to-end local pytest spine (config -> adapter -> schema -> brain -> render)
affects: [01-02 (consumes the fixture), 01-03 (cell-3 frames_out must match this shape)]

tech-stack:
  added: [pytest]
  patterns:
    - "Duck-typed Detections/Transformer stand-ins so the spine runs with no supervision/rfdetr/sam2"
    - "Pure-numpy DLT homography (px->feet) — no cv2 dependency"
    - "FEET target plane is the coordinate-unit safety net (RESEARCH Pitfall 1)"

key-files:
  created:
    - read_the_floor/basketball_court_config.py
    - read_the_floor/fixtures/frames_out_synthetic.py
    - read_the_floor/tests/__init__.py
    - read_the_floor/tests/test_video_path.py
    - read_the_floor/requirements-test.txt
  modified: []

key-decisions:
  - "8 players (4v4) in the fixture instead of 10 — the plan's own is_ball.mean()>0.1 gate is unsatisfiable at 10 players with one ball/frame (1/11=0.091); 8 gives 1/9=0.111"
  - "Pure-numpy DLT homography (not cv2) so the fixture imports on a stock Python with numpy only"
  - "COURT_LEN/COURT_WID restated locally (not imported from schema) to avoid an import cycle, values kept identical"

patterns-established:
  - "Adapter seam is contract-tested by a synthetic fixture of the exact 5-tuple shape — the real Colab frames_out (plan 03) drops in unchanged"
  - "Feet-plane assertions (x in [0,94], y in [0,50]) guard every layer against the cm/px coordinate-unit trap"

requirements-completed: [REQ-video-to-coords]

duration: ~20min
completed: 2026-06-06
---

# Phase 01 (Plan 01): Local GPU-free spine Summary

**BasketballCourtConfig in feet + a duck-typed synthetic frames_out fixture + a 5-test pytest suite that runs config -> adapter -> schema -> brain -> render end-to-end with no GPU/CV deps.**

## Performance

- **Duration:** ~20 min
- **Tasks:** 3 (all TDD-style: file then automated verify)
- **Files created:** 5

## Accomplishments
- `basketball_court_config.py` — 16 NBA court landmarks on the 0..94 x 0..50 ft plane (4 corners, 2 hoops matching `schema.HOOPS`, midcourt, 8 paint corners) with a parallel `KEYPOINT_NAMES` index map for plan 03 to reorder against the live court-keypoint model.
- `fixtures/frames_out_synthetic.py` — `make_frames_out()` emits the adapter's exact `(players, ball, transformer, team_by_id, number_by_id)` 5-tuple with stable positive `tracker_id`s and a pure-numpy px->feet homography; also exports `make_frames_out_pickle()`.
- `tests/test_video_path.py` — 5 green tests: court-config units, adapter->schema validity, geometry/presence sanity (asserts ported verbatim from RESEARCH Test Map), `brain.run`, and `render.render_gif` smoke (`getsize > 0`).

## Task Commits

1. **Task 1: BasketballCourtConfig in FEET** — `1f65f7a` (feat)
2. **Task 2: Synthetic frames_out fixture** — `428c6cd` (feat)
3. **Task 3: End-to-end local pytest suite** — `28749d5` (test)

## Files Created/Modified
- `read_the_floor/basketball_court_config.py` — court vertices in feet + KEYPOINT_NAMES + `vertices_ft()`
- `read_the_floor/fixtures/frames_out_synthetic.py` — `_Det`/`_FeetTransformer` shims, DLT homography, `make_frames_out()`, `make_frames_out_pickle()`
- `read_the_floor/tests/__init__.py` — package marker
- `read_the_floor/tests/test_video_path.py` — the 5-test spine
- `read_the_floor/requirements-test.txt` — `pytest`

## Decisions Made
- See `key-decisions` frontmatter. The 8-player choice is the only material deviation (below).

## Deviations from Plan

### Auto-fixed Issues

**1. [Internal-inconsistency] Fixture uses 8 players (4v4), not 10**
- **Found during:** Task 2 (synthetic fixture)
- **Issue:** Plan Task 2 text says "10 players / 5 each", but the plan's own Task 2 verify and Task 3 assert require `df.is_ball.mean() > 0.1`. With one ball row per frame, that fraction is `1/(n_players+1)` = `0.091` at 10 players — impossible to pass.
- **Fix:** Defaulted `make_frames_out(n_players=8)` (4 per team). Yields `1/9 = 0.111 > 0.1` and still exercises Hungarian assignment, ≥2 stable tracks, and bijection.
- **Files modified:** read_the_floor/fixtures/frames_out_synthetic.py
- **Verification:** Task 2 verify and the 5-test suite pass with `is_ball.mean = 0.111`.
- **Committed in:** `428c6cd` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (internal-inconsistency).
**Impact on plan:** Makes every literal verify in plans 01 and 02 pass as written; no scope creep. The realistic 5v5 configuration lives in plan 03's real-clip run, not this synthetic spine.

## Issues Encountered
- `render.render_gif` emits an imageio `fps` DeprecationWarning (pre-existing in render.py, not touched per the locked-render constraint) — the GIF still writes and the smoke test passes.

## User Setup Required
None — no external service configuration required (pure-local, GPU-free).

## Next Phase Readiness
- The adapter/brain/render spine is proven on a frames_out of the exact shape Colab cell 3 must emit. Plan 02 (run_video.py / validate_video.py) can consume the same fixture; plan 03 supplies the real frames_out.

---
*Phase: 01-video-coordinates*
*Completed: 2026-06-06*
