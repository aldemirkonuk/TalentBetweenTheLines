"""Top-down render of the Matchup Engine output, in the locked palette."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc
import imageio
from brain import BG, EARTH, INK, STONE, TEAL


def _ramp(b):
    t = b / 100
    if t < 0.5:
        s = t / 0.5; c0 = (0.24, 0.39, 0.30); c1 = (0.48, 0.37, 0.19)
    else:
        s = (t - 0.5) / 0.5; c0 = (0.48, 0.37, 0.19); c1 = (0.78, 0.27, 0.16)
    return tuple(c0[k] + (c1[k] - c0[k]) * s for k in range(3))


def _court(ax):
    ax.add_patch(Rectangle((0, 0), 94, 50, fill=False, ec="#B8B4A8", lw=1.4))
    ax.plot([47, 47], [0, 50], color="#B8B4A8", lw=1)
    ax.add_patch(Arc((47, 25), 12, 12, theta1=-90, theta2=90, ec="#B8B4A8", lw=1))
    hx = 88.75
    ax.add_patch(Circle((hx, 25), 0.75, fill=False, ec=EARTH, lw=1.6))
    ax.add_patch(Rectangle((75, 17), 19, 16, fill=False, ec="#B8B4A8", lw=1))
    ax.add_patch(Arc((75, 25), 12, 12, theta1=-90, theta2=90, ec="#B8B4A8", lw=1))
    ax.add_patch(Arc((hx, 25), 47.5, 47.5, theta1=112, theta2=248, ec="#B8B4A8", lw=1))
    ax.plot([94, 80.2], [3, 3], color="#B8B4A8", lw=1)
    ax.plot([94, 80.2], [47, 47], color="#B8B4A8", lw=1)


def render_gif(results, df, out_path, fps=12, step=2):
    ball_by_frame = {int(r.frame): (r.x, r.y)
                     for r in df[df.is_ball].itertuples()}
    # Orient so the attack is always toward the right hoop: mirror x if the
    # possession attacks the left basket. Keeps the court drawing/zoom valid both ways.
    flip = results and results[0]["hoop"][0] < 47
    fx = (lambda x: 94 - x) if flip else (lambda x: x)
    imgs = []
    for res in results[::step]:
        off, dfn, pairs = res["off"], res["dfn"], res["pairs"]
        fig = plt.figure(figsize=(9.4, 5.2), dpi=100); ax = fig.add_axes([0, 0, 1, 1])
        fig.patch.set_facecolor(BG); ax.set_facecolor(BG); _court(ax)
        # tether color = VALUE of that man's shot now (expected points). hot = more points.
        vscore = lambda v: float(np.clip((v - 0.5) / 0.8 * 100, 0, 100))
        best = max(pairs, key=lambda p: p["value"]) if pairs else None
        for p in pairs:
            d = np.array(p["dpos"]); o = np.array(p["opos"]); s = vscore(p["value"])
            ax.plot([fx(d[0]), fx(o[0])], [d[1], o[1]], color=_ramp(s),
                    lw=1.2 + 4.5 * s / 100, solid_capstyle="round", zorder=2)
        for (name, ox, oy) in off.values():
            ax.add_patch(Circle((fx(ox), oy), 1.25, color=TEAL, ec="#1f6b56", lw=0.6, zorder=4))
        for (name, dx, dy) in dfn.values():
            ax.add_patch(Circle((fx(dx), dy), 1.25, color=STONE, ec="#7d7563", lw=0.6, zorder=4))
        if res["frame"] in ball_by_frame:
            bx, by = ball_by_frame[res["frame"]]
            ax.add_patch(Circle((fx(bx), by), 0.75, color=EARTH, zorder=5))
        if best is not None:
            ox, oy = best["opos"]
            ax.text(fx(ox), oy + 2.6, f"{str(best['off_name']).upper()} +{best['value']:.1f}",
                    color="#9c3a22", fontsize=9, ha="center", weight="bold",
                    family="monospace", zorder=6)
        ax.text(48, 53.3, "READ THE FLOOR", color=EARTH, fontsize=11, family="monospace",
                weight="bold", ha="left")
        ax.text(48, 50.9, "value of the floor", color=INK,
                fontsize=8.5, family="monospace", ha="left")
        ax.text(92, 53.3, f"{res['frame']}", color=INK, fontsize=12, family="monospace",
                ha="right", weight="bold")
        bn = str(best["off_name"]).upper() if best else "-"
        bv = best["value"] if best else 0.0
        ax.text(92, 50.9, f"best read  {bn} +{bv:.2f}", color=_ramp(vscore(bv)),
                fontsize=9, family="monospace", ha="right", weight="bold")
        ax.set_xlim(43, 97); ax.set_ylim(-3, 56); ax.axis("off"); ax.set_aspect("equal")
        fig.canvas.draw()
        buf = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8).reshape(
            int(fig.bbox.height), int(fig.bbox.width), 4)[..., :3]
        imgs.append(buf.copy()); plt.close(fig)
    imageio.mimsave(out_path, imgs, fps=fps, loop=0)
    return out_path
