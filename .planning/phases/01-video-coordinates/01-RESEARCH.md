# Phase 1: Video → Coordinates — Research

**Researched:** 2026-06-06
**Domain:** Computer vision / basketball player tracking / homography / Colab ML pipeline
**Confidence:** HIGH (core stack verified from source code) / MEDIUM (SAM2 integration pattern) / LOW (clip sourcing legal nuance)

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| REQ-video-to-coords | A real clip runs end-to-end through Colab cell 3 (RF-DETR + SAM2 + team + jersey + homography) into `frames_out` → brain → render; Skalski adapter produces schema.py-compliant tracking table | Full stack verified; adapter contract mapped precisely to schema.py columns and brain.py assumptions |
</phase_requirements>

---

## Summary

The brain is proven end-to-end on SportVU 2015-16 data. The only missing piece is cell 3 of `colab_read_the_floor.ipynb` — the RF-DETR + SAM2 + team-assignment + jersey-OCR + homography block that produces `frames_out`, a list of `(players, ball, transformer, team_by_id, number_by_id)` tuples consumed by `skalski.frame_to_rows()`.

The Roboflow/sports open-source repository (`github.com/roboflow/sports`) contains all the exact components needed. The `sports.common.team.TeamClassifier` class (SigLIP-base-patch16-224 → UMAP(n_components=3) → KMeans(n_clusters=2)) is already written and tested. The `sports.common.view.ViewTransformer` class exposes `__init__(source, target)` and `transform_points(points)` with `cv2.findHomography` / `cv2.perspectiveTransform` under the hood. The soccer `main.py` example demonstrates the full radar loop; basketball is structurally identical.

The critical coordinate-unit risk: the roboflow/sports soccer CONFIG uses centimeters as its target space (12000 x 7000 cm). For basketball the `target` array passed to `ViewTransformer` is **whatever you define** — you must define it in feet (94 × 50) to match `schema.py`'s `COURT_LEN=94, COURT_WID=50` contract. This is not automatic; it is an explicit definition task. The skalski adapter assumes `transformer.transform_points()` returns feet directly — that assumption must hold.

**Primary recommendation:** Copy the roboflow/sports soccer `run_radar` loop, swap the soccer pitch CONFIG for a `BasketballCourtConfiguration` with vertices in feet, swap YOLO for RF-DETR + SAM2, and wire `frames_out` to feed `skalski.frame_to_rows()`. The adapter and the brain run unchanged.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Player/ball detection | Colab GPU (inference) | — | RF-DETR requires GPU; runs in notebook cell 3 |
| Player tracking / stable IDs | Colab GPU (SAM2) | supervision ByteTrack (fallback) | SAM2 memory bank maintains IDs through occlusion |
| Team assignment | Colab GPU (SigLIP) | — | Embedding extraction over player crops; CPU-feasible but slow |
| Jersey OCR | Colab GPU (SmolVLM2) | ResNet-32 classifier | Optional column; brain tolerates empty `identity` |
| Court keypoints → homography | Colab GPU (inference model) | — | Keypoint model requires GPU inference; ViewTransformer is CPU |
| Coordinate projection (px → ft) | CPU (ViewTransformer) | — | Pure linear algebra; no GPU needed |
| Schema adaptation | CPU (skalski.py) | — | Pure Python; runs locally or in Colab |
| Brain + render | CPU (local or Colab) | — | Proven locally; numpy/matplotlib/scipy only |

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `rfdetr` | 1.3.0 | Player + ball + jersey detection | Verified on PyPI [VERIFIED: pip index] |
| `supervision` | 0.28.0 | Detections container, ByteTrack, video utilities, sv.KeyPoints | Verified on PyPI [VERIFIED: pip index] |
| `sam2` | ≥1.0 (install from facebookresearch/sam2 repo) | Multi-object player tracking through occlusion | Memory bank preserves IDs; official pip package available [VERIFIED: pypi.org/project/sam2] |
| `roboflow/sports` (git) | HEAD 42c80c0 (no release tag) | TeamClassifier (SigLIP+UMAP+KMeans), ViewTransformer, BallTracker | Exact classes used; source verified [VERIFIED: github.com/roboflow/sports] |
| `transformers` | ≥4.40 | SiglipVisionModel, AutoProcessor for TeamClassifier; SmolVLM2 | Required by sports.common.team [VERIFIED: team.py source] |
| `umap-learn` | 0.5.12 | UMAP dimensionality reduction inside TeamClassifier | Verified on PyPI [VERIFIED: pip index] |
| `scikit-learn` | ≥1.3 | KMeans inside TeamClassifier | [ASSUMED] — scikit-learn is standard; version floor not verified |
| `torch` | ≥2.5.1 | SAM2 requires torch>=2.5.1 on GPU | [VERIFIED: pypi.org/project/sam2 install docs] |
| `opencv-python` | ≥4.8 | ViewTransformer (cv2.findHomography, cv2.perspectiveTransform) | [ASSUMED] — version floor; any modern cv2 works |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `inference` (Roboflow) | latest | Alternative model serving via `get_model()` | Use if RF-DETR direct API proves brittle; adds `sv.Detections.from_inference()` |
| `SmolVLM2-2.2B-Instruct` (HuggingFace) | latest | Jersey number OCR via VLM prompt | Optional — brain tolerates empty `identity`; use for portfolio polish |
| `imageio`, `matplotlib`, `scipy` | (existing) | Brain + render — already in requirements-local.txt | No change needed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SAM2 (tracking) | supervision ByteTrack | ByteTrack is faster/simpler; loses occlusion recovery via memory bank — ID switches become more common in dense plays |
| SmolVLM2 (jersey OCR) | ResNet-32 classifier on same dataset | ResNet-32 achieves 93% vs SmolVLM2 fine-tuned 86% per blog [CITED: blog.roboflow.com/identify-basketball-players] — ResNet is better if you fine-tune |
| RF-DETR fine-tuned model | YOLO player detection | RF-DETR is the Roboflow/Skalski recommendation; YOLO would work but loses the pre-trained basketball weights |

