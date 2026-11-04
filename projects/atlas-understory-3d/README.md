# Atlas Understory — cinematic editorial-collage sample

A fresh visual pass built to match the supplied screenshot: layered paper/map/document elements around a dominant cinematic 3D image cut-out. The six Batch 0 anchors are generated and stored in `anchors/`. Each is 1672×941 (16:9) and avoids depicting the reported ring, museum objects, the actual palace plan, an exact findspot, or archaeological records.

## Sample video

`sample/atlas_understory_3d_collage_sample_v1.mp4` is a 39.32-second, 1920×1080, 25 fps H.264 sample using all six anchors, the existing selected narration, paper-style caption cards, and fade-in/out. Motion uses Vox Director's local `scripts/kenburns.py` still-to-motion fallback (alternating slow push/pull), not an AI image-to-video service. The cut has no music and is a short visual proof, not the full documentary.

Re-render from the repository root with Pillow and `ffmpeg` available:

```bash
python3 projects/atlas-understory-3d/sample/render_sample.py
```

The runner calls `scripts/kenburns.py`, then assembles the clips, caption overlays, and narration. `sample/beats.json` documents the six beats and local image paths.

## Current review gate

These six anonymous anchor images are for visual review. Do not create dependent full-film EDIT images until the user approves the look. After that gate, the full shot plan and assets can be built and animated in the same visual language. The existing long-form research/corroboration and oral-read signoff remain open.

## Evidence boundaries

- No depiction of the actual ring or engraving, museum objects, exact findspot, palace plan, excavation, or historical people as documentary evidence.
- Map fragments are abstract decorative paper, not a site plan or location record.
- AI-generated environments/materials are illustrative atmosphere, not field evidence.

## Repo rendering lanes

`style: "cinematic_collage"` in `beats.json` selects the repository's combined 3D-image + layered-editorial-collage prompt path. The local review sample uses `scripts/kenburns.py`. The more generative `scripts/clips.py` path requires the configured Atlas Cloud video provider; no such API call was used for this sample.
