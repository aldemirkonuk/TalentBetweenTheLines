# Body & Angles — the biomechanics edition

Extends Read the Floor from *where players are* to *how their bodies are built and oriented* —
and how that drives scoring, finishing, passing, and defense.

## The core split (read this first)
There are **two** sources of body data, and confusing them wastes effort:

1. **Anthropometrics = look it up.** The NBA already measures wingspan, standing reach,
   hand length/width, height, weight, body fat, AND max vertical leap at the Draft Combine,
   and publishes it. We **join by player identity** — we do NOT measure these from video.
   (Measuring arm length from one broadcast camera is unreliable: a 2D view foreshortens
   segments depending on pose. The tape measure already won.)

2. **Angles & pose = infer from video.** Foot/hip/shoulder orientation, knee bend, balance,
   extension, release point — these are *per-moment* and only exist in the footage.
   From a pose model (RTMPose / COCO-WholeBody, which include foot keypoints).
   Rule of thumb: **orientation (angles) is robust; absolute lengths are not** — so use pose
   for angles, combine for lengths.

---

## What you asked for, measurement by measurement

### Feet & body angle → success  (your lead idea — strong)
- **Measure:** foot/hip orientation in the ground plane relative to the basket and to the
  defender, at key moments (catch, gather, release; for D, at the closeout/drive).
- **Offense metric — "Square-Up Score":** how squared the feet/hips are to the rim at
  release, correlated with FG%. Hypothesis: squared = better; drifting/open stance = worse.
- **Drive metric:** the angle a ball-handler attacks vs the defender's hip orientation —
  you beat a defender to his **back foot** (the direction his stance can't cover quickly).
- **Defense metric — "Stance Read":** which foot/hip angles give the defender the **lowest
  blow-by rate** (best containment). Mine across thousands of matchups to learn the optimal
  stance, then grade each defender against it.
- **Feasibility:** 🟡 pose works; foot keypoints are noisy on wide broadcast angles, cleaner
  on tighter shots. Angles are the robust signal here.

### Arm length / wingspan / reach → defense, finishing, dunks
- **Source:** Combine (wingspan, standing reach). **Join, don't measure.**
- **Metrics:** correlate reach with contest effectiveness (shots altered), rim finishing %,
  passing-lane deflections. 🟢 data is clean; the outcome side comes from tracking + PBP.

### Hand size → ball security & finishing
- **Source:** Combine (hand length, hand width).
- **Metrics:** correlate with turnover rate, finishing through contact, strip rate on D.
  🟢 clean join.

### Foot length → ?  (honest pushback)
- **Not in Combine data** (they measure hands, not feet) and **~impossible from broadcast**
  (feet are tiny, occluded, motion-blurred). Shoe size is occasionally public but unreliable
  and not a clean proxy. **Recommendation: drop it, or treat as a low-priority stretch.** 🔴

### Influence on dunks
- **Source:** Combine **standing reach + max vertical leap** → dunk reach.
- **Metric:** correlate dunk reach with dunk frequency/efficiency (dunk events from PBP /
  shot detection). 🟢 anthro side; 🟡 dunk-event detection from video.

### Scoring per position + correlation to efficiency
- **Two meanings, do both:**
  - **By court zone** (already our value surface): scoring & efficiency by spot on the floor.
  - **By player position** (PG/SG/SF/PF/C, from roster): correlate anthropometrics + spatial
    behavior with efficiency (TS%, eFG%) per position.
- **Metric:** which body/angle traits predict efficient scoring, and how that differs by
  position. 🟢 (shot + roster data exist; combine for the body traits).

---

## How it bolts onto what we have
- New table columns (optional, per player per frame): `foot_angle`, `hip_angle`,
  `shoulder_angle`, `knee_bend` — emitted by a **pose adapter** (RTMPose) that runs alongside
  the Skalski pipeline. Same `schema.py` contract, just more columns.
- A static **`players_anthro.csv`** (combine join, one row per player) the brain merges by
  `identity`.
- New brain modules: `square_up.py` (angle→shot), `stance.py` (defender angle→blow-by),
  `anthro_corr.py` (combine→efficiency/dunks).

## Feasibility summary
- 🟢 wingspan/reach/hand → defense/finishing/dunks/efficiency (data join)
- 🟢 scoring by zone & position → efficiency correlation
- 🟡 feet/hip angle → square-up & stance (pose; noisy on wide angles)
- 🟡 dunk-event detection from video
- 🔴 foot length (not in data, not reliably measurable)
