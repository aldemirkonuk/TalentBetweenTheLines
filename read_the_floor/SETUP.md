# SETUP — full step by step

Two tracks. **Track A** (local, no GPU) gets the Matchup Engine running in ~10 minutes on the
open SportVU data — do this first to see the brain work. **Track B** (Colab, GPU) runs
Skalski's vision pipeline so you can analyze *any video clip*.

---

## Track A — Local quick win (no GPU, ~10 min)

**Goal:** render a Matchup Engine clip from the 2015-16 tracking data.

### A1. Get Python 3.10+
Check: `python3 --version`. If missing, install from python.org or `brew install python`.

### A2. Get the code
It lives in `Portfolio/Talent Between the Lines/read_the_floor/`. In a terminal:
```bash
cd "/path/to/Portfolio/Talent Between the Lines/read_the_floor"
```

### A3. Create an environment and install
```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-local.txt
```

### A4. Run it on a downloaded game
The subset is already in `Talent Between the Lines/data/tracking/`. Pick any `.7z`:
```bash
python run_sportvu.py ../data/tracking/11.07.2015.CHA.at.SAS.7z --auto
```
`--auto` picks a clean half-court possession. Output: `matchup_engine.gif`.
You'll see the offense team id, frame count, and the peak Beaten Index printed.

### A5. (optional) Pick a specific possession
```bash
python run_sportvu.py ../data/tracking/11.07.2015.CHA.at.SAS.7z --event 217 --out cha_sas.gif
```

✅ If the GIF renders, the whole brain → table → render path works on your machine.

---

## Track B — Video pipeline on Colab (GPU)

**Goal:** turn a real video clip into coordinates with Skalski's pipeline, then run our brain.

### B1. Get a clip
A short single-possession `.mp4` (5–15 s). Trim it however you like (QuickTime, ffmpeg).
Keep the camera angle as stable as possible for the first try.

### B2. Open the notebook
Upload `read_the_floor/colab_read_the_floor.ipynb` to https://colab.research.google.com
(File → Upload notebook). Then **Runtime → Change runtime type → T4 GPU → Save**.

### B3. Make our modules available in Colab
Easiest: zip the `read_the_floor` folder, upload it in the Colab file panel, and:
```python
!unzip -q read_the_floor.zip -d /content/
```
(Or `git clone` your portfolio repo if it's pushed, then `%cd` into `read_the_floor`.)

### B4. Run cell 1 — install the stack
RF-DETR, supervision, SAM2, transformers, umap, scikit-learn, and `roboflow/sports`.

### B5. Run cell 3 — Skalski's models  ← the one part you fill in
Open his notebook **“basketball-ai-how-to-detect-track-and-identify-basketball-players”**
(linked in his video) and copy the model cells. Use these three Roboflow Universe datasets:
- Player detection: `roboflow-jvuqo/basketball-player-detection-3-ycjdo`
- Court keypoints:  `roboflow-jvuqo/basketball-court-detection-2`
- Jersey OCR:       `roboflow-jvuqo/basketball-jersey-numbers-ocr`

The goal of this cell: for **each frame**, produce four objects —
`players` (Detections+tracker_id), `ball` (Detections), `transformer` (ViewTransformer),
`team_by_id` ({id:0/1}). Collect them into a list `frames_out`.

### B6. Run cells 4–5 — adapt + brain + render
Our adapter turns `frames_out` into the tracking table; the brain runs; the GIF displays.
Nothing to edit here.

✅ When the overlay renders from your clip's coordinates, the two halves are connected.

---

## Data you need

| Data | What for | Where |
|------|----------|-------|
| SportVU 2015-16 (have) | train/validate the brain | `Talent Between the Lines/data/tracking/` (+ 636 games on GitHub) |
| Draft Combine anthro | body layer (wingspan, reach, hand size) | hoopR `nba_draftcombineplayeranthro`, or Kaggle |
| Video clips | apply on current footage | your own trims |

Fetch more SportVU games: the manifest + source URLs are in `data/tracking/MANIFEST.txt`.

---

## Troubleshooting
- **`py7zr` error** → `pip install py7zr` (Track A only).
- **Colab “no GPU”** → Runtime → Change runtime type → GPU. RF-DETR/SAM2 need it.
- **Discs off the feet** → use the SAM2 *mask* bottom, not the box bottom, for the ground point.
- **Jittery tracks** → `skalski.build_table(..., smooth=True)`; upgrade to Kalman later.
- **Wrong team on offense** → the brain infers it from who's nearest the ball; check `team_by_id`.
