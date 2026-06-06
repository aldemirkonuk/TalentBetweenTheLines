# Decisions (ADR intel)

No ADR-type documents were present in this ingest set. The two SPEC documents
(READ_THE_FLOOR.md, BODY_AND_ANGLES.md) carry several architectural choices that
function as locked decisions in practice. They are recorded here as SPEC-derived
decisions so downstream planning preserves them, but none originate from a formal
ADR and none carry `locked: true` at the classification level.

---

## DEC-pipeline-fork
- Source: READ_THE_FLOOR.md
- Origin type: SPEC (precedence 0)
- Status: spec-locked (declared under "LOCKED features")
- Decision: The vision pipeline is a fork of the Skalski / Roboflow "sports" stack:
  RF-DETR (detection + jersey) → SAM2 (tracking) → SigLIP/UMAP/K-Means (zero-shot
  team assignment) → SmolVLM2 (jersey OCR, voted across frames) → keypoints +
  homography (top-down court) → shot detect/classify. The proprietary layer added
  on top: value surface (EPV), risk analysis, X-ray render.
- Scope: computer-vision pipeline architecture

## DEC-tracking-schema-contract
- Source: STATE.md (built), READ_THE_FLOOR.md (spec), BODY_AND_ANGLES.md (extension)
- Origin type: DOC confirms a SPEC-level decision
- Status: built & verified (schema.py)
- Decision: A single tracking-table interface (`read_the_floor/schema.py`) is the one
  contract every data source adapts into. Both the SportVU adapter and the Skalski
  video adapter target it; the Body & Angles pose adapter extends the same contract
  with additional columns rather than a new schema.
- Scope: data interface / adapter boundary

## DEC-matchup-method
- Source: READ_THE_FLOOR.md (FOCUS FIVE #1)
- Origin type: SPEC (precedence 0)
- Status: built & validated (brain.py)
- Decision: Who-Guards-Whom uses optimal defender-assignment (Franks/Bornn 2015):
  each defender's expected anchor is a weighted blend of his man, the ball, and the
  hoop; Hungarian assignment + HMM/temporal smoothing for stable IDs over time.
- Scope: Matchup Engine algorithm

## DEC-anthro-join-not-measure
- Source: BODY_AND_ANGLES.md
- Origin type: SPEC (precedence 1)
- Status: spec-locked decision; anthro join built (anthro.py)
- Decision: Anthropometrics (wingspan, standing reach, hand length/width, height,
  weight, body fat, max vertical) are JOINED by player identity from published
  Draft Combine data — NOT measured from video. Per-moment orientation/pose (foot,
  hip, shoulder angles, knee bend) ARE inferred from video via a pose model
  (RTMPose / COCO-WholeBody). Rule: use pose for angles, Combine for lengths.
- Scope: Body & Angles data sourcing
- Note: BODY_AND_ANGLES.md explicitly recommends DROPPING foot-length as a feature
  (not in Combine data, ~impossible from broadcast). Recorded as a scoping decision.

## DEC-possession-by-control
- Source: read_the_floor/VALIDATION.md (fix), STATE.md (corroborates)
- Origin type: DOC (validation record of an implemented decision)
- Status: built & verified; supersedes prior nearest-player heuristic
- Decision: Possession is inferred from actual ball CONTROL (ball within ~4 ft of a
  player), and the attacking hoop is the hoop nearest the controlled ball's median
  position — replacing the earlier "nearest player" / offense-median heuristic that
  inverted geometry on ~1-in-10 possessions.
- Scope: possession / attacking-hoop inference
