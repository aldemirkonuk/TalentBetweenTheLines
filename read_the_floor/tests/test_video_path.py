"""End-to-end local spine test for the video path, on the synthetic frames_out fixture.

Proves config -> skalski adapter -> schema -> brain.run -> render.render_gif runs green
on local Python with NO GPU/CV deps. The real Colab frames_out (plan 03) has the same
shape, so the brain/adapter/render run unchanged on real coordinates once it exists.
"""
import os
import sys

# Make read_the_floor importable exactly like run_sportvu.py does.
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import numpy as np

import schema
import brain
import render
from adapters import skalski
from fixtures.frames_out_synthetic import make_frames_out
import basketball_court_config as bcc


def _table(n_frames=30):
    fo = make_frames_out(n_frames)
    per_frame = [skalski.frame_to_rows(i, *t) for i, t in enumerate(fo)]
    return skalski.build_table(per_frame, smooth=True)


def test_court_config_units():
    v = bcc.vertices_ft()
    assert (v[:, 0] >= 0).all() and (v[:, 0] <= 94).all(), "x out of [0,94] (FEET trap)"
    assert (v[:, 1] >= 0).all() and (v[:, 1] <= 50).all(), "y out of [0,50] (FEET trap)"
    for hoop in schema.HOOPS:
        assert any(np.allclose([x, y], hoop) for x, y in v), f"hoop {hoop} missing from config"


def test_adapter_schema():
    df = _table()
    assert schema.validate(df) is True


def test_geometry_sanity():
    df = _table()
    # Asserts ported verbatim from RESEARCH "Phase 1 Requirements -> Test Map".
    assert df[~df.is_ball].x.between(0, 94).all()
    assert df[~df.is_ball].y.between(0, 50).all()
    assert (df.groupby("frame").size() >= 2).mean() > 0.9
    assert df.is_ball.mean() > 0.1
    stable = (df[~df.is_ball].groupby("track_id").frame.count() > len(df.frame.unique()) * 0.5).sum()
    assert stable >= 2


def test_brain_runs():
    df = _table()
    results, off_team, hoop = brain.run(df)
    assert len(results) > 0
    assert any(len(r["pairs"]) > 0 for r in results), "no matchup pairs produced"
    assert any(np.allclose(hoop, h) for h in schema.HOOPS), "attacking hoop not a real hoop"


def test_render_smoke(tmp_path):
    df = _table()
    results, _, _ = brain.run(df)
    out = str(tmp_path / "fixture.gif")
    render.render_gif(results, df, out)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 0
