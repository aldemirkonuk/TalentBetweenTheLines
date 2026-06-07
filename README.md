# Talent Between the Lines

> Recognizing talent the box score can't see — the read, the gap, the decision,
> rendered as light on the floor.

The flagship: a computer-vision + ML system that watches basketball and surfaces the
**value of the floor** — who guards whom, where the gap is, what the best read is worth,
and what it risks. Built on a forked Roboflow/Skalski vision pipeline plus an original
value-and-risk brain trained on open tracking data.

## What's in here
- **`READ_THE_FLOOR.md`** — the project spec: features, focus five, feasibility.
- **`BODY_AND_ANGLES.md`** — the biomechanics edition (feet angle, wingspan/hand via Combine).
- **`STATE.md`** — current status: what's built/working vs spec-only. Read this first.
- **`read_the_floor/`** — the system code. Start with `read_the_floor/SETUP.md`.
  - `schema.py` (tracking-table interface) · `brain.py` (Matchup Engine + value) ·
    `value.py` + `shot_model.json` (Shot Quality) · `render.py` · `adapters/` (SportVU + Skalski) ·
    `anthro.py` (Combine join) · `validate.py` + `VALIDATION.md` · `run_sportvu.py` ·
    `colab_read_the_floor.ipynb` · `experiments/`
- **`data/tracking/`** — SportVU 2015-16 subset (top-10 vs top-10 games) + manifest.
- **`prototypes/`** — `matchup_engine.gif` (the working top-down read).
- **`frames/`** — broadcast X-ray stills (`ss1.png`, `ss1_xray.png`).

## Quick start
```bash
cd read_the_floor
pip install -r requirements-local.txt
python run_sportvu.py ../data/tracking/11.07.2015.CHA.at.SAS.7z --auto
```

The name: a portfolio about reading the floor and finding the talent **between the lines** —
the court lines, and the spaces the eye walks past.
