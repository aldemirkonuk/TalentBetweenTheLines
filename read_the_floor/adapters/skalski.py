"""Adapter: Skalski / Roboflow pipeline output  ->  tracking table (schema.py).

This is the bridge. Skalski's notebook produces, per frame:
  - `players`  : supervision.Detections  (RF-DETR boxes + SAM2 tracker_id)
  - `ball`     : supervision.Detections  (the ball; may be empty some frames)
  - `transformer` : roboflow `sports` ViewTransformer  (image px -> court ft),
                    fit from the court-keypoint model each frame
  - `team_by_id`   : {tracker_id: 0/1}   from SigLIP + K-means
  - `number_by_id` : {tracker_id: '23'}  from SmolVLM2 / ResNet (optional)

We turn each player box into a single ground-contact point (FEET = bottom-center
of the box; use the mask bottom if you have it), project it to court coords, and
emit one row. No separate "feet detector" is needed — feet = bottom of the mask/box.

team ids: we map K-means {0,1} to two stable ints and tag the ball as -1.
"""
import numpy as np
import pandas as pd

# map Skalski's two clusters to stable team ids; ball is always -1
_TEAM = {0: 100, 1: 200}


def _feet_xy(xyxy):
    """Ground-contact point of a box: bottom-center. xyxy = [x1,y1,x2,y2]."""
    x1, y1, x2, y2 = xyxy
    return np.array([(x1 + x2) / 2.0, y2], dtype=float)


def frame_to_rows(frame_idx, players, ball, transformer,
                  team_by_id, number_by_id=None, time=float("nan")):
    """Convert one frame of Skalski outputs into tracking-table rows."""
    number_by_id = number_by_id or {}
    rows = []

    # ball -> single row (centroid bottom is fine; ball has no team)
    if ball is not None and len(ball) > 0:
        bpt = _feet_xy(ball.xyxy[0])
        bx, by = transformer.transform_points(bpt.reshape(1, 2))[0]
        rows.append(dict(frame=frame_idx, time=time, team=-1, track_id=-1,
                         identity="", x=float(bx), y=float(by), is_ball=True))

    # players
    feet = np.array([_feet_xy(b) for b in players.xyxy]) if len(players) else np.empty((0, 2))
    court = transformer.transform_points(feet) if len(feet) else np.empty((0, 2))
    for i in range(len(players)):
        # stable id when SAM2 gives one; otherwise a per-frame-unique NEGATIVE id so
        # smoothing never blends unrelated detections that happen to share index i.
        tid = (int(players.tracker_id[i]) if players.tracker_id is not None
               else -(frame_idx * 100 + i + 2))
        cluster = team_by_id.get(tid, 0)
        rows.append(dict(frame=frame_idx, time=time,
                         team=_TEAM.get(cluster, cluster),
                         track_id=tid,
                         identity=str(number_by_id.get(tid, "")),
                         x=float(court[i][0]), y=float(court[i][1]), is_ball=False))
    return rows


def build_table(per_frame, smooth=True):
    """per_frame: list of row-lists (one per frame) from frame_to_rows().
    Returns a tracking-table DataFrame, optionally Kalman-smoothed per track."""
    df = pd.DataFrame([r for rows in per_frame for r in rows])
    if smooth and len(df):
        df = _smooth_tracks(df)
    return df


def _smooth_tracks(df, alpha=0.4):
    """Light exponential smoothing per track_id to tame extraction jitter.
    (Swap for a proper Kalman filter when you need velocity too.)"""
    out = df.copy().sort_values(["track_id", "frame"])
    for tid, g in out.groupby("track_id"):
        if tid < 0 or len(g) < 3:        # ball (-1), unstable/None ids, or too-short tracks
            continue
        xs, ys = g.x.values.copy(), g.y.values.copy()
        for k in range(1, len(xs)):
            xs[k] = alpha * xs[k] + (1 - alpha) * xs[k - 1]
            ys[k] = alpha * ys[k] + (1 - alpha) * ys[k - 1]
        out.loc[g.index, "x"] = xs
        out.loc[g.index, "y"] = ys
    return out.sort_values(["frame", "track_id"]).reset_index(drop=True)
