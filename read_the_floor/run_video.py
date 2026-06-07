"""Video-path runner — the Track-B analog of run_sportvu.py (no GPU needed).

Consumes an already-projected `frames_out` (a pickle produced by Colab cell 3, or the
synthetic fixture), runs the UNCHANGED skalski adapter -> schema -> brain -> render, and
writes the broadcast X-ray GIF + N evenly-spaced overlay stills.

Load only a frames_out YOU generated (pickle is unsafe on untrusted input).

Usage:
    python run_video.py --frames-out frames_out.pkl --out matchup_video.gif --stills 5
"""
import argparse
import os
import pickle
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schema
import brain
import render
from adapters import skalski


def main():
    ap = argparse.ArgumentParser(description="Render the read from a saved frames_out.")
    ap.add_argument("--frames-out", required=True, help="path to a pickled frames_out list")
    ap.add_argument("--out", default="matchup_video.gif", help="output GIF path")
    ap.add_argument("--stills", type=int, default=5, help="number of overlay stills to dump")
    ap.add_argument("--frames-dir", default="frames", help="directory for stills")
    a = ap.parse_args()

    if not os.path.exists(a.frames_out):
        ap.error(f"frames_out not found: {a.frames_out}")

    with open(a.frames_out, "rb") as fh:
        frames_out = pickle.load(fh)

    per_frame = [skalski.frame_to_rows(i, *t) for i, t in enumerate(frames_out)]
    df = skalski.build_table(per_frame, smooth=True)
    schema.validate(df)
    results, off_team, hoop = brain.run(df)
    peak = max((max((p["beaten"] for p in r["pairs"]), default=0) for r in results), default=0)
    print(f"frames {len(results)} | offense {off_team} | peak Beaten Index {peak:.0f}")

    render.render_gif(results, df, a.out)
    print(f"wrote {a.out}")

    if a.stills > 0:
        import imageio
        os.makedirs(a.frames_dir, exist_ok=True)
        gif = imageio.mimread(a.out)
        idxs = np.linspace(0, len(gif) - 1, a.stills).astype(int)
        for k, gi in enumerate(idxs):
            p = os.path.join(a.frames_dir, f"still_{k:02d}.png")
            imageio.imwrite(p, gif[gi])
        print(f"wrote {a.stills} stills to {a.frames_dir}/")


if __name__ == "__main__":
    main()
