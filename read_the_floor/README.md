# Read the Floor — system

CV + ML system that renders the **value of the floor** on basketball footage.
Skalski's vision pipeline extracts coordinates; our **brain** reads the floor and prices the risk.

## The one interface that makes it work

Every source is converted into ONE shared **tracking table** (`schema.py`).
The brain only ever reads this table, so it doesn't care where coordinates came from:

```
frame | time | team | track_id | identity | x | y | is_ball     (court feet, 94 x 50)
```

```
SportVU JSON  ─┐
                ├─►  tracking table  ─►  brain (Matchup / Value / Risk)  ─►  render
Skalski video ─┘        (schema.py)        (brain.py)                       (render.py)
```

## Files
- `schema.py` — the interface contract (tracking table).
- `brain.py` — Matchup Engine: who-guards-whom + Beaten Index + per-read **expected-points value**.
- `value.py` + `shot_model.json` — Shot-Quality model (P(make) → expected points). AUC 0.63, calibrated.
- `render.py` — top-down render in the locked palette (floor colored by value).
- `adapters/sportvu.py` — SportVU 2015-16 JSON → table  (training/validation data).
- `adapters/skalski.py` — Skalski pipeline output → table  (any video → table).
- `anthro.py` — Combine anthropometrics → joined to player identities (body layer).
- `validate.py` (+ `VALIDATION.md`) — robustness checks for the Matchup Engine.
- `run_sportvu.py` (+ `requirements-local.txt`) — local CPU entry point → top-down GIF.
- `colab_read_the_floor.ipynb` — run the video path on Colab (Skalski cell is a fill-in stub).
- `experiments/` — Shot-Quality training + the parked tracking-extraction attempt (lesson kept).

## Why two adapters
- **SportVU** = clean, full-court, has outcomes → **train & validate** the brain here.
- **Skalski** = any footage (incl. 2026), noisier, camera-limited → **apply** the brain here.
  Feet = bottom of each SAM2 mask, projected by the court homography. No separate feet model.

## Proven so far
`adapters/sportvu.py → brain.run → render` runs end-to-end on real possessions
(`prototypes/matchup_engine.gif`): who-guards-whom, Beaten Index, and per-read expected
points, with the floor colored by value. Validated across possessions (assignment bijection
0.997, swap 0.004); possession/hoop inversion fixed (`VALIDATION.md`). Shot-Quality model is
trained + calibrated (`value.py`). The Skalski adapter targets the same schema, so the brain
runs unchanged on extracted video — but that video→coords path is **not yet proven** (Colab
Skalski cell is still a stub; only the SportVU path is end-to-end).

## Run on Colab (GPU)
Open `colab_read_the_floor.ipynb`, Runtime → GPU, run top to bottom. It installs the
open-source stack, runs Skalski's detect/track/team/number/homography cells on a clip,
adapts the output to the table, runs the brain, and renders the overlay.

## Honest TODO
- Prove the **video → coords** path: fill the Colab Skalski cell, run RF-DETR + SAM2 + homography on a clip.
- Full **EPV surface** (pass / drive / turnover), not just "shoot now"; then **Points Left on the Floor**.
- PBP-anchored possession for the last rare edge cases.
- Per-frame homography on a moving broadcast camera; Kalman (not exponential) track smoothing.
- Upgrade defender assignment to the Franks/Bornn model (help & switches).
