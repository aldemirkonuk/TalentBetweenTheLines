"""Synthetic `frames_out` fixture — the exact 5-tuple shape the skalski adapter consumes.

Lets the whole video spine (config -> adapter -> schema -> brain -> render) be tested on
local Python with NO GPU and NO CV deps (no supervision / rfdetr / sam2). The heavy CV in
Colab (plan 03) produces a real `frames_out` of this same shape; here we fabricate one.

Each frame entry is `(players, ball, transformer, team_by_id, number_by_id)`:
  - players : duck-typed Detections with `.xyxy` (N,4) and `.tracker_id` (N,) int  (NOT None)
  - ball    : duck-typed Detections with `.xyxy` (1,4); `.tracker_id` None
  - transformer : px -> FEET projector (`transform_points`), built from a synthetic
                  pixel court mapped onto BASKETBALL_COURT_VERTICES_FT corners (in feet)
  - team_by_id  : {tracker_id: 0|1}
  - number_by_id: {} (identity tolerated empty by the adapter)

NOTE (documented deviation from 01-01-PLAN Task 2): the plan text says "10 players",
but the plan's own acceptance asserts `df.is_ball.mean() > 0.1`. With one ball row per
frame that fraction is 1/(n_players+1) = 0.091 at 10 players — impossible to satisfy. We
use 8 players (4 per team), giving 1/9 = 0.111 > 0.1, which keeps every literal verify in
plans 01 and 02 green while still exercising the 5-on-... Hungarian assignment, track
stability, and bijection on a synthetic configuration.
"""
import pickle
import numpy as np

import basketball_court_config as bcc


class _Det:
    """Minimal stand-in for supervision.Detections — the adapter never isinstance-checks."""

    def __init__(self, xyxy, tracker_id=None):
        self.xyxy = np.asarray(xyxy, dtype=float)                      # (N, 4)
        self.tracker_id = (None if tracker_id is None
                           else np.asarray(tracker_id, dtype=int))     # (N,) or None

    def __len__(self):
        return len(self.xyxy)


class _FeetTransformer:
    """px -> feet projector. H maps pixel homogeneous coords to court feet.

    Built once from a synthetic pixel court vs the court_config feet corners, so
    `transform_points` returns coordinates in feet (0..94 x 0..50), exactly what the
    skalski adapter and brain expect. Mirrors roboflow/sports ViewTransformer's API.
    """

    def __init__(self, H):
        self.H = np.asarray(H, dtype=float)

    def transform_points(self, pts):
        pts = np.asarray(pts, dtype=float).reshape(-1, 2)
        ones = np.ones((len(pts), 1))
        hom = np.hstack([pts, ones]) @ self.H.T
        return hom[:, :2] / hom[:, 2:3]


def _homography(src, dst):
    """Pure-numpy DLT (no cv2): solve 3x3 H mapping src (N,2) -> dst (N,2), N>=4."""
    src = np.asarray(src, dtype=float)
    dst = np.asarray(dst, dtype=float)
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([-x, -y, -1, 0, 0, 0, x * u, y * u, u])
        A.append([0, 0, 0, -x, -y, -1, x * v, y * v, v])
    _, _, Vt = np.linalg.svd(np.asarray(A, dtype=float))
    H = Vt[-1].reshape(3, 3)
    return H / H[2, 2]


# --- synthetic pixel court (1280x720) mapped to the four feet corners of the court ---
# Image y grows downward, so feet y=0 (baseline) -> larger pixel y. Axis-aligned rect ->
# axis-aligned rect is affine (a valid homography); the box bottom-center round-trips to feet.
_FEET_CORNERS = np.array([(0.0, 0.0), (94.0, 0.0), (94.0, 50.0), (0.0, 50.0)], dtype=float)
_PX_CORNERS = np.array([(100.0, 620.0), (1180.0, 620.0), (1180.0, 100.0), (100.0, 100.0)], dtype=float)
_H_PX2FT = _homography(_PX_CORNERS, _FEET_CORNERS)   # pixel -> feet
_H_FT2PX = np.linalg.inv(_H_PX2FT)                   # feet  -> pixel (to place boxes)


def _ft_to_px(pt_ft):
    """Map a feet point to its pixel position via the inverse homography."""
    x, y = pt_ft
    v = _H_FT2PX @ np.array([x, y, 1.0])
    return v[:2] / v[2]


def _box_from_feet(pt_ft, w_px=20.0, h_px=44.0):
    """Build a pixel box whose BOTTOM-CENTER is the pixel projection of `pt_ft`.

    skalski._feet_xy uses bottom-center ((x1+x2)/2, y2) as the ground-contact point,
    so transform_points(bottom-center) round-trips back to `pt_ft` in feet.
    """
    px, py = _ft_to_px(pt_ft)
    return [px - w_px / 2.0, py - h_px, px + w_px / 2.0, py]


# 8 players (4 per team) at fixed feet anchors inside (5..89, 3..47). Offense = team 0
# (tracker 1-4) near the right side; defense = team 1 (tracker 5-8) between them and the
# right hoop (88.75,25) so the contain geometry is sane.
_BASE_FT = {
    1: (70.0, 25.0), 2: (78.0, 12.0), 3: (78.0, 38.0), 4: (62.0, 20.0),   # team 0 (offense)
    5: (74.0, 24.0), 6: (81.0, 14.0), 7: (81.0, 36.0), 8: (66.0, 21.0),   # team 1 (defense)
}
_TEAM_BY_ID = {1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 1, 7: 1, 8: 1}
_BALL_NEAR = 1   # ball sits ~1.5 ft from this tracker (within brain.POSSESSION_R=4.0)


def make_frames_out(n_frames=30, n_players=8):
    """Return a list of length n_frames; each entry is the adapter's 5-tuple.

    The whole formation drifts slightly and each player oscillates a little so temporal
    smoothing has signal and the Beaten Index varies across the possession.
    """
    ids = sorted(_BASE_FT)[:n_players]
    transformer = _FeetTransformer(_H_PX2FT)
    frames = []
    for f in range(n_frames):
        drift = 0.08 * f                                   # whole formation eases up-court
        boxes, tracker_ids = [], []
        feet_now = {}
        for j, tid in enumerate(ids):
            bx, by = _BASE_FT[tid]
            x = bx + drift
            y = by + 1.2 * np.sin(0.3 * f + j)             # per-player lateral wiggle
            feet_now[tid] = (x, y)
            boxes.append(_box_from_feet((x, y)))
            tracker_ids.append(tid)
        players = _Det(boxes, tracker_id=tracker_ids)

        # ball ~1.5 ft from the ball-handler, present EVERY frame
        hx, hy = feet_now[_BALL_NEAR]
        ball = _Det([_box_from_feet((hx + 1.5, hy), w_px=9.0, h_px=9.0)], tracker_id=None)

        frames.append((players, ball, transformer, dict(_TEAM_BY_ID), {}))
    return frames


def make_frames_out_pickle(path, **kw):
    """Build frames and pickle.dump them — the on-disk shape plan 02 / plan 03 consume."""
    frames = make_frames_out(**kw)
    with open(path, "wb") as fh:
        pickle.dump(frames, fh)
    return path