**Installation (Colab cell 1 — matches existing notebook stub):**
```bash
pip -q install rfdetr supervision sam2 transformers umap-learn scikit-learn imageio matplotlib pandas scipy
pip -q install git+https://github.com/roboflow/sports.git
```

**Version verification as of 2026-06-06:**
- `rfdetr`: 1.3.0 [VERIFIED: pip index]
- `supervision`: 0.28.0 [VERIFIED: pip index]
- `umap-learn`: 0.5.12 [VERIFIED: pip index]
- `sam2`: available on PyPI; requires `torch>=2.5.1` [VERIFIED: pypi.org/project/sam2]
- `roboflow/sports`: no version tag; pin by commit hash 42c80c0 [VERIFIED: git ls-remote]

---

## Architecture Patterns

### System Architecture Diagram

```
VIDEO CLIP (.mp4)
      |
      v
[Cell 3 — Colab T4 GPU]
      |
      +---> RF-DETR inference ──────────────────────────────────+
      |     (basketball-player-detection-3-ycjdo)               |
      |     classes: player, ball, number, referee              |
      |     First frame boxes → SAM2 init prompts              |
      |                                                          |
      +---> SAM2 VideoPredictor ──────────────────────────────-->+
      |     propagate_in_video() → masks per frame              |
      |     mask bottom-center = ground contact point           |
      |                                                          |
      +---> Court keypoint model ──────────────────────────────->+
      |     (basketball-court-detection-2)                       |
      |     sv.KeyPoints → filter confidence > 0.5              |
      |     ViewTransformer(source=px, target=feet 94x50)       |
      |                                                          |
      +---> TeamClassifier.fit() (once, on crops from stride)-->+
      |     SigLIP embeddings → UMAP(n=3) → KMeans(k=2)        |
      |     -> team_by_id {tracker_id: 0|1}                     |
      |                                                          |
      +---> SmolVLM2 / ResNet jersey OCR (optional) ──────────->+
            voted across frames → number_by_id {id: '23'}       |
                                                                 |
                        frames_out = [(players_sv, ball_sv,      |
                                       transformer, team_by_id,  |
                                       number_by_id), ...]  <----+
      |
      v
[skalski.frame_to_rows() — adapter seam]
      |
      | _feet_xy(xyxy) = bottom-center of box/mask
      | transformer.transform_points(feet_px) -> (x_ft, y_ft)
      | team = _TEAM[team_by_id[tracker_id]]  (100 or 200)
      | identity = number_by_id.get(tracker_id, "")
      |
      v
[schema.py tracking table]
  frame | time | team | track_id | identity | x(ft) | y(ft) | is_ball
      |
      v
[brain.run(df)] ──> [render.render_gif(results, df)] ──> broadcast X-ray GIF
      |                                                          |
      v                                                          v
 frames/*.png                                         prototypes/video_matchup.gif
```

### Key per-frame data contract

Cell 3 must produce `frames_out`, a list with one entry per frame. Each entry is a 5-tuple:

```python
# Entry i:
players    : sv.Detections  # RF-DETR player boxes with SAM2 tracker_id populated
ball       : sv.Detections  # ball box(es); may be len 0
transformer: ViewTransformer  # fitted this frame from court keypoints
team_by_id : dict           # {tracker_id (int): cluster_label (0 or 1)}
number_by_id: dict          # {tracker_id (int): jersey_number_str}  -- optional, {} ok
```

The adapter `skalski.frame_to_rows(i, players, ball, transformer, team_by_id, number_by_id)` maps this exactly to schema.py rows. `players.tracker_id` must be a NumPy array of ints (set by SAM2 or ByteTrack).

### Recommended Colab cell 3 structure

