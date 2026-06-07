---
phase: 1
slug: video-coordinates
status: approved
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-06
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Phase 1 has two verification surfaces: a **local GPU-free pytest spine** (plans 01-02,
> runnable on Python 3.9.6) and a **GPU-gated Colab run** (plan 03) whose checks are
> inline asserts + manual visual inspection. The local spine proves the adapter→brain→
> render path on a synthetic `frames_out` of the exact shape Colab cell 3 must emit, so
> the only thing left unverifiable-by-machine is the real CV inference itself.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (local, Python 3.9.6) + inline `assert` checks in Colab cell 4 + manual visual spot-check (Colab cell 3 CV run) |
| **Config file** | none — Wave 0 task (plan 01, Task 3) creates `read_the_floor/requirements-test.txt` with `pytest` |
| **Quick run command** | `cd read_the_floor && python3 -m pytest tests/test_video_path.py -q` |
| **Full suite command** | `cd read_the_floor && python3 -m pytest tests/test_video_path.py -q && python3 validate_video.py --frames-out <fixture.pkl>` (+ existing `python3 validate.py <sportvu_game.7z>` to confirm the brain is unchanged) |
| **Estimated runtime** | ~30–60 seconds local (Colab cell-3 run is 5–15 min, GPU-gated, manual) |

---

## Sampling Rate

- **After every task commit:** Run `cd read_the_floor && python3 -m pytest tests/test_video_path.py -q`
- **After every plan wave:** Run the full suite (pytest + `validate_video.py` on the synthetic fixture)
- **Before `/gsd-verify-work`:** Full local suite green; for plan 03, the Colab adapt-cell `schema.validate(df)` + 6 inline asserts pass on the real clip and a 5-frame visual spot-check passes
- **Max feedback latency:** ~60 seconds (local); the Colab leg is a deliberate manual gate (GPU-gated, `autonomous: false`)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | REQ-video-to-coords | T-01-01 | Court vertices in FEET (x∈[0,94], y∈[0,50]); cm/px regression fails the assert (coordinate-unit safety net) | unit | `cd read_the_floor && python3 -c "import basketball_court_config as c, numpy as np; v=c.vertices_ft(); assert (v[:,0]>=0).all() and (v[:,0]<=94).all() and (v[:,1]>=0).all() and (v[:,1]<=50).all()"` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | REQ-video-to-coords | T-01-01 | Synthetic fixture emits the exact 5-tuple; stable positive `track_id`; feet coords | unit | `cd read_the_floor && python3 -c "import sys; sys.path.insert(0,'.'); from fixtures.frames_out_synthetic import make_frames_out; from adapters import skalski; import schema; fo=make_frames_out(20); df=skalski.build_table([skalski.frame_to_rows(i,*t) for i,t in enumerate(fo)]); schema.validate(df); assert df[~df.is_ball].x.between(0,94).all()"` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01 | 1 | REQ-video-to-coords | T-01-01 | Full local spine (config→adapter→schema→brain→render) green without GPU/CV deps | integration | `cd read_the_floor && python3 -m pytest tests/test_video_path.py -q` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 2 | REQ-video-to-coords | T-01-04 | `run_video.py` renders X-ray GIF + stills via unchanged adapter/brain/render; no pickle from untrusted source | integration | `cd read_the_floor && python3 run_video.py --frames-out <fixture.pkl> --out v.gif --stills 3 --frames-dir frames` (exit 0, non-empty GIF, 3 stills, peak-Beaten-Index line) | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 2 | REQ-video-to-coords | T-01-04 | `validate_video.py` reports validate.py metrics + SC4 sanity verdicts vs SportVU baseline | integration | `cd read_the_floor && python3 validate_video.py --frames-out <fixture.pkl>` (exit 0; stdout has valid_rate/swap_rate/beaten_mean/contain_rate + `SC4` PASS/WARN) | ❌ W0 | ⬜ pending |
| 01-03-02 | 03 | 3 | REQ-video-to-coords | T-01-07 / T-01-08 | Cell 3 targets FEET via `vertices_ft()`; SAM2 `tracker_id` wired; API key only via `userdata.get`; adapter/schema/brain/render unchanged | structure | `cd read_the_floor && python3 -c "import json; nb=json.load(open('colab_read_the_floor.ipynb')); src=''.join(''.join(c.get('source',[])) for c in nb['cells']); assert 'frames_out' in src and ('vertices_ft' in src or 'BASKETBALL_COURT_VERTICES_FT' in src) and 'skalski.frame_to_rows' in src and 'between(0,94)' in src.replace(' ','')"` + `git diff --quiet read_the_floor/adapters/skalski.py read_the_floor/schema.py` | ✅ (notebook stub) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Manual-gated tasks (no machine verify) are listed below, not in this map: 01-03-01 (Wave-0 prerequisites: clip/GPU/key/keypoint order) and 01-03-03 (real-clip run → GIF + SC4 sanity + visual spot-check).*

