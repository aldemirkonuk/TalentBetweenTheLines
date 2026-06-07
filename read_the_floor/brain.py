"""The brain: reads a tracking table (schema.py) and computes the read.

v1 implements the Matchup Engine:
  - who guards whom   (Hungarian assignment on expected-defender-position)
  - the Beaten Index  (0..100, how open each offensive man is)
  - a top-down render in the locked palette

Pipeline-agnostic: works identically on SportVU coords or Skalski-extracted coords.
"""
import numpy as np
from scipy.optimize import linear_sum_assignment
from schema import HOOPS
from value import expected_points

THREE_PT_FT = 23.75   # top-of-key 3 (corners are 22); simple threshold for is3

PINE, SAGE, STONE, EARTH, TEAL, BG, INK = (
    "#1B3C30", "#6E8A7E", "#A39A88", "#7A5E30", "#2E8B72", "#EDEAE0", "#1B3C30")


# ---------- possession ----------
POSSESSION_R = 4.0   # ft: ball within this of a player = that player is in control


def _control_frames(df, off_team=None):
    """Yield (bx, by, control_team) for frames where a player actually controls the
    ball (ball within POSSESSION_R). Filters out loose-ball / defensive-nearest noise
    that flips possession on ~1/10 possessions."""
    for f, g in df.groupby("frame"):
        ball = g[g.is_ball]; pl = g[~g.is_ball]
        if ball.empty or pl.empty:
            continue
        bx, by = ball.iloc[0][["x", "y"]]
        d = np.hypot(pl.x - bx, pl.y - by)
        i = int(np.argmin(d.values))
        if d.values[i] <= POSSESSION_R:
            yield bx, by, int(pl.iloc[i].team)


def detect_offense(df):
    """Offense = team that actually CONTROLS the ball most (not just is nearest)."""
    votes = {}
    for _, _, t in _control_frames(df):
        votes[t] = votes.get(t, 0) + 1
    if not votes:                                  # fallback: nearest-ball, any distance
        for f, g in df.groupby("frame"):
            ball = g[g.is_ball]; pl = g[~g.is_ball]
            if ball.empty or pl.empty:
                continue
            bx, by = ball.iloc[0][["x", "y"]]
            t = int(pl.iloc[int(np.argmin(np.hypot(pl.x - bx, pl.y - by).values))].team)
            votes[t] = votes.get(t, 0) + 1
    if not votes:
        raise ValueError("no possession frames (need ball + players in the same frame)")
    return max(votes, key=votes.get)


def attacking_hoop(df, off_team):
    """Hoop nearest the BALL while the offense controls it. The controlled ball lives
    in the offensive half for the whole possession, so its median is robust to
    transition/odd-spacing frames that broke the offense-median heuristic."""
    ball_ctrl = [(bx, by) for bx, by, t in _control_frames(df) if t == off_team]
    if ball_ctrl:
        bm = np.median(np.array(ball_ctrl), axis=0)
    else:
        bm = df[df.is_ball][["x", "y"]].median().values
    if np.isnan(bm).any():
        return np.array(HOOPS[1])
    return np.array(min(HOOPS, key=lambda h: np.hypot(h[0] - bm[0], h[1] - bm[1])))


# ---------- assignment + beaten index ----------
def _frame_arrays(g, off_team):
    """Return offense/defense as (track_id, name, x, y) tuples — track_id is the
    STABLE key used for temporal voting (positional indices are not stable)."""
    off = g[(~g.is_ball) & (g.team == off_team)]
    dfn = g[(~g.is_ball) & (g.team != off_team)]
    return (list(zip(off.track_id, off.identity, off.x.values, off.y.values)),
            list(zip(dfn.track_id, dfn.identity, dfn.x.values, dfn.y.values)))


