# Synthesis Summary — Read the Floor ingest

Entry point for `gsd-roadmapper`. Mode: new (net-new bootstrap).
Precedence applied: ADR > SPEC > PRD > DOC.

## Doc counts by type
- Total: 5
- SPEC: 2 — READ_THE_FLOOR.md (p0, authoritative), BODY_AND_ANGLES.md (p1)
- DOC: 3 — STATE.md (p2, live build-status SoT), read_the_floor/VALIDATION.md (p3),
  read_the_floor/SETUP.md (p4)
- ADR: 0 · PRD: 0 · UNKNOWN: 0
- All classifications: confidence high, manifest_override: true.

## Decisions
- Formal ADR decisions: 0 (no ADRs in set; none `locked: true`).
- SPEC-derived spec-locked decisions recorded: 5
  - DEC-pipeline-fork (READ_THE_FLOOR.md)
  - DEC-tracking-schema-contract (READ_THE_FLOOR.md / STATE.md / BODY_AND_ANGLES.md)
  - DEC-matchup-method (READ_THE_FLOOR.md)
  - DEC-anthro-join-not-measure (BODY_AND_ANGLES.md)
  - DEC-possession-by-control (VALIDATION.md / STATE.md)
- Detail: intel/decisions.md

## Requirements
- Extracted: 14 (no PRDs; derived from SPEC feature sets, status cross-checked vs STATE.md)
  - Tier 0 built & validated (7): REQ-tracking-schema, REQ-matchup-engine,
    REQ-beaten-index, REQ-possession-hoop-detection, REQ-shot-quality-value,
    REQ-anthro-join, REQ-top-down-render
  - Tier 1 written-not-proven (1): REQ-video-to-coords
  - Tier 2 spec-only (6): REQ-epv-surface, REQ-points-left/REQ-decision-grade,
    REQ-set-perfectionist, REQ-tell-snitch, REQ-moneyball-vision,
    REQ-body-angles-layer, REQ-reads-suite (grouped backlog)
- Competing acceptance variants: 0
- Detail: intel/requirements.md

## Constraints
- Extracted: 8
  - protocol/dependency: CON-pipeline-stack, CON-data-availability
  - api-contract/schema: CON-schema-contract
  - nfr: CON-anthro-source, CON-pose-feasibility, CON-value-model-scope,
    CON-season-mismatch, CON-possession-edge-cases
- Detail: intel/constraints.md

## Context topics
- Topics: 4 — build status (STATE.md), validation numbers (VALIDATION.md),
  runbook (SETUP.md), cross-reference notes.
- Detail: intel/context.md

## Conflicts
- BLOCKERS: 0
- Competing variants (WARNINGS): 0
- Auto-resolved / INFO: 3 (benign ref cycle, foot length-vs-location near-collision,
  SPEC<->STATE status reconciliation — all consistent, no precedence override needed)
- Full report: .planning/INGEST-CONFLICTS.md

## Status
READY — no blockers, no competing variants. Safe to route to gsd-roadmapper.

## Intel files
- .planning/intel/decisions.md
- .planning/intel/requirements.md
- .planning/intel/constraints.md
- .planning/intel/context.md
- .planning/INGEST-CONFLICTS.md