---

## Wave 0 Requirements

- [ ] `read_the_floor/requirements-test.txt` — adds `pytest` (no test framework configured yet) — created by plan 01, Task 3
- [ ] `read_the_floor/basketball_court_config.py` — court vertices in FEET; the coordinate-unit safety net every downstream assert depends on (plan 01, Task 1)
- [ ] `read_the_floor/fixtures/frames_out_synthetic.py` — `make_frames_out()` shared test fixture consumed by plans 01-02-03 (plan 01, Task 2)
- [ ] `read_the_floor/tests/__init__.py` + `read_the_floor/tests/test_video_path.py` — the 5-test spine (plan 01, Task 3)

*External Wave-0 prerequisites (no automated solution — plan 03, Task 1 checkpoint): a 5–15s `.mp4` clip, a Colab T4 GPU session, a `ROBOFLOW_API_KEY` Colab secret, and the confirmed court-keypoint index ordering.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Cell 3 runs on one real clip producing `frames_out` (len > 0) with no exception | REQ-video-to-coords / SC1 | Requires a Colab T4 GPU (RF-DETR + SAM2); local Python is 3.9.6, below sam2's 3.10+ | Runtime → T4 GPU; run install/modules/cell-3 cells on `/content/clip.mp4`; confirm `len(frames_out) > 0` |
| Adapt cell `schema.validate(df)` + 6 inline geometry/presence asserts pass on the REAL clip | REQ-video-to-coords / SC2 | Asserts run inside the Colab session against live CV output | Run the adapt cell; paste the cell output (asserts pass) into the resume signal |
| `brain.run(df)` + overlay GIF renders inline on video-derived coords | REQ-video-to-coords / SC3 | Depends on the real `frames_out` from the GPU run | Run the brain+render cell; confirm the X-ray overlay GIF displays inline |
| SC4 sanity vs SportVU baseline (hoop-dist 5–40ft, control >0.6, beaten_std >5) + 5-frame visual spot-check | REQ-video-to-coords / SC4 | Plausibility/eyeball comparison of dots-to-video; not a binary unit test | Download `frames_out.pkl`; run `python3 validate_video.py --frames-out frames_out.pkl` (PASS, or documented WARN); compare 5 stills to source frames |
| Artifacts persisted: `prototypes/video_matchup.gif` + `read_the_floor/frames/still_*.png` | REQ-video-to-coords / SC4 | Produced by the operator's GPU run | `test -s prototypes/video_matchup.gif` and `ls read_the_floor/frames/still_*.png` |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies (manual-gated Colab tasks 01-03-01/03 are documented above with explicit resume signals)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify (all 3 autonomous wave-1/2 tasks plus the cell-3 structure check are machine-verified; the 2 remaining are GPU-gated human checkpoints by necessity)
- [x] Wave 0 covers all MISSING references (court config + fixture + tests + pytest install created in plan 01; external clip/GPU/key gated in plan 03 Task 1)
- [x] No watch-mode flags
- [x] Feedback latency < 60s (local spine)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-06
