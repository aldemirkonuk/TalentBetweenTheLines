"""Video-path robustness report — the Track-B analog of validate.py (no GPU needed).

Runs the brain over a video-derived tracking table (from a saved frames_out) and prints
the SAME robustness metrics validate.py reports (valid_rate, swap_rate, beaten_mean/std,
contain_rate), plus the RESEARCH SC4 sanity signals (median attacking-hoop distance,
offense ball-control share, Beaten Index spread) with PASS/WARN verdicts — so a video run
can be eyeballed against the SportVU baseline.

This is a REPORT, not a gate: it always exits 0; a WARN is printed text, not a failure.
Load only a frames_out YOU generated (pickle is unsafe on untrusted input).

Usage:
    python validate_video.py --frames-out frames_out.pkl
"""
import argparse
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schema
import brain
from adapters import skalski


def metrics(results, hoop):
    """Mirror validate.py.check(): bijection validity, swap rate, beaten spread, contain."""
    valid, swaps, beaten_all, contain = 0, 0, [], 0
    pair_frames, prev = 0, {}
    for r in results:
        offs = {p["off_id"] for p in r["pairs"]}
        valid += int(len(offs) == len(r["pairs"]) and len(r["pairs"]) > 0)
        cur = {p["def_id"]: p["off_id"] for p in r["pairs"]}
        for dt, ot in cur.items():
            pair_frames += 1
            if dt in prev and prev[dt] != ot:
                swaps += 1
        prev = cur
        for p in r["pairs"]:
            beaten_all.append(p["beaten"])
            d = np.array(p["dpos"]); o = np.array(p["opos"])
            u = hoop - o; v = d - o
            contain += int(np.dot(v, u) > 0)
    n = max(1, len(results))
    return dict(frames=len(results), valid_rate=round(valid / n, 3),
                swap_rate=round(swaps / max(1, pair_frames), 3),
                beaten_mean=round(float(np.mean(beaten_all)), 1) if beaten_all else 0.0,
                beaten_std=round(float(np.std(beaten_all)), 1) if beaten_all else 0.0,
                contain_rate=round(contain / max(1, len(beaten_all)), 3))


def control_share(df):
    """Offense ball-control share, recomputed from PUBLIC symbols only.

    For each frame, the non-ball player nearest the ball within brain.POSSESSION_R counts
    a control frame for his team. Returns max-team-share over controlled frames. Uses only
    public symbols — it does not reach into the brain's private control-frame helper.
    """
    votes = {}
    for _, g in df.groupby("frame"):
        ball = g[g.is_ball]; pl = g[~g.is_ball]
        if ball.empty or pl.empty:
            continue
        bx, by = ball.iloc[0][["x", "y"]]
        dists = np.hypot(pl.x - bx, pl.y - by).values
        i = int(np.argmin(dists))
        if dists[i] <= brain.POSSESSION_R:
            t = int(pl.iloc[i].team)
            votes[t] = votes.get(t, 0) + 1
    total = sum(votes.values())
    return (max(votes.values()) / total) if total else 0.0


def main():
    ap = argparse.ArgumentParser(description="Robustness report for a video-derived frames_out.")
    ap.add_argument("--frames-out", required=True, help="path to a pickled frames_out list")
    a = ap.parse_args()

    if not os.path.exists(a.frames_out):
        ap.error(f"frames_out not found: {a.frames_out}")

    with open(a.frames_out, "rb") as fh:
        frames_out = pickle.load(fh)

    per_frame = [skalski.frame_to_rows(i, *t) for i, t in enumerate(frames_out)]
    df = skalski.build_table(per_frame, smooth=True)
    schema.validate(df)
    results, off_team, hoop = brain.run(df)

    m = metrics(results, hoop)
    print("METRICS", m)

    # SC4 sanity signals vs the SportVU baseline (RESEARCH).
    hoop_dists = [float(np.hypot(p["opos"][0] - hoop[0], p["opos"][1] - hoop[1]))
                  for r in results for p in r["pairs"]]
    hd = float(np.median(hoop_dists)) if hoop_dists else 0.0
    cs = control_share(df)
    bs = m["beaten_std"]

    hd_v = "PASS" if 5.0 <= hd <= 40.0 else "WARN"     # SportVU median ~18 ft
    cs_v = "PASS" if cs > 0.6 else "WARN"               # one team clearly on offense
    bs_v = "PASS" if bs > 5.0 else "WARN"               # SportVU beaten std ~20+

    print(f"SC4 hoop_dist_median={hd:.1f} ({hd_v})  "
          f"control_share={cs:.2f} ({cs_v})  beaten_std={bs:.1f} ({bs_v})")
    print(f"(offense team {off_team}; SportVU baseline: valid_rate ~1.0, swap low, beaten_mean ~55)")


if __name__ == "__main__":
    main()
