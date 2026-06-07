"""Basketball court landmark vertices, expressed in FEET.

Target space is FEET (0..94 x 0..50) to match schema.py. A centimeter or pixel
target silently corrupts brain.POSSESSION_R=4.0 ft — see RESEARCH Pitfall 1. The
roboflow/sports soccer CONFIG uses centimeters; basketball must not.

This file is the homography TARGET array: the `basketball-court-detection-2` keypoint
model emits pixel positions (the `source` array); these feet coordinates are the
`target` array passed to ViewTransformer. Plan 03 confirms the live model's keypoint
count/order in Colab and reorders/subselects this superset to match (apply the same
confidence mask to both source and target — RESEARCH Pitfall 7).

Per CON-schema-contract: this is new seam-support, NOT a schema fork. COURT_LEN/COURT_WID
are restated here (not imported) to avoid an import cycle, but MUST equal schema.py.
"""
import numpy as np

# MUST match schema.py exactly (restated, not imported, to avoid an import cycle).
COURT_LEN, COURT_WID = 94.0, 50.0

# Canonical NBA full-court landmarks in FEET on the 0..94 (x) x 0..50 (y) plane.
# Paint geometry mirrors what render.py draws: left paint (0,17)-(19,33),
# right paint (75,17)-(94,33). Hoops MUST equal schema.HOOPS = (5.25,25),(88.75,25).
# (vertex_xy, name) kept paired so KEYPOINT_NAMES stays in lockstep with the array order.
_LANDMARKS = [
    ((0.0, 0.0),    "corner_left_baseline_bottom"),   # court corner
    ((94.0, 0.0),   "corner_right_baseline_bottom"),  # court corner
    ((94.0, 50.0),  "corner_right_baseline_top"),     # court corner
    ((0.0, 50.0),   "corner_left_baseline_top"),      # court corner
    ((5.25, 25.0),  "hoop_left"),                      # MUST equal schema.HOOPS[0]
    ((88.75, 25.0), "hoop_right"),                     # MUST equal schema.HOOPS[1]
    ((47.0, 0.0),   "midcourt_sideline_bottom"),       # halfcourt line at sideline
    ((47.0, 50.0),  "midcourt_sideline_top"),          # halfcourt line at sideline
    ((0.0, 17.0),   "left_paint_baseline_bottom"),     # left paint rectangle
    ((19.0, 17.0),  "left_paint_ft_bottom"),           # left paint rectangle
    ((19.0, 33.0),  "left_paint_ft_top"),              # left paint rectangle
    ((0.0, 33.0),   "left_paint_baseline_top"),        # left paint rectangle
    ((75.0, 17.0),  "right_paint_ft_bottom"),          # right paint rectangle
    ((94.0, 17.0),  "right_paint_baseline_bottom"),    # right paint rectangle
    ((94.0, 33.0),  "right_paint_baseline_top"),       # right paint rectangle
    ((75.0, 33.0),  "right_paint_ft_top"),             # right paint rectangle
]

BASKETBALL_COURT_VERTICES_FT = np.array([xy for xy, _ in _LANDMARKS], dtype=np.float32)

# Parallel index map (same length/order as BASKETBALL_COURT_VERTICES_FT). Plan 03
# reorders this against the basketball-court-detection-2 model's keypoint output.
KEYPOINT_NAMES = [name for _, name in _LANDMARKS]


def vertices_ft():
    """Return a copy of the court landmark vertices in FEET (shape (K, 2), float32)."""
    return BASKETBALL_COURT_VERTICES_FT.copy()
