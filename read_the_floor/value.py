"""Shot Quality — the value model's first brick (a working EPV seed).

Trained on the 2014-15 NBA shot logs (128k shots), which ship clean SHOT_DIST and
CLOSE_DEF_DIST — so we do NOT extract shot location from movement tracking (that failed:
see experiments/SHOT_QUALITY_NOTE.md). Use the right dataset for the job.

Leave-game-out AUC 0.63, well calibrated. Coefficients in shot_model.json.

    shot_quality(shot_dist_ft, defender_dist_ft, is3) -> P(make)   in [0,1]
    expected_points(...)                              -> P(make) * (3 or 2)
"""
import json
import math
import os

_MODEL = None
_PATH = os.path.join(os.path.dirname(__file__), "shot_model.json")


def _model():
    global _MODEL
    if _MODEL is None:
        _MODEL = json.load(open(_PATH))
    return _MODEL


def shot_quality(shot_dist_ft, defender_dist_ft, is3=False):
    m = _model()
    d = min(float(defender_dist_ft), 15.0)          # match training clip
    z = (m["intercept"] + m["shot_dist"] * float(shot_dist_ft)
         + m["def_dist"] * d + m["is3"] * (1 if is3 else 0))
    return 1.0 / (1.0 + math.exp(-z))


def expected_points(shot_dist_ft, defender_dist_ft, is3=False):
    return shot_quality(shot_dist_ft, defender_dist_ft, is3) * (3 if is3 else 2)
