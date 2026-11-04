# Atlas Understory — cinematic editorial-collage sample

A fresh visual pass built to match the supplied screenshot: layered paper/map/document elements around a dominant cinematic 3D image cut-out. The six Batch 0 anchors are generated and stored in `anchors/`. Each is 1672×941 (16:9) and avoids depicting the reported ring, museum objects, the actual palace plan, an exact findspot, or archaeological records.

## Sample video

`sample/atlas_understory_photo_stack_motion_sample_v2.mp4` is the current 39.32-second, 1920×1080, 24 fps sample. Each 3D image is isolated as its own printed photo card; cards fly in, scale/rotate, and settle into a layered stack. A red thread draws across the board while a needle pin travels to each new card and anchors it. Narration and editorial caption cards are included. This is a local layer-animation proof, not the full documentary; it has no music.

The earlier `atlas_understory_3d_collage_sample_v1.mp4` is superseded because it only moved whole frames.

Re-render the stacked-card sample from the repository root with Pillow, DejaVu fonts, and `ffmpeg` available:

```bash
python3 projects/atlas-understory-3d/sample/animate_stack.py
```

The runner uses the repo's `scripts/motion.py` Layer/easing engine for independent card motion, then locally encodes and muxes narration. `sample/beats.json` and `sample/animate_stack.py` document the animation timings and inputs.

## Current review gate

These six anonymous anchor images are for visual review. Do not create dependent full-film EDIT images until the user approves the look. After that gate, the full shot plan and assets can be built and animated in the same visual language. The existing long-form research/corroboration and oral-read signoff remain open.

## Evidence boundaries

- No depiction of the actual ring or engraving, museum objects, exact findspot, palace plan, excavation, or historical people as documentary evidence.
- Map fragments are abstract decorative paper, not a site plan or location record.
- AI-generated environments/materials are illustrative atmosphere, not field evidence.

## Repo rendering lanes

`style: "cinematic_collage"` in `beats.json` selects the repository's combined 3D-image + layered-editorial-collage prompt path. The local review sample uses `scripts/kenburns.py`. The more generative `scripts/clips.py` path requires the configured Atlas Cloud video provider; no such API call was used for this sample.
