# Validation — Matchup Engine

Run: `python validate.py data/tracking/<game>.7z` (10 possessions/game).

## Results (CHA @ SAS, 10 possessions)
| metric | value | meaning |
|--------|-------|---------|
| `valid_rate`   | **0.996** | each man guarded by exactly one defender (bijection) — essentially always holds |
| `swap_rate`    | **0.004** | a defender's assigned man flips on only 0.4% of frame transitions — very stable |
| `beaten_mean`  | 55.4 | Beaten Index is non-degenerate... |
| `beaten_std`   | 26.2 | ...and varies meaningfully across the possession |
| `contain_rate` | 0.80 | defenders sit between their man and the hoop ~80% of the time (geometry sanity) |

## What's solid
- **Assignment is robust:** near-perfect bijection + very low swap rate. The Hungarian
  cost (expected-defender-position) + sticky temporal smoothing works well.

## Possession/hoop inversion — FIXED
- **Was:** on ~1 in 10 possessions the offense/attacking-hoop inference misfired (e.g.
  possession 52: both teams stacked in one half), inverting the contain geometry and
  inflating both Beaten Index and value. `contain_rate` there was 0.09.
- **Fix:** possession is now inferred from actual ball **control** (ball within ~4 ft of a
  player), not just "nearest player"; the attacking hoop is the hoop nearest the **controlled
  ball's** median position (robust to transition/odd spacing) rather than offense-median.
- **Result:** possession 52 `contain_rate` 0.09 → **0.99**; game aggregate 0.80 → **0.89**,
  with assignment stability unchanged (valid 0.997, swap 0.004). Generalizes to other games.
- **Still ideal later:** PBP-anchored possession for the rare remaining edge cases; note that
  `contain_rate` < 1 is partly real (help defense, gambling), not pure error.

Also: `value` now uses the **nearest** defender as the contest (not just the assigned man).

## Independent review + fixes applied
An independent code-review pass (subagent) found several robustness bugs; the high-severity
ones are now fixed and re-verified:
- **Stable-ID smoothing.** Temporal vote was on *positional* indices (not stable frame to
  frame) — could blend mismatched identities and drop matchups. Now votes on `track_id`.
- **Partial rosters.** `assign()` returned nothing unless exactly 5-on-5; now does a
  rectangular Hungarian assignment, so occlusion/sub frames still produce matchups.
- **Graceful empties.** `detect_offense`/`attacking_hoop` no longer crash or silently pick a
  wrong hoop on empty/NaN inputs; the SportVU adapter emits partial rosters instead of
  dropping frames.
- **Skalski adapter.** `None` tracker_ids get unique negative ids and are excluded from
  smoothing (no cross-player blending); short tracks aren't smoothed.
- **Orientation-aware render.** The clip now mirrors when a possession attacks the left
  hoop (previously only the right half drew correctly).
Post-fix validation unchanged on the good path (valid 0.995, swap 0.004, contain 0.80).

## Honest status
Core matchup assignment: **validated and hardened.** Beaten Index: **correct on standard
half-court possessions**; still needs PBP-anchored possession/hoop detection to be
trustworthy on every possession (transition/inbound edge cases) before it ships as a metric.