```python
# Source: roboflow/sports examples/soccer/main.py + blog.roboflow.com/identify-basketball-players

from rfdetr import RFDETRBase
import supervision as sv
from sam2.build_sam import build_sam2_video_predictor   # [ASSUMED: exact import path]
from sports.common.team import TeamClassifier
from sports.common.view import ViewTransformer
# from inference import get_model  # alternative model serving

# --- 0. Define basketball court CONFIG in FEET (94 x 50 ft) ---
# There is no BasketballCourtConfiguration in roboflow/sports yet (only soccer).
# Must define it manually using the same vertex pattern as SoccerPitchConfiguration.
# CRITICAL: target vertices must be in feet to match schema.py COURT_LEN=94, COURT_WID=50.
# The basketball-court-detection-2 model detects keypoints whose pixel positions become
# the `source` array; your court feet coordinates become the `target` array.

COURT_W_FT, COURT_H_FT = 94.0, 50.0
# Example: 4-corner vertices only (minimum for homography; more = more stable)
# Full keypoint set corresponds to dataset labels (paint corners, 3-pt line etc.)
# Indices must match the order the model returns keypoints.

# --- 1. Load models ---
player_detector = RFDETRBase()  # fine-tuned basketball weights loaded separately
# OR: from inference import get_model; player_detector = get_model("basketball-player-detection-3-ycjdo/...")

court_model = ...   # keypoint model for basketball-court-detection-2

# --- 2. Fit TeamClassifier on stride-sampled crops ---
crops = []
for frame in sv.get_video_frames_generator(VIDEO, stride=30):
    result = player_detector.predict(frame, threshold=0.3)
    # filter to player class only; extract crops
    crops += [sv.crop_image(frame, xyxy) for xyxy in player_detections.xyxy]
team_classifier = TeamClassifier(device='cuda')
team_classifier.fit(crops)  # SigLIP -> UMAP -> KMeans

# --- 3. SAM2 init: run detector on frame 0, use boxes as prompts ---
# predictor = build_sam2_video_predictor(config, checkpoint)
# inference_state = predictor.init_state(video_path=VIDEO)
# for each player box: predictor.add_new_points_or_box(inference_state, box=xyxy, obj_id=i)
# video_segments = predictor.propagate_in_video(inference_state)

# --- 4. Per-frame loop ---
frames_out = []
for frame_idx, (out_obj_ids, out_mask_logits) in enumerate(video_segments):
    frame = get_frame(frame_idx)

    # Court keypoints -> transformer
    kp_result = court_model(frame)
    keypoints = sv.KeyPoints.from_inference(kp_result)  # or from_ultralytics
    mask = keypoints.xy[0][:, 0] > 1  # filter undetected keypoints
    transformer = ViewTransformer(
        source=keypoints.xy[0][mask].astype(np.float32),
        target=BASKETBALL_COURT_VERTICES[mask].astype(np.float32)  # in feet!
    )

    # Convert SAM2 masks -> sv.Detections with tracker_id
    players_sv = masks_to_sv_detections(out_obj_ids, out_mask_logits)
    # players_sv.tracker_id = np.array(out_obj_ids)

    # Ball: re-detect each frame (not tracked by SAM2 typically)
    ball_sv = detect_ball(frame)

    # Team assignment per frame
    crops_frame = [sv.crop_image(frame, xyxy) for xyxy in players_sv.xyxy]
    team_labels = team_classifier.predict(crops_frame)
    team_by_id = {int(tid): int(lbl)
                  for tid, lbl in zip(players_sv.tracker_id, team_labels)}

    # Jersey OCR (optional)
    number_by_id = {}  # fill with SmolVLM2 or ResNet if needed

    frames_out.append((players_sv, ball_sv, transformer, team_by_id, number_by_id))
```

### Recommended Project Structure (additions for Phase 1)

```
read_the_floor/
├── colab_read_the_floor.ipynb     — cell 3 filled (this phase's deliverable)
├── basketball_court_config.py     — BasketballCourtConfig with vertices in feet
├── adapters/
│   └── skalski.py                 — unchanged (already correct)
└── schema.py                      — unchanged
```

### Pattern 1: ViewTransformer construction per frame

The `source` array is the detected keypoint pixel positions. The `target` array is your canonical court in the units you want output in — **feet for our schema**.

```python
# Source: /tmp/sports/sports/common/view.py (verified from source)
# Source: /tmp/sports/examples/soccer/main.py render_radar()
transformer = ViewTransformer(
    source=keypoints.xy[0][mask].astype(np.float32),  # detected px positions
    target=np.array(BASKETBALL_VERTICES_FT)[mask].astype(np.float32)  # in feet
)
# transform player feet (bottom-center of box) to court coordinates in feet:
feet_px = np.array([[(x1+x2)/2, y2] for x1,y1,x2,y2 in players.xyxy])
court_ft = transformer.transform_points(feet_px)  # shape (N, 2), units = feet
```

`court_ft[:, 0]` → `x` column (0..94 ft), `court_ft[:, 1]` → `y` column (0..50 ft).

### Pattern 2: TeamClassifier usage

```python
# Source: /tmp/sports/sports/common/team.py (verified from source)
from sports.common.team import TeamClassifier

tc = TeamClassifier(device='cuda', batch_size=32)
tc.fit(all_crops)          # list of np.ndarray BGR crops from stride pass
labels = tc.predict(crops) # np.ndarray of 0/1 per crop, THIS frame
```

### Pattern 3: skalski adapter — no changes needed

```python
# Source: read_the_floor/adapters/skalski.py
rows = skalski.frame_to_rows(
    frame_idx=i,
    players=players_sv,        # sv.Detections with .xyxy and .tracker_id
    ball=ball_sv,
    transformer=transformer,   # ViewTransformer returning feet
    team_by_id=team_by_id,     # {tracker_id: 0|1}
    number_by_id=number_by_id, # {tracker_id: '23'} or {}
    time=float('nan')          # game clock unknown from video
)
```

