# Requirements: Read the Floor

**Defined:** 2026-06-06
**Core Value:** A real broadcast clip flows end-to-end (video → coords → value/risk brain → X-ray overlay GIF) and is wired as the portfolio's Work-face flagship.

## v1 Requirements

Requirements for the flagship milestone. Each maps to exactly one roadmap phase. Tier-0 requirements are already built & validated (Phase 0 foundation).

### Foundation (built & validated — Phase 0)

- [x] **REQ-tracking-schema**: A single tracking-table schema (`schema.py`) that every data source adapts into; partial rosters handled.
- [x] **REQ-matchup-engine**: Assign each defender to his man live (who-guards-whom) via Hungarian + temporal smoothing (bijection ~0.997, swap ~0.004).
- [x] **REQ-beaten-index**: Per-matchup 0–100 likelihood the defender is about to be beaten (separation spike + off the man-hoop line); non-degenerate (mean ~55, std ~26).
- [x] **REQ-possession-hoop-detection**: Detect possession and attacking hoop from ball control; inversion fixed (possession-52 contain_rate 0.09→0.99, aggregate 0.80→0.89).
- [x] **REQ-shot-quality-value**: Grade every shot attempt in expected points ("shoot now" value model); leave-game-out AUC 0.63, calibrated, wired into the read and colored floor render.
- [x] **REQ-anthro-join**: Join Combine anthropometrics to players by identity (`anthro.py`), verified on real rosters.
- [x] **REQ-top-down-render**: Render the read as a top-down / broadcast X-ray overlay; locked palette, orientation-aware, local CPU runner `.7z`→GIF.

### Video Pipeline (Phase 1)

- [ ] **REQ-video-to-coords**: Skalski video→coordinates adapter feeding the shared schema. A real clip runs end-to-end through Colab cell 3 (RF-DETR + SAM2 + team + jersey + homography) into `frames_out` → brain → render.

### Value & Decision (Phase 2)

- [ ] **REQ-points-left / REQ-decision-grade**: Running tally of expected points lost (EV(best read) − EV(chosen)) cumulated, plus a Decision Grade comparing the actual decision to the optimal read.
- [ ] **REQ-epv-surface**: Full EPV surface — shot prob, pass-success, drive, and turnover probability as spatial functions — beyond "shoot now"; heatmap + running counter.

### Differentiators (Phase 3)

- [ ] **REQ-set-perfectionist**: Recognize the set being run and grade execution vs ideal template (HoopTransformer-style trajectory encoder → classify + grade).
- [ ] **REQ-tell-snitch**: Mine telegraphed pre-decision tendencies (The Tell) → auto one-page scouting report (The Snitch).
- [ ] **REQ-moneyball-vision**: Court-IQ scout — Decision Grade across a prospect's film → Court-Vision percentile independent of scoring, with clip reel.

### Biomechanics (Phase 4)

- [ ] **REQ-body-angles-layer**: Pose-derived angles (`foot_angle`, `hip_angle`, `shoulder_angle`, `knee_bend`) via a pose adapter + Combine-joined anthropometrics → scoring/finishing/passing/defense metrics (Square-Up Score, Stance Read).

### Portfolio (Phase 5)

- [ ] **REQ-portfolio-integration**: Wire Read the Floor onto the cube's Work face as the flagship project card, linking the overlay GIF/stills, per the parent `CLAUDE.md` chapter map (Next.js 14).

## v2 Requirements

Deferred to a future release. Tracked but not in the current roadmap.

### Reads Suite

- **REQ-reads-suite**: The Read, Open Man, Gravity, Skip, Extra Pass, Hot Zones, Spacing Grade, The Gap, Help Is Late, Mismatch Finder, Coverage Read, Rim Pressure, Transition Math — each priced by reward-vs-risk and surfaced on the overlay. Most depend on REQ-epv-surface; surfaced incrementally after Phase 2.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Stats dashboard | The flagship renders a spatial X-ray read, not tables/charts — dashboards are the anti-thesis |
| Hard-coded rule engine | Every flagship piece must learn from data, not encode if/else heuristics |
| Tutorial reskin | Must add the layer no one else has (reading the floor + pricing the risk) |
| Foot-length feature | Not in Combine data, not reliably measurable from broadcast |
| Video-measured body lengths | 2D foreshortening makes single-camera length measurement unreliable; lengths come from Combine join only |

## Traceability

Which phases cover which requirements.

| Requirement | Phase | Status |
|-------------|-------|--------|
| REQ-tracking-schema | Phase 0 | Complete |
| REQ-matchup-engine | Phase 0 | Complete |
| REQ-beaten-index | Phase 0 | Complete |
| REQ-possession-hoop-detection | Phase 0 | Complete |
| REQ-shot-quality-value | Phase 0 | Complete |
| REQ-anthro-join | Phase 0 | Complete |
| REQ-top-down-render | Phase 0 | Complete |
| REQ-video-to-coords | Phase 1 | Pending |
| REQ-points-left / REQ-decision-grade | Phase 2 | Pending |
| REQ-epv-surface | Phase 2 | Pending |
| REQ-set-perfectionist | Phase 3 | Pending |
| REQ-tell-snitch | Phase 3 | Pending |
| REQ-moneyball-vision | Phase 3 | Pending |
| REQ-body-angles-layer | Phase 4 | Pending |
| REQ-portfolio-integration | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 15 total (7 foundation complete + 8 active)
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-06*
*Last updated: 2026-06-06 after initial ingest bootstrap*
