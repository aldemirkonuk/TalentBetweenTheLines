# Constraints (SPEC intel)

Constraints extracted from the two SPEC documents (READ_THE_FLOOR.md precedence 0,
BODY_AND_ANGLES.md precedence 1) plus the technical limitations recorded in the DOC
sources (STATE.md, VALIDATION.md). Where a DOC limitation qualifies a SPEC claim,
the SPEC defines the target and the DOC scopes the current honest boundary — no
contradiction; both are kept.

---

## CON-pipeline-stack
- Source: READ_THE_FLOOR.md
- Type: protocol / dependency
- Content: Vision pipeline depends on the Roboflow/Skalski stack — RF-DETR (detection
  + jersey), SAM2 (tracking), SigLIP→UMAP→K-Means (team assignment), SmolVLM2 (jersey
  OCR), keypoints + homography (court mapping). Roboflow Universe datasets required:
  `basketball-player-detection-3-ycjdo`, `basketball-court-detection-2`,
  `basketball-jersey-numbers-ocr`. RF-DETR / SAM2 require a GPU (Colab T4).

## CON-schema-contract
- Source: STATE.md, BODY_AND_ANGLES.md
- Type: api-contract / schema
- Content: All adapters (SportVU, Skalski, pose) MUST emit the single tracking-table
  schema in `read_the_floor/schema.py`. Body & Angles adds optional per-player
  per-frame columns (`foot_angle`, `hip_angle`, `shoulder_angle`, `knee_bend`) and a
  static one-row-per-player `players_anthro.csv` merged by identity — same contract,
  more columns, no schema fork.

## CON-anthro-source
- Source: BODY_AND_ANGLES.md
- Type: nfr / data-sourcing
- Content: Absolute body lengths (wingspan, reach, hand size, vertical) MUST come from
  published Draft Combine data joined by identity, never measured from a single
  broadcast camera (2D foreshortening makes video length-measurement unreliable).
  Orientation/angles are robust from pose and ARE inferred from video. Foot length is
  out of scope (not in Combine, not reliably measurable from broadcast).

## CON-pose-feasibility
- Source: BODY_AND_ANGLES.md
- Type: nfr
- Content: Pose-derived foot keypoints are noisy on wide broadcast angles and cleaner
  on tighter shots; angles (orientation) are the robust signal, not absolute segment
  lengths. Dunk-event detection from video is amber-feasibility.

## CON-value-model-scope
- Source: STATE.md
- Type: nfr
- Content: The value model is "shoot now" only — it uses the nearest defender as the
  contest and distance to the attacking hoop; it does NOT yet weigh passing/driving
  alternatives. Full EPV (pass/drive/turnover) is required to lift this constraint.

## CON-season-mismatch
- Source: STATE.md
- Type: nfr / data
- Content: The value model trains on 2014-15 shot logs while the matchup brain runs on
  2015-16 tracking — acceptable for a model, but it is not a single unified game.

## CON-possession-edge-cases
- Source: VALIDATION.md, STATE.md
- Type: nfr
- Content: Control-based possession/hoop inference is validated on standard half-court
  possessions. PBP-anchored possession remains the gold standard for rare edge cases
  (transition / inbound). `contain_rate` < 1.0 is partly real basketball (help
  defense, gambling), not pure error. Beaten Index should not ship as a trustworthy
  per-possession metric until PBP-anchored possession is in place.

## CON-data-availability
- Source: SETUP.md, READ_THE_FLOOR.md
- Type: data / dependency
- Content: SportVU 2015-16 tracking (top-10 vs top-10 subset, ~55 games locally; 636
  games on GitHub) + PBP outcomes (90,524 possessions) are the training/validation
  base. The Tell/Snitch and Moneyball-for-Vision are data-volume / cross-level
  transfer constrained (thin tracking volume for current players; NBA-trained value
  model may not transfer to HS/college spacing).
