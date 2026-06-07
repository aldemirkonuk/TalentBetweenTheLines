"""Adapter: SportVU 2015-16 raw tracking JSON  ->  tracking table (schema.py).

SportVU moment = [quarter, unix_ms, game_clock, shot_clock, _, positions]
positions = [ [ -1, -1, bx, by, bz ],  then 10 x [team_id, player_id, x, y, z] ]
Coordinates are already in court feet (0..94 x 0..50).
"""
import json
import pandas as pd


def event_to_table(json_path, event_index):
    j = json.load(open(json_path))
    ev = j["events"][event_index]
    names = {}
    for side in ("home", "visitor"):
        for p in ev[side]["players"]:
            names[p["playerid"]] = p["lastname"]
    rows = []
    for fi, m in enumerate(ev.get("moments", [])):
        pos = m[5]
        if not pos or len(pos) < 2:        # need at least the ball + one player
            continue
        gc = m[2]
        b = pos[0]                          # ball is always first (team -1)
        rows.append(dict(frame=fi, time=gc, team=-1, track_id=-1,
                         identity="", x=b[2], y=b[3], is_ball=True))
        for p in pos[1:]:                   # emit whatever players are present
            if int(p[0]) == -1:             # skip any extra ball rows
                continue
            rows.append(dict(frame=fi, time=gc, team=int(p[0]), track_id=int(p[1]),
                             identity=names.get(p[1], ""), x=p[2], y=p[3], is_ball=False))
    return pd.DataFrame(rows)
