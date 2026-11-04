# Atlas Understory — cinematic 3D production lane

This is a **fresh** Vox Director production path for the user's cinematic 3D reference—not a continuation of the rejected paper-collage sample. It uses the repo's native `keyframes.py` and `clips.py` stages with a new `style: "cinematic_3d"` prompt lane. The image treatment is high-end, physically based 3D documentary visualization with deep teal/navy shadows, motivated volumetric light, restrained warm highlights, realistic materials, and deliberate editorial composition. It explicitly avoids collage, torn paper, halftone, and baked-in text.

## Current gate: Batch 0 anchors only

`beats.json` contains six anonymous environment/material anchors and no EDIT derivatives. Create and review these six images first. Do not create dependent full-film images until the user has reviewed the six actual generated anchor images. Each anchor is explicitly illustrative, not a site plan, findspot, artifact reconstruction, or field record.

## Run when the repo's provider is available

```bash
python3 scripts/keyframes.py projects/atlas-understory-3d
```

The repo's image stage uses Atlas Cloud's `google/nano-banana-2/text-to-image` model (2K, 16:9). For animation later, the cinematic lane is implemented in `scripts/clips.py`; the 3D motion stage must wait until anchor approval and a production beat map. Final assembly also needs local `ffmpeg` and `ffprobe`.

## Evidence boundaries

- No depiction of the actual ring, its engraving, museum objects, exact findspot, palace plan, excavation, or historical people as documentary evidence.
- No generated map, archaeological plan, invented inscription, or object detail that could be mistaken for the source record.
- Independent field corroboration and oral-read signoff remain open.

## Runtime prerequisites

The repo keyframe stage requires `ATLASCLOUD_API_KEY`, Python dependencies, and access to the Atlas Cloud API. The current workspace does not have the key or Atlas Cloud network access, so the render command is prepared but cannot yet produce image files here. Do not substitute procedural mockups for the requested production-quality 3D images.