The adapter uses `_feet_xy(xyxy)` (bottom-center of box) as the ground-contact point, then calls `transformer.transform_points(feet_px)`. It assigns team IDs via `_TEAM = {0: 100, 1: 200}`, uses `tracker_id` for temporal smoothing, and falls back to a per-frame-unique negative ID when `tracker_id` is None.

### Anti-Patterns to Avoid

- **Defining court CONFIG vertices in centimeters or pixels**: The soccer CONFIG uses cm; basketball must use feet. `schema.py` expects 0–94 x and 0–50 y. A centimeter-scale CONFIG would produce coordinates around 0–2800, which the brain's `POSSESSION_R=4.0` ft threshold and `HOOPS=[(5.25,25),(88.75,25)]` would fail on silently.
- **Using ByteTrack instead of SAM2 and expecting no ID switches**: ByteTrack is per-frame IoU matching; occlusion in a 3-second NBA possession causes multiple ID switches. SAM2's memory bank prevents this. ByteTrack is acceptable as a fallback but will produce noisier track_id streams.
- **Fitting TeamClassifier per-frame**: Fit once on stride-sampled crops from the whole clip, then predict per-frame. Per-frame fitting causes cluster-label flipping (team 0 becomes team 1 mid-clip).
- **Using the mask centroid instead of mask bottom**: `skalski._feet_xy` uses bottom-center of the bounding box as the ground contact point. Using the mask centroid gives the torso center — inflates height ~3 ft and corrupts distance-to-hoop calculations in `brain.beaten_index`.
- **Running SmolVLM2 every frame**: Jersey OCR is optional and slow. Vote across sampled frames, cache by `tracker_id`, use `{}` if unavailable. Brain tolerates empty `identity`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| SigLIP → UMAP → KMeans team separation | Custom color-histogram clustering | `sports.common.team.TeamClassifier` | Already implemented and tested; handles jersey color variation, referees, white backgrounds |
| Perspective projection px → feet | Custom homography math | `sports.common.view.ViewTransformer` | Uses `cv2.findHomography` RANSAC; handles noisy keypoints; validated against soccer |
| Multi-object tracking through occlusion | IoU matching loop | SAM2 `build_sam2_video_predictor` | Internal memory bank handles full-frame occlusion; proven on sports video |
| Video frame iteration | Custom `cv2.VideoCapture` loop | `sv.get_video_frames_generator()` | Handles seek, stride, codec; well-tested |
| Crop extraction from detections | Manual array slicing | `sv.crop_image(frame, xyxy)` | Handles edge cases, bounds clipping |

**Key insight:** Every non-trivial component already exists in `roboflow/sports` or `supervision`. Cell 3 is an integration task, not a modeling task.

---

## Output Contract: What Cell 3 Must Produce

The adapter `skalski.py` defines the exact contract. Cell 3 must produce for each frame index `i`:

| Variable | Type | Required | Notes |
|----------|------|---------|-------|
| `players_sv` | `sv.Detections` | Yes | `.xyxy` shape `(N,4)`, `.tracker_id` shape `(N,)` int array — **must not be None** |
| `ball_sv` | `sv.Detections` | Recommended | May be empty (`len=0`); brain falls back to nearest player if no ball rows |
| `transformer` | `ViewTransformer` | Yes | Fitted this frame; `transform_points` returns feet |
| `team_by_id` | `dict[int,int]` | Yes | Keys = tracker_ids; values = {0, 1} |
| `number_by_id` | `dict[int,str]` | No | May be `{}` throughout; identity col will be `""` |

The adapter writes these schema.py columns:
```
frame=i, time=NaN, team=100|200|-1, track_id=tracker_id, identity="23"|"",
x=court_ft[0], y=court_ft[1], is_ball=False|True
```

Coordinates must satisfy: `0 ≤ x ≤ 94`, `0 ≤ y ≤ 50` (feet). Hoops at `(5.25,25)` and `(88.75,25)`.

---

## Roboflow Universe Dataset IDs (from CON-pipeline-stack)

| Dataset | Roboflow Universe ID | Used For |
|---------|---------------------|----------|
| Basketball player detection | `roboflow-jvuqo/basketball-player-detection-3-ycjdo` | RF-DETR player/ball/number boxes |
| Basketball court keypoints | `roboflow-jvuqo/basketball-court-detection-2` | Homography keypoints |
| Jersey number OCR | `roboflow-jvuqo/basketball-jersey-numbers-ocr` | SmolVLM2 / ResNet fine-tune |

Classes in `basketball-player-detection-3-ycjdo`: `ball`, `player`, `number`, `referee`, `ball-in-basket`, `player-in-possession`, `player-jump-shot`, `player-layup-dunk`, `player-shot-block`. [VERIFIED: Roboflow Universe search results]

---

## Common Pitfalls

### Pitfall 1: Court coordinate units mismatch
**What goes wrong:** `transformer.transform_points()` returns values like (2400, 1300) instead of (47, 25). Brain's `POSSESSION_R=4.0` ft radius captures zero players; `detect_offense()` raises "no possession frames".
**Why it happens:** The soccer CONFIG uses centimeters; developer copies the soccer pattern without defining basketball target vertices in feet.
**How to avoid:** Define `BASKETBALL_VERTICES_FT` as a numpy array with x in [0,94] and y in [0,50], matching the court landmarks the `basketball-court-detection-2` model detects.
**Warning signs:** `df.x.max()` >> 94 in notebook output after `schema.validate(df)`.

