"""The interface contract between any vision pipeline and our brain.

Every source — SportVU tracking OR Skalski's RF-DETR/SAM2 pipeline — gets adapted
into ONE tracking table. The brain only ever reads this schema, so it never knows
or cares where the coordinates came from.

One row per tracked entity per frame.

Columns
-------
frame      int    frame index (monotonic)
time       float  game clock seconds remaining (optional; NaN ok)
team       int    team id; -1 for the ball
track_id   int    stable per-entity id (-1 for the ball)
identity   str    jersey number or player name ('' if unknown)
x          float  court X in feet, 0..94
y          float  court Y in feet, 0..50
is_ball    bool   True for the ball row

Court convention: 94 x 50 ft. Hoops at (5.25, 25) and (88.75, 25).
"""

COLUMNS = ["frame", "time", "team", "track_id", "identity", "x", "y", "is_ball"]
COURT_LEN, COURT_WID = 94.0, 50.0
HOOPS = [(5.25, 25.0), (88.75, 25.0)]


def validate(df):
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"tracking table missing columns: {missing}")
    if not df["is_ball"].any():
        raise ValueError("tracking table has no ball rows (is_ball never True)")
    # one ball per frame, ~10 players per frame is expected but not enforced
    return True
