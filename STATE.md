# STATE — Talent Between the Lines

Current status of the *Read the Floor* flagship. Single source of truth; updated as we build.
_Last updated: June 2026._

---

## TL;DR
The brain works end-to-end on open tracking data: it identifies who guards whom, prices the
floor in expected points, and renders the read. It is **not** yet running on video — only on
SportVU 2015-16 coordinates. The value model is "shoot now," not the full EPV surface.

---

## ✅ Built & verified
| Piece | File | Status / numbers |
|-------|------|------------------|
| Tracking-table interface | `read_the_floor/schema.py` | the one contract every source adapts into |
| SportVU adapter | `read_the_floor/adapters/sportvu.py` | JSON → table, partial rosters handled |
| Matchup Engine (who guards whom) | `read_the_floor/brain.py` | assignment bijection **0.997**, swap **0.004** |
| Beaten Index | `read_the_floor/brain.py` | 0–100; geometry sane after possession/hoop fix |
| Possession / attacking-hoop | `read_the_floor/brain.py` | control-based; inversion **0.09 → 0.99** on the bad possession |
| Shot-Quality value model | `read_the_floor/value.py`, `shot_model.json` | leave-game-out **AUC 0.63**, calibrated; open-3 > open-mid |
| Value wired into the read | `read_the_floor/brain.py`, `render.py` | each read shows expected points; floor colored by value |
| Combine anthro join | `read_the_floor/anthro.py` | name-match join + report, verified on real rosters |
| Top-down render | `read_the_floor/render.py` | locked palette; orientation-aware |
| Local runner | `read_the_floor/run_sportvu.py` | CPU-only, `.7z` → GIF |
| Robustness checks | `read_the_floor/validate.py`, `VALIDATION.md` | run across possessions/games |
| Independent review | — | subagent pass; high-severity bugs fixed |

Data: `data/tracking/` — SportVU 2015-16, top-10 vs top-10 subset (~55 games) + `MANIFEST.txt`.
Prototype: `prototypes/matchup_engine.gif`. Broadcast X-ray stills: `frames/`.

## 🟡 Written but NOT proven end-to-end
- **Video → coordinates (Skalski pipeline).** Adapter `read_the_floor/adapters/skalski.py`
  targets the shared schema; `colab_read_the_floor.ipynb` is scaffolded but **cell 3 (the
  RF-DETR + SAM2 + team + homography models) is a fill-in stub.** No real clip has been run.
  Repos to wire: `roboflow/rf-detr`, `roboflow/supervision`, `roboflow/sports`.

## 📋 Spec-only (designed, not built)
- Full **EPV surface** — pass / drive / turnover, not just "shoot now."
- **Points Left on the Floor** / **Decision Grade** (best available read − chosen).
- **Set Perfectionist**, **The Tell → The Snitch**, **Moneyball for Vision**.
- **Body & Angles** layer (feet/hip angle from pose; wingspan/hand via Combine). See `BODY_AND_ANGLES.md`.

## Known limitations (honest)
- Value is **"shoot now"** only; it uses the nearest defender as the contest and distance to
  the attacking hoop — it does not yet weigh passing/driving alternatives.
- `contain_rate` < 1.0 is partly real basketball (help defense, gambling), not pure error.
- The value model trains on 2014-15 shot logs; the matchup brain runs on 2015-16 tracking —
  different seasons, fine for a model but not a single unified game.
- PBP-anchored possession is still the gold standard for the last rare edge cases.

## Run it
```bash
cd read_the_floor
pip install -r requirements-local.txt
python run_sportvu.py ../data/tracking/11.07.2015.CHA.at.SAS.7z --auto   # → matchup_engine.gif
python validate.py   ../data/tracking/11.07.2015.CHA.at.SAS.7z           # robustness numbers
```

## Next (recommended order)
1. Prove **video → coords** (fill the Colab Skalski cell on one clip).
2. **Points Left on the Floor** on the SportVU path (uses what's already built).
3. Grow value into the full **EPV surface**.

Docs: `READ_THE_FLOOR.md` (spec) · `read_the_floor/SETUP.md` (run) · `read_the_floor/VALIDATION.md`
(numbers) · `BODY_AND_ANGLES.md` (biomechanics) · `read_the_floor/experiments/SHOT_QUALITY_NOTE.md`
(the labeling lesson).