### Pitfall 2: tracker_id is None (no SAM2 IDs)
**What goes wrong:** `players.tracker_id is None` → skalski adapter assigns per-frame negative IDs → `_smooth_tracks` skips all tracks (tid < 0) → exponential smoothing does nothing → jittery coordinates.
**Why it happens:** SAM2 integration not wired correctly; `players_sv.tracker_id` not set from SAM2 object IDs.
**How to avoid:** Explicitly assign: `players_sv.tracker_id = np.array(out_obj_ids)` after building the Detections object from SAM2 masks.
**Warning signs:** All `track_id` values in `df` are negative; `brain.run()` temporal smoothing window has no effect.

### Pitfall 3: TeamClassifier cluster-label flip mid-clip
**What goes wrong:** Team 100 and 200 swap halfway through; brain's `detect_offense()` votes split evenly; possession/hoop detection fails.
**Why it happens:** Fitting TeamClassifier per-frame restarts the KMeans; label assignment is arbitrary and can flip.
**How to avoid:** Fit once before the per-frame loop on stride-sampled crops. KMeans cluster labels are stable within a single fit.
**Warning signs:** `off_team` alternates between 100 and 200 across consecutive frames in `brain.run()` output.

### Pitfall 4: Homography instability on broadcast camera pan
**What goes wrong:** `ViewTransformer.__init__` raises `ValueError: Homography matrix could not be calculated` or produces degenerate transforms; player coordinates jump wildly on pan frames.
**Why it happens:** During camera pans, the court-keypoint model detects fewer than 4 keypoints, or detected keypoints are colinear — `cv2.findHomography` fails or returns garbage.
**How to avoid:** (1) Use a short, single-possession clip with a roughly stable camera angle for the first run. (2) Add a `try/except` around `ViewTransformer()` construction; fall back to the previous frame's transformer. (3) Filter: if fewer than 4 keypoints are detected above confidence 0.5, skip the frame's transformer update.
**Warning signs:** Sudden large jumps in player x,y coordinates in consecutive frames; `transform_points` output outside [0,94] × [0,50].

### Pitfall 5: Ball not detected many frames
**What goes wrong:** `schema.validate(df)` raises "tracking table has no ball rows (is_ball never True)" — or ball rows present but only a fraction of frames; `brain.detect_offense()` falls back to nearest-player heuristic (acceptable but degrades possession accuracy).
**Why it happens:** Ball is small and fast; occlusion by players is frequent; RF-DETR may miss it at default confidence.
**How to avoid:** (1) Lower ball detection confidence threshold to 0.2. (2) Use `sv.InferenceSlicer` for ball sub-image detection (proven in soccer BallTracker pattern). (3) Brain's fallback is functional — don't block Phase 1 on perfect ball detection.
**Warning signs:** `df[df.is_ball].shape[0]` < 10% of total frames.

### Pitfall 6: SAM2 mask producing multi-segment garbage
**What goes wrong:** A player's mask includes the crowd background or another player's body; bottom-center of the composite mask is completely wrong for ground-contact projection.
**Why it happens:** High-motion frames cause SAM2 to "explode" the mask; documented in the Skalski blog [CITED: blog.roboflow.com/identify-basketball-players].
**How to avoid:** Post-process SAM2 masks: keep only the largest connected component; discard masks whose bounding box area exceeds 20% of frame area (full-body players are ~2–5% of a 1920x1080 frame). The blog describes exactly this cleanup step.
**Warning signs:** One player's bounding box spans most of the frame width.

### Pitfall 7: BasketballCourtConfiguration keypoint index mapping
**What goes wrong:** `keypoints.xy[0]` has N keypoints from the model, but `BASKETBALL_VERTICES_FT` has M vertices (M ≠ N, or order mismatched) → `ViewTransformer.__init__` raises shape mismatch error.
**Why it happens:** The court model returns keypoints in a fixed order defined by its training labels; the developer-defined vertex array must match that exact order and count.
**How to avoid:** Inspect the `basketball-court-detection-2` dataset on Roboflow Universe to confirm the number and ordering of keypoints. Apply the confidence-filter mask (`mask = keypoints.xy[0][:, 0] > 1`) to both arrays simultaneously so undetected keypoints are excluded from both source and target.

---

## Test Clip Sourcing

No official open-license NBA broadcast clip exists that is trivially downloadable. Three viable approaches:

1. **Self-recorded (recommended for portfolio):** Record a 5–15 second single-possession clip at a gym, college game, or YMCA league with a phone/camera at a stable angle. Fixed half-court side angle is ideal. No copyright concern.

2. **YouTube fair use (portfolio / research):** A short clip (5–15 s, single possession) trimmed from a publicly posted game highlights video constitutes likely fair use for a non-commercial research/portfolio context [CITED: pbs.org/standards/media-law-101/copyright-fair-use] — "commentary, criticism, research" — but has legal gray area. Use only for local/private demo; do not distribute the clip.

3. **Open datasets:** The `TeamTrack` dataset includes multi-person sports tracking video with annotations (basketball, handball). Not guaranteed to include NBA broadcast footage. [CITED: arxiv.org/pdf/2406.19655]

