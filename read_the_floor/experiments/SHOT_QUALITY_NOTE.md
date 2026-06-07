# Shot-Quality model — experiment log

## ✅ RESOLVED — see `../value.py` + `../shot_model.json`
The lesson: **don't extract shot location from movement tracking.** The NBA shot logs already
publish `SHOT_DIST` and `CLOSE_DEF_DIST` per shot. Trained on those (128k shots, 2014-15):
**leave-game-out AUC 0.63, well calibrated**, defender sign correct, expected points sane
(open 3 > open mid > tight 2). Working model in `value.py`; rebuild with `build_shot_model.py`.
Movement tracking is for spacing/matchups — not for shot location.

---

## Original failure (kept as the lesson)
**The quick labeling from movement tracking was not reliable enough to ship.**
Recording this honestly so we don't repeat the mistake or trust a bad artifact.

## What we tried
- Downloaded 2015-16 play-by-play, merged shot events to SportVU events by `(GAME_ID, EVENTNUM=eventId)`.
- Labeled each shot from tracking: shooter position at "release" (ball-height apex heuristic),
  → shot distance, nearest-defender distance, is-3.
- Trained logreg + GBM, leave-one-game-out CV across 7 games (1,023 shots).

## Result (honest)
- **Leave-game-out AUC ≈ 0.54** (≈ chance). Brier ≈ 0.25.
- Defender-distance coefficient came out **backwards** (confounded with distance).
- **Root cause:** computed shot distance correlates only **r = 0.16** with the play-by-play
  distance. Fit was `calc ≈ 0.18·pbp + 14.6` — i.e. distances collapsed toward ~15–20 ft
  regardless of the real shot. The release-frame heuristic grabs the wrong moment, so the
  spatial feature is mostly noise.

## Why
The SportVU event ↔ play-by-play ↔ moment alignment needs to be done properly (as the
Hugging Face loader does), and the shot frame must be detected from the **ball trajectory**
(ball crossing toward/over the rim), not from "ball-height apex in the last 50 frames."

## Correct fix path (next attempt)
1. Use the HF dataset's merged PBP+tracking, or replicate its event alignment exactly.
2. Detect the release frame by ball trajectory: last frame the ball is in the shooter's hands
   before it travels monotonically toward the rim and reaches rim height near the hoop xy.
3. Validate features FIRST: shot-distance vs PBP distance should hit r > 0.9 / median err < 2 ft
   **before** training. Only train once the feature is trustworthy.
4. Then features: distance, defender distance + angle, catch-and-shoot vs off-dribble, shot clock.

Code kept here: `build_dataset.py`, `train_shotmodel.py`, `label_shots.py` — experimental.
