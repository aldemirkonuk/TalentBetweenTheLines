"""Robustness checks for the Matchup Engine.

Runs the brain over many possessions and reports:
  - assignment validity : is each frame's defender->man map a bijection (no two
    defenders on the same man)? should be ~100%.
  - assignment stability: how often a defender's assigned man flips frame-to-frame
    (swap rate). lower = steadier tracking. (sticky smoothing should keep this low.)
  - beaten index health : not degenerate (varies, sane range), and defenders are on
    average between their man and the hoop (contain geometry sign check).

Usage: python validate.py data/tracking/<game>.7z
"""
import sys, json, tempfile, os
import numpy as np
from adapters import sportvu
import brain


def possessions(json_path, n=10, min_len=180):
    j = json.load(open(json_path))
    cand = []
    for i, e in enumerate(j["events"]):
        ms = e.get("moments", [])
        if len(ms) < min_len:
            continue
        bx = [m[5][0][2] for m in ms if m[5]]
        if bx:
            cand.append((max(bx) - min(bx), i))
    cand.sort()
    return [i for _, i in cand[:n]]


def check(json_path, ev):
    df = sportvu.event_to_table(json_path, ev)
    results, off_team, hoop = brain.run(df)
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
            contain += int(np.dot(v, u) > 0)   # defender on the hoop side of his man
    n = len(results)
    return dict(frames=n, valid_rate=round(valid / n, 3),
                swap_rate=round(swaps / max(1, pair_frames), 3),
                beaten_mean=round(float(np.mean(beaten_all)), 1),
                beaten_std=round(float(np.std(beaten_all)), 1),
                contain_rate=round(contain / max(1, len(beaten_all)), 3))


def main():
    path = sys.argv[1]
    if path.endswith(".7z"):
        import py7zr
        d = tempfile.mkdtemp()
        with py7zr.SevenZipFile(path) as z:
            z.extractall(path=d)
        path = os.path.join(d, os.listdir(d)[0])
    evs = possessions(path, n=10)
    print(f"possessions: {evs}")
    agg = {}
    for ev in evs:
        try:
            r = check(path, ev)
            for k, v in r.items():
                agg.setdefault(k, []).append(v)
            print(f"  ev {ev:>4}: {r}")
        except Exception as e:
            print(f"  ev {ev}: ERR {str(e)[:60]}")
    print("\nAGGREGATE (mean over possessions):")
    for k, vs in agg.items():
        print(f"  {k:14s} {np.mean(vs):.3f}")


if __name__ == "__main__":
    main()