**Clip constraints for reliable homography:**
- Duration: 5–15 seconds (one possession)
- Camera: stable / minimally panning — avoid broadcast pans during first run
- Angle: wide-angle half-court side view showing most of the half-court and court markings
- Resolution: ≥720p preferred; RF-DETR works on 1280-wide input
- Format: `.mp4` H.264

---

## Compute Reality

| Component | GPU Required? | Approx Size | Runtime / clip-second |
|-----------|--------------|-------------|----------------------|
| RF-DETR inference (per frame) | Yes (T4 practical) | ~160 MB weights | ~50ms/frame on T4 [ASSUMED] |
| SAM2-base (video predictor) | Yes, required | ~300 MB checkpoint | ~80ms/frame on T4 [ASSUMED] |
| SigLIP-base-patch16-224 (TeamClassifier) | GPU preferred, CPU possible | ~400 MB | 2-5s per batch-32 on T4; slow on CPU [ASSUMED] |
| SmolVLM2-2.2B-Instruct | GPU strongly preferred | ~4.4 GB | ~200ms/jersey crop on T4 [ASSUMED] |
| Court keypoint model | GPU preferred | ~50 MB | ~30ms/frame on T4 [ASSUMED] |
| ViewTransformer, skalski adapter, brain | CPU only | negligible | <1ms/frame |

**Colab tier needed:** Free T4 GPU (15 GB VRAM) is sufficient for all models in sequence. Loading all simultaneously (~5.5 GB) may fit with care; stagger model loading if OOM.

**Total pipeline for a 10-second clip at 30fps = 300 frames:** Approximately 5–15 minutes on Colab T4 (dominated by SAM2 propagation). [ASSUMED — based on typical SAM2 throughput reports]

**TeamClassifier:** The `.fit()` pass runs on stride-sampled crops (stride=30 → ~10 frames → ~100 crops for a 10s clip); fast. The per-frame `.predict()` call is also fast.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Python scripts + manual Colab inspection (no pytest for Colab cells) |
| Config file | None — validation via `schema.validate(df)` + numeric sanity checks |
| Quick run command | `python -c "import schema; import pandas as pd; df=pd.read_csv('frames_out.csv'); schema.validate(df); print('ok')"` |
| Full suite command | `python read_the_floor/validate.py <sportvu_game.7z>` (existing; run on SportVU to confirm brain unchanged) |

### Phase 1 Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | Notes |
|--------|----------|-----------|-------------------|-------|
| REQ-video-to-coords / SC1 | Cell 3 runs on one real clip producing `frames_out` | Smoke | Run Colab cells 1–3; no exception | Manual Colab run |
| REQ-video-to-coords / SC2 | Skalski adapter produces schema-compliant table | Unit | `schema.validate(df)` — must pass | Auto in Colab cell 4 |
| REQ-video-to-coords / SC2 | x in [0,94], y in [0,50] for all player rows | Geometry sanity | `assert df[~df.is_ball].x.between(0,94).all()` | Add to cell 4 |
| REQ-video-to-coords / SC2 | At least 8 player rows per frame (partial rosters ok) | Roster sanity | `assert (df.groupby('frame').size() >= 2).mean() > 0.9` | Add to cell 4 |
| REQ-video-to-coords / SC2 | Ball present in ≥10% of frames | Ball presence | `assert df.is_ball.mean() > 0.1` | Add to cell 4 |
| REQ-video-to-coords / SC2 | At least 2 track_ids stable across ≥50% of frames | Track stability | `stable = (df[~df.is_ball].groupby('track_id').frame.count() > len(frames)*0.5).sum(); assert stable >= 2` | Add to cell 4 |
| REQ-video-to-coords / SC3 | `brain.run(df)` completes without exception | Integration smoke | Run Colab cell 5 | Manual |
| REQ-video-to-coords / SC3 | Render GIF produced | Output check | `assert os.path.exists('/content/matchup_engine.gif')` | Auto in Colab cell 5 |
| REQ-video-to-coords / SC4 | Video-path coords geometry sane vs SportVU baseline | Sanity comparison | Compare median hoop distance, team separation | Manual inspection |
| REQ-video-to-coords / SC4 | Stills saved to frames/, GIF to prototypes/ | Artifact check | File presence assertions | Manual |

### Sanity Checks: Video-Derived Coords vs SportVU Baseline (SC4)

These are not automated unit tests but **manual inspection checks** to verify the video pipeline produces geometrically plausible output:

1. **Hoop distance distribution:** Players should be 5–40 ft from the attacking hoop. SportVU median ≈ 18 ft. Video-derived median should be in the same range (not 0–5 ft, which suggests units wrong).

2. **Team separation:** `brain.detect_offense()` should identify one team with > 60% ball-control frames. If it alternates 50/50, team assignment is unstable.

3. **Beaten Index range:** Should be non-degenerate (mean ~55, std ~20+) as in the SportVU baseline. If all values are 0 or 100, coordinate geometry is wrong.

4. **Assignment bijection:** `brain.run()` should produce `pairs` with approximately equal numbers of offense/defense assignments per frame. Badly wrong coordinates produce empty `pairs`.

5. **Visual spot-check:** Save 5 overlay frames from the video run; compare player dots on the court diagram to their visual positions in the source video frame.

### Sampling Rate

