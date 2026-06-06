## Conflict Detection Report

Mode: new (net-new bootstrap). Precedence: ADR > SPEC > PRD > DOC.
Ingest set: 5 docs — 2 SPEC (READ_THE_FLOOR.md p0, BODY_AND_ANGLES.md p1),
3 DOC (STATE.md p2, read_the_floor/VALIDATION.md p3, read_the_floor/SETUP.md p4).
No ADR or PRD documents present. No `locked: true` classifications present.

### BLOCKERS (0)

None. No LOCKED-vs-LOCKED ADR contradictions (no ADRs in set). No UNKNOWN /
low-confidence docs (all 5 typed high, manifest_override: true). No reference cycle
exceeded the depth cap. No existing locked context to contradict (new mode).

### WARNINGS (0)

None. No competing acceptance variants. The two SPEC documents cover disjoint scopes:
READ_THE_FLOOR.md owns floor-value, reads, and the FOCUS FIVE; BODY_AND_ANGLES.md owns
the biomechanics layer. Their overlap (the Body & Angles layer) is consistent — the
flagship spec defers to BODY_AND_ANGLES.md by name for that layer. No requirement is
defined twice with divergent acceptance criteria.

### INFO (3)

[INFO] Benign cross-reference cycle: READ_THE_FLOOR.md <-> STATE.md
  Found: READ_THE_FLOOR.md (SPEC, p0) cross_refs STATE.md, and STATE.md (DOC, p2)
    cross_refs READ_THE_FLOOR.md — a 2-node cycle in the reference graph.
  Note: This is a documentation back-citation, not a synthesis dependency. Precedence
    SPEC > DOC breaks it deterministically — READ_THE_FLOOR.md defines intent;
    STATE.md reports current build reality. Synthesis proceeded normally; depth cap
    (50) not approached. No action required.

[INFO] Near-collision (not a conflict): foot LENGTH vs foot LOCATION
  Found: BODY_AND_ANGLES.md recommends DROPPING foot-length as a feature (not in
    Combine data, ~impossible from broadcast). READ_THE_FLOOR.md v2 lists "Feet
    Location (all 10)" as a locked feature.
  Note: These reference different quantities — foot *length* (anthropometric segment,
    dropped) vs foot *position* on the court (top-down coordinate, kept and built).
    No contradiction; recorded for transparency. Both SPECs retained as written.

[INFO] Status reconciliation: SPEC build-status vs STATE.md (consistent)
  Note: READ_THE_FLOOR.md "BUILD STATUS" section and STATE.md agree on what is built
    (schema, Matchup Engine, Beaten Index, possession/hoop, Shot-Quality, anthro join,
    render), written-but-unproven (Skalski video->coords), and spec-only (full EPV,
    Points Left, Set Perfectionist, Tell/Snitch, Moneyball, Body & Angles). No
    precedence override was needed — DOC corroborates SPEC rather than contradicting it.