def assign(off, dfn, hoop):
    """Hungarian on cost = |defender - expected spot between his man and the hoop|.
    Handles partial rosters (len(off) != len(dfn)): linear_sum_assignment on a
    rectangular matrix returns min(n, m) pairs. Returns {def_track_id: off_track_id}."""
    if not off or not dfn:
        return {}
    C = np.zeros((len(dfn), len(off)))
    for i, (_, _, dx, dy) in enumerate(dfn):
        for k, (_, _, ox, oy) in enumerate(off):
            o = np.array([ox, oy]); e = o + 0.12 * (hoop - o)
            C[i, k] = np.linalg.norm(np.array([dx, dy]) - e)
    ri, ci = linear_sum_assignment(C)
    return {dfn[ri[x]][0]: off[ci[x]][0] for x in range(len(ri))}


def beaten_index(d, o, hoop):
    """0 = contained, 100 = blown by. sep + behind/sideways minus on-the-line credit."""
    u = hoop - o; nu = np.linalg.norm(u) + 1e-6; uu = u / nu
    v = d - o
    proj = float(np.dot(v, uu))                 # + : defender toward hoop (good)
    perp = float(np.linalg.norm(v - proj * uu)) # lateral beat
    sep = float(np.linalg.norm(v))
    openness = sep + max(0, -proj) * 1.6 + perp * 0.9 - max(0, proj) * 0.6
    return float(np.clip(100 / (1 + np.exp(-0.5 * (openness - 6))), 0, 100))


def run(df, smooth_window=12):
    """Returns per-frame list of dicts:
       {frame, off:{tid:(name,x,y)}, dfn:{tid:(name,x,y)},
        pairs:[{def_id, off_id, def_name, off_name, dpos, opos, beaten}], hoop}.

    Temporal smoothing votes on STABLE track_ids (not positional indices), so a
    defender keeps his man through roster changes/occlusion, and partial frames
    contribute instead of being dropped."""
    off_team = detect_offense(df)
    hoop = attacking_hoop(df, off_team)
    frames = sorted(df.frame.unique())
    per = []
    for f in frames:
        off, dfn = _frame_arrays(df[df.frame == f], off_team)
        offpos = {t: (name, x, y) for (t, name, x, y) in off}
        dfnpos = {t: (name, x, y) for (t, name, x, y) in dfn}
        per.append((assign(off, dfn, hoop), offpos, dfnpos))
    out = []
    for n, (_, offpos, dfnpos) in enumerate(per):
        votes = {}
        for k in range(max(0, n - smooth_window), min(len(per), n + smooth_window)):
            for dt, ot in per[k][0].items():
                votes.setdefault(dt, {}).setdefault(ot, 0)
                votes[dt][ot] += 1
        smap = {dt: max(v, key=v.get) for dt, v in votes.items()}
        pairs = []
        for dt, ot in smap.items():
            if dt in dfnpos and ot in offpos:          # both present THIS frame
                dn, dx, dy = dfnpos[dt]; on, ox, oy = offpos[ot]
                b = beaten_index(np.array([dx, dy]), np.array([ox, oy]), hoop)   # vs his man
                shot_dist = float(np.hypot(ox - hoop[0], oy - hoop[1]))
                # contest = the NEAREST defender (who'd actually challenge the shot),
                # not necessarily the assigned man.
                contest = min(np.hypot(ox - ddx, oy - ddy)
                              for (_, ddx, ddy) in dfnpos.values())
                is3 = shot_dist >= THREE_PT_FT
                val = expected_points(shot_dist, contest, is3)   # pts if he shoots now
                pairs.append(dict(def_id=dt, off_id=ot, def_name=dn, off_name=on,
                                  dpos=(dx, dy), opos=(ox, oy), beaten=b,
                                  shot_dist=shot_dist, is3=is3, contest=float(contest),
                                  value=val))
        out.append({"frame": frames[n], "off": offpos, "dfn": dfnpos,
                    "pairs": pairs, "hoop": hoop})
    return out, off_team, hoop