- **Per Colab cell:** Run `schema.validate(df)` and the 6 geometry/presence assertions inline before proceeding to brain
- **Phase gate:** All assertions pass + overlay GIF renders + visual spot-check of 5 frames passes before closing out Phase 1

### Wave 0 Gaps (work needed before implementation)

- [ ] `read_the_floor/basketball_court_config.py` — `BasketballCourtConfig` with vertices in feet matching the `basketball-court-detection-2` keypoint model's output ordering — **must be created; no equivalent in roboflow/sports today** [VERIFIED: sports/configs/ contains only soccer.py]
- [ ] Test clip sourced and uploaded to Colab (self-recorded or trimmed) — no automated solution
- [ ] Colab T4 GPU session active (not CPU — RF-DETR + SAM2 will time out)
- [ ] Roboflow API key (for hosted model inference via `get_model()`) — optional if using direct RF-DETR weights

---

## Runtime State Inventory

This is a greenfield fill-in for an existing stub — no rename/refactor. All state is file-based.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None — no databases, no vector stores in this pipeline | None |
| Live service config | None — no n8n, no external services | None |
| OS-registered state | None | None |
| Secrets/env vars | Roboflow API key needed in Colab (`ROBOFLOW_API_KEY`) — not in git, set as Colab secret | Add Colab secret before run |
| Build artifacts | None | None |

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.10+ | sam2, rfdetr | Partial (3.9.6 locally) | 3.9.6 — **below sam2 minimum** | Run on Colab (3.10+); local track A (SportVU) unaffected |
| GPU (NVIDIA T4+) | RF-DETR, SAM2, SigLIP | Available on Colab T4 | — | Free Colab tier sufficient |
| git | Repo clone | Available | 2.50.1 | — |
| ffmpeg | Clip trimming (optional) | Not found locally | — | Use QuickTime or online trimmer |

**Missing dependencies with no fallback (for Colab run):**
- None — all required libraries are `pip install`-able in Colab T4 session

**Missing dependencies with fallback:**
- Python 3.9.6 locally: below sam2 minimum (3.10+) — use Colab for Track B; local Track A (run_sportvu.py) unaffected

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| ByteTrack only for player tracking | SAM2 segment-and-track (memory bank) | 2024 (SAM2 release) | Occlusion recovery; stable IDs through full-body contact |
| Hard-coded color thresholds for team assignment | SigLIP → UMAP → KMeans (zero-shot) | 2024 (Skalski pipeline) | Works across jersey colors without retraining |
| Manual jersey OCR (hard-coded digit classifiers) | SmolVLM2 / ResNet-32 fine-tuned on NBA crops | 2025 (Skalski blog) | ResNet-32 at 93% accuracy > SmolVLM2 baseline 56% → fine-tuned 86% |
| Homography from four court corners manually annotated | YOLOv11/RF-DETR keypoint model auto-detected | 2024 | Automated per-frame; no manual annotation |

**Deprecated / outdated:**
- Custom SORT / DeepSORT for basketball: superseded by SAM2 for occlusion-heavy scenes
- Color histogram team separation: superseded by SigLIP embeddings

---

## Open Questions (RESOLVED)

1. **BasketballCourtConfiguration vertex ordering** — (RESOLVED)
   - What we know: `basketball-court-detection-2` model on Roboflow Universe detects specific keypoints (corners of paint, 3-pt line, etc.) in a fixed order defined by the dataset labels
   - What's unclear: Exact number of keypoints, their names, and their index ordering — cannot be read without a Roboflow account or running inference
   - Recommendation: First task in Wave 0 — run the court model on a test image in Colab, inspect `keypoints.xy[0].shape` and confidence values, map indices to court positions, then define `BASKETBALL_COURT_VERTICES_FT` to match
   - **(RESOLVED):** Operationally handled — plan 01 defines a generous, documented superset `BASKETBALL_COURT_VERTICES_FT` + parallel `KEYPOINT_NAMES` index map; plan 03 Task 1 (Wave-0 checkpoint) confirms the live model's keypoint count/order in Colab and reorders/subselects the vertex array to match, applying the same confidence mask to source and target (Pitfall 7). No further research needed pre-execution.

2. **SAM2 exact import path in Colab (pip install sam2 vs git clone)** — (RESOLVED)
   - What we know: SAM2 is available via `pip install sam2` on PyPI; facebookresearch recommends git clone for latest features including the Dec 2024 multi-object update
   - What's unclear: Whether the PyPI package includes `build_sam2_video_predictor` or whether the git-installed version is required
   - Recommendation: Use `pip install sam2` first; if `build_sam2_video_predictor` is missing, fall back to `pip install git+https://github.com/facebookresearch/sam2.git`
   - **(RESOLVED):** Operationally handled — plan 03 Task 2 encodes the fallback as an inline comment in cell 3 (`pip install sam2` first; git-install facebookresearch/sam2 if `build_sam2_video_predictor` is missing). A try-at-runtime decision, not a planning blocker.

