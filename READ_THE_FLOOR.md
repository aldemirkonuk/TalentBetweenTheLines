# Read the Floor — Project Spec

> *"I read the floor. I find the gap. I weigh the risk. I show it as light."*

A computer-vision system that watches basketball footage and renders the **value of the floor** —
where points are, what the best read is, and what it risks — as a broadcast-grade overlay.

---

## What the system does (one line each)
- Finds, tracks, and names every player automatically from a clip.
- Splits them into teams and pins each to a precise top-down court position.
- Prices every spot on the floor by how many points it's worth right now.
- Scores each available pass and drive by reward vs. turnover risk.
- Surfaces the single highest reward-to-risk read — the gap.
- Paints all of it back onto the live footage as a broadcast X-ray overlay.

## Pipeline (fork of Skalski / Roboflow "sports")
1. Detect players + jersey numbers — RF-DETR
2. Track players — SAM2 (stable IDs through occlusion)
3. Assign teams — SigLIP → UMAP → K-Means (zero-shot)
4. Read jersey numbers — SmolVLM2, voted across frames
5. Map to court coordinates — keypoints + homography → top-down
6. Detect + classify shots — make/miss → shot chart
+ OUR LAYER: value surface (EPV), risk analysis, X-ray render

---

## LOCKED features (v1 candidate set)

### Reading the offense (the gap)
- **The Read** — the single best action with the ball, by reward-for-risk.
- **The Open Man** — who's open and how open (wide / contested / denied).
- **Gravity** — how much each player bends the defense.
- **The Skip** — cross-court skip pass vs. safe swing, priced.
- **The Extra Pass** — does one more pass raise the shot's value.

### Shot & spacing
- **Shot Quality** — every attempt graded in expected points.
- **Hot Zones** — each player's personal scoring spots (tendencies).
- **Spacing Grade** — floor balance: spread vs. clogged.

### Reading the defense (the risk)
- **The Gap** — the soft spot + countdown to when it closes.
- **Help Is Late** — the help defender / closeout a step slow.
- **Mismatch Finder** — big-on-guard, and where to attack it.
- **Coverage Read** — drop / switch / ice / blitz.
- **Rim Pressure** — how protected the basket is right now.

### Whole-possession
- **Transition Math** — numbers on the break (3-on-2) + fastest attack.
- **Decision Grade** — actual decision vs. optimal read.

---

## v2 LOCKED additions
- **Feet Location (all 10)** — precise on-court foot position of every player, offense + defense, every frame.
- **The Matchup (Who Guards Whom)** — assigns each defender to his man, live; the spine for everything defensive.
- **Beaten Likelihood** — per matchup, how likely the defender is about to get beaten (separation + off-the-line).
- **Set Perfectionist** — recognizes the set being run and grades whether it reached its full potential.
- **The Tell** — telegraphed tendencies a player tips before he commits.
- **The Snitch** — instant one-page scouting report from a handful of clips.
- **Points Left on the Floor** — running tally of expected points lost to suboptimal reads.
- **Moneyball for Vision** — court-IQ scout for undervalued talent in lower-level film.

---

## FOCUS FIVE (engineered for build)

