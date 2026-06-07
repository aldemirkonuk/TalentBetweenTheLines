"""Combine anthropometrics -> joined to player identities.

We do NOT measure wingspan/reach/hand size from video — the NBA measures them at the
Draft Combine and publishes them. This module loads that table and joins it to the
players our pipeline identifies, by name, with an honest match report.

Get the combine CSV (run where stats.nba.com is reachable):

    from nba_api.stats.endpoints import draftcombineplayeranthro as A
    A.DraftCombinePlayerAnthro(season_all_time='2015-16').get_data_frames()[0].to_csv('combine.csv')

or hoopR `nba_draftcombineplayeranthro`, or a Kaggle combine dataset.
"""
import re
import unicodedata
import pandas as pd

# canonical output columns (inches / lb)
CANON = ["name", "last", "height_in", "wingspan_in", "standing_reach_in",
         "hand_length_in", "hand_width_in", "weight_lb", "max_vertical_in"]

# tolerant column aliases (NBA stats / Kaggle variants)
ALIASES = {
    "name": ["PLAYER", "PLAYER_NAME", "name", "Player"],
    "height_in": ["HEIGHT_WO_SHOES", "HEIGHT", "height_wo_shoes"],
    "wingspan_in": ["WINGSPAN", "wingspan"],
    "standing_reach_in": ["STANDING_REACH", "standing_reach"],
    "hand_length_in": ["HAND_LENGTH", "hand_length"],
    "hand_width_in": ["HAND_WIDTH", "hand_width"],
    "weight_lb": ["WEIGHT", "weight"],
    "max_vertical_in": ["MAX_VERTICAL_LEAP", "max_vertical", "MAX_VERT"],
}


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()


def _to_inches(v):
    """Accept 84 (in), 7'0'' style, or '84.5'. Returns float inches or NaN."""
    if pd.isna(v):
        return float("nan")
    s = str(v).strip().replace('"', "")
    m = re.match(r"^(\d+)'\s*([\d.]+)?$", s)        # 7' 0.5
    if m:
        return int(m.group(1)) * 12 + (float(m.group(2)) if m.group(2) else 0)
    try:
        return float(s)
    except ValueError:
        return float("nan")


def load_combine(csv_path):
    """Read a combine CSV (any common schema) into the canonical table."""
    raw = pd.read_csv(csv_path)
    out = pd.DataFrame()
    for canon, alts in ALIASES.items():
        col = next((a for a in alts if a in raw.columns), None)
        out[canon] = raw[col] if col else pd.NA
    for c in [c for c in CANON if c.endswith(("_in", "_lb"))]:
        out[c] = out[c].map(_to_inches)
    out["name"] = out["name"].astype(str)
    out["last"] = out["name"].map(lambda n: _norm(n).split()[-1] if _norm(n) else "")
    return out[CANON]


def join(identities, combine_df):
    """identities: list of player names (e.g. SportVU last names) OR a tracking-table
    DataFrame with an 'identity' column. Returns (merged_df, report)."""
    if isinstance(identities, pd.DataFrame):
        names = sorted(set(identities.loc[~identities.is_ball, "identity"]) - {""})
    else:
        names = sorted(set(identities))

    by_last = {}
    for _, r in combine_df.iterrows():
        by_last.setdefault(r["last"], []).append(r)

    rows, matched, unmatched, ambiguous = [], [], [], []
    for nm in names:
        key = _norm(nm).split()[-1] if _norm(nm) else ""
        cands = by_last.get(key, [])
        if len(cands) == 1:
            rows.append({"identity": nm, **{c: cands[0][c] for c in CANON}})
            matched.append(nm)
        elif len(cands) > 1:
            ambiguous.append(nm)            # same last name -> needs first-name/team disambiguation
        else:
            unmatched.append(nm)
    merged = pd.DataFrame(rows)
    report = {"n_players": len(names), "matched": len(matched),
              "match_rate": round(len(matched) / max(1, len(names)), 3),
              "ambiguous": ambiguous, "unmatched": unmatched}
    return merged, report