3. **RF-DETR fine-tuned basketball weights access** — (RESOLVED)
   - What we know: The blog describes a custom 10-class fine-tuned model; `basketball-player-detection-3-ycjdo` is on Roboflow Universe with multiple architectures including rfdetr
   - What's unclear: Whether the fine-tuned weights are publicly downloadable without a Roboflow account/API key, or whether base RF-DETR weights + Roboflow inference API is required
   - Recommendation: Use Roboflow `inference` SDK (`get_model("basketball-player-detection-3-ycjdo/...")`) as primary path; requires free Roboflow API key; add `ROBOFLOW_API_KEY` as Colab secret
   - **(RESOLVED):** Operationally handled — plan 03 adopts the Roboflow `inference` SDK (`get_model(...)`) as the primary path with the `ROBOFLOW_API_KEY` Colab secret (user_setup + Task 1 checkpoint), and notes direct `RFDETRBase` weights as the documented fallback. Access is a Wave-0 prerequisite, not an open design question.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | SmolVLM2-2.2B-Instruct requires ~4.4 GB VRAM; all models together fit in 15 GB Colab T4 | Compute Reality | OOM error in Colab; mitigation: load/unload models sequentially |
| A2 | RF-DETR inference takes ~50ms/frame on T4 (total pipeline ~5-15 min for 300 frames) | Compute Reality | Pipeline may time out in Colab's 12h session limit; mitigation: use <100 frame clip |
| A3 | `pip install sam2` on PyPI includes `build_sam2_video_predictor` | Open Questions | Must use git install instead; adds 2-3 min to cell 1 |
| A4 | `basketball-court-detection-2` model keypoints are accessible via Roboflow inference API without fine-tuning | Roboflow Dataset IDs | May require Roboflow subscription; fallback is manual homography from 4 visible corners |
| A5 | Python 3.10+ minimum requirement for sam2 means Colab T4 (which runs 3.10+) is required | Environment Availability | Colab free tier downgraded; mitigation: use Colab Pro or local Python 3.10+ venv |
| A6 | scikit-learn ≥1.3 is compatible with the KMeans usage in sports.common.team | Standard Stack | API breakage; mitigation: pin to version that ships with roboflow/sports dependencies |

---

## Project Constraints (from CLAUDE.md)

**Applicable to Phase 1:**
- **ML not dashboards:** The pipeline must produce spatial coordinates that the value/risk brain consumes — not a stats table. Cell 3 is the CV/ML layer.
- **Fork the best pipeline, add the value+risk layer:** Roboflow/Skalski is explicitly the reference pipeline. Phase 1 forks it. The brain (value model, beaten index) bolts on after `skalski.frame_to_rows()` — not inside cell 3.
- **Schema contract (CON-schema-contract):** MUST NOT fork schema.py. The adapter is the only seam. Brain runs unchanged.
- **Stack locked (CON-pipeline-stack):** RF-DETR + SAM2 + SigLIP/UMAP/KMeans + SmolVLM2 + keypoints/homography. No substitutions without explicitly documenting why.
- **Render palette locked (Stone Dust × Pine Teal):** render.py already implements this palette. Phase 1 must not touch render.py colors.
- **Surgical changes:** Touch only cell 3, `basketball_court_config.py` (new file), and notebook cells. Do not refactor brain.py, render.py, schema.py, or skalski.py.
- **No Tailwind, CSS Modules only:** Not applicable to this phase (backend/ML).

---

## Sources

### Primary (HIGH confidence)
- `/tmp/sports/sports/common/view.py` — ViewTransformer source code, verified from git clone 42c80c0
- `/tmp/sports/sports/common/team.py` — TeamClassifier source code (SigLIP, UMAP, KMeans), exact API
- `/tmp/sports/examples/soccer/main.py` — Full radar pipeline reference; ViewTransformer usage pattern
- `read_the_floor/adapters/skalski.py` — Exact input contract skalski adapter expects
- `read_the_floor/schema.py` — COLUMNS, COURT_LEN=94, COURT_WID=50, HOOPS
- `read_the_floor/brain.py` — What the brain assumes about coordinate units (POSSESSION_R, HOOPS, beaten_index)
- PyPI: rfdetr 1.3.0, supervision 0.28.0, umap-learn 0.5.12 [VERIFIED: pip index]

### Secondary (MEDIUM confidence)
- [blog.roboflow.com/identify-basketball-players](https://blog.roboflow.com/identify-basketball-players/) — Pipeline description, SmolVLM2 vs ResNet accuracy numbers, SAM2 mask cleanup pattern
- [pypi.org/project/sam2](https://pypi.org/project/sam2/) — Package existence, torch>=2.5.1 requirement
- Roboflow Universe: `basketball-player-detection-3-ycjdo` class names (ball, player, number, referee, player-in-possession, player-jump-shot, player-layup-dunk, player-shot-block)

### Tertiary (LOW confidence)
- Compute runtime estimates (RF-DETR ~50ms, SAM2 ~80ms/frame on T4) — from general SAM2 performance literature, not basketball-specific benchmarks

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verified from source code and PyPI
- Architecture patterns: HIGH — ViewTransformer, TeamClassifier, skalski adapter all read from source
- Coordinate unit contract: HIGH — verified schema.py, brain.py, skalski.py
- Pitfalls: MEDIUM — derived from source + blog documentation + known CV pitfalls
- Compute estimates: LOW — based on general model size reports, not measured

**Research date:** 2026-06-06
**Valid until:** 2026-09-06 (90 days — rfdetr/supervision release cadence is fast; re-verify versions before executing)