### 1. The Matchup Engine  (Who Guards Whom + Beaten Index)
- **In:** top-down feet coords of all 10 + ball, per frame.
- **Model:** optimal defender-assignment (Franks/Bornn 2015) — each defender's expected anchor = weighted blend of his man, ball, hoop; Hungarian assignment + HMM smoothing for stable IDs over time.
- **Beaten Index:** track man-defender separation and whether defender stays on the man-hoop line; separation spike + off-line = beaten (0–100).
- **Out:** defender→man tethers that glow as a matchup is lost.
- **Data:** SportVU 2015-16 (both teams' XY) to build/validate; broadcast pipeline for live. **Difficulty: Medium.**

### 2. Value Surface + Points Left on the Floor  (EPV)
- **In:** top-down positions, ball, matchups (from #1).
- **Model:** approximate EPV (Cervone / Fernández) — shot prob, pass-success, turnover prob as functions of spatial config; trained on labeled possessions.
- **Points Left:** at each decision, EV(best option) − EV(chosen), cumulated.
- **Out:** the heatmap, the running counter, Decision Grade.
- **Data:** SportVU 2015-16 + PBP outcomes (90,524 possessions). **Difficulty: High (model), data exists.**

### 3. Set Perfectionist  (Play Recognition + Execution Grade)
- **In:** offensive trajectories for a possession.
- **Model:** HoopTransformer-style self-supervised trajectory encoder → classify the set; grade execution vs ideal template (cut timing, spacing, screen angle).
- **Out:** "Horns Flare, run at 72% — screener slipped early, killed the flare."
- **Data:** SportVU 2015-16; HoopTransformer (2024) proves recognition. **Difficulty: High, research-backed.**

### 4. The Tell → The Snitch  (Tendency Mining → Scouting Report)
- **In:** many ID'd possessions per player.
- **Model:** mine pre-decision micro-features (dribble hand, drop-step dir, screen-reject rate, time-to-decide) conditioned on context; sequence model finds telegraphing patterns; aggregate into a report.
- **Out:** "78% right out of a ghost screen" + auto one-pager.
- **Data:** volume of per-player tracking — strong for 2015-16 players, thin for current (needs broadcast-derived volume). **Difficulty: High; data-volume bottleneck.**

### 5. Moneyball for Vision  (Court-IQ Scout)
- **In:** any film → broadcast pipeline → top-down → value model (#2).
- **Model:** run Decision Grade across a prospect's film → Court-Vision percentile independent of scoring; flag undervalued IQ.
- **Out:** vision score + clip reel of elite reads the box score hides.
- **Data:** the catch — NBA-trained value model may not transfer to HS/college spacing; needs domain adaptation. **Difficulty: High; transfer is the risk, but this is the "change the game" one.**

---

## FEASIBILITY (doability check)
- 🟢 Feet location / tracking — Skalski pipeline, proven.
- 🟢 Who guards whom — Franks/Bornn 2015 method, reproducible on open tracking.
- 🟢 Beaten Index — derives directly from matchup + separation.
- 🟢 Set recognition — HoopTransformer 2024 + 632-game open set.
- 🟡 EPV / Points Left — model is hard but data (90k possessions) exists.
- 🟡 The Tell / Snitch — works for 2015-16 players; current players limited by tracking volume.
- 🔴→🟡 Moneyball for Vision — biggest payoff, biggest risk (cross-level transfer).

## BUILD STATUS (what's actually implemented — see `STATE.md`)
- ✅ **Built & validated:** tracking-table schema, Matchup Engine (who-guards-whom + Beaten
  Index), possession/hoop detection (inversion fixed), Shot-Quality value model (AUC 0.63,
  calibrated) wired into the read, top-down render, Combine anthro join, local runner.
- 🟡 **Adapter written, not yet run end-to-end:** Skalski video → coords (Colab cell is a stub;
  only the SportVU path is proven).
- 📋 **Spec-only (not built):** full EPV surface (pass/drive/turnover), Points Left on the
  Floor / Decision Grade, Set Perfectionist, The Tell → The Snitch, Moneyball for Vision,
  the Body & Angles layer.

## Body & Angles edition
Biomechanics layer — feet/hip angle → shot & stance success, wingspan/hand (Combine join)
→ defense/finishing/dunks, scoring-by-position efficiency. Full spec + feasibility:
`BODY_AND_ANGLES.md`. Setup runbook: `read_the_floor/SETUP.md`.

## EDGY backlog (the "could change the game" ideas)
- The Road Not Taken — simulate the pass he didn't make; show the ghost bucket.
- Points Left on the Floor — running tally of expected points lost to bad reads.
- Clutch Realness — does decision quality rise or crack under pressure.
- Hero-Ball Meter — when a star iced out the open man.
- The Ankle Index — how badly a defender got beaten (separation created).
- The Tell — telegraphed tendencies a player tips before he moves.
- Vision Fingerprint — ID a player purely by how he reads the floor.
- The Snitch — instant scouting report of a player's risky habits from a few clips.
- No-Call X-Ray — contact/leverage the broadcast and refs missed.
- Moneyball for Vision — find undervalued court-IQ in lower-level film.
