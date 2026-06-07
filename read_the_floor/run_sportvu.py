"""Local quick-win entry point — no GPU needed.

Runs the Matchup Engine on a SportVU game (the open 2015-16 tracking data),
straight to a top-down GIF. This is the fastest way to see the brain work.

Usage:
    python run_sportvu.py data/tracking/01.02.2016.HOU.at.SAS.7z --auto
    python run_sportvu.py game.json --event 362 --out matchup.gif

--auto picks the longest half-court possession for you.
"""
import argparse, json, os, tempfile
import numpy as np
import pandas as pd
from adapters import sportvu
import schema, brain, render


def load_json(path):
    if path.endswith(".json"):
        return path
    import py7zr  # only needed for .7z
    d = tempfile.mkdtemp()
    with py7zr.SevenZipFile(path) as z:
        z.extractall(path=d)
    return os.path.join(d, os.listdir(d)[0])


def pick_event(json_path):
    j = json.load(open(json_path))
    best, score = None, 1e9
    for i, e in enumerate(j["events"]):
        ms = e.get("moments", [])
        if len(ms) < 200:
            continue
        bx = [m[5][0][2] for m in ms if m[5]]
        if not bx:
            continue
        rng = max(bx) - min(bx)            # small range = half-court possession
        if rng < score:
            score, best = rng, i
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("game", help=".7z game file or extracted .json")
    ap.add_argument("--event", type=int, default=None)
    ap.add_argument("--auto", action="store_true", help="auto-pick a clean possession")
    ap.add_argument("--out", default="matchup_engine.gif")
    a = ap.parse_args()

    jp = load_json(a.game)
    ev = a.event if a.event is not None else (pick_event(jp) if a.auto else 0)
    print(f"event {ev}")
    df = sportvu.event_to_table(jp, ev)
    schema.validate(df)
    results, off_team, hoop = brain.run(df)
    peak = max((max((p["beaten"] for p in r["pairs"]), default=0) for r in results), default=0)
    print(f"frames {len(results)} | offense {off_team} | peak Beaten Index {peak:.0f}")
    render.render_gif(results, df, a.out)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
