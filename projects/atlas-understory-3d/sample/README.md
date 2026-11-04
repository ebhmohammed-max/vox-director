# Cinematic editorial-collage sample v1

- Runtime: 39.32 seconds
- Frame: 1920×1080, 25 fps, H.264
- Images: six freshly generated 16:9 collage/3D anchor plates from `../anchors/`
- Motion: Vox Director repo's `scripts/kenburns.py` fallback, alternating slow push/pull on each plate
- Audio: reused selected synthetic narration from the earlier sample; no music in this cut
- Captions: locally typeset paper cards with an always-visible non-evidence disclosure

This is a six-anchor style/motion sample, not the full documentary. It deliberately uses only anonymous environmental/material images. The reported ring, its engraving, museum objects, actual palace plan, exact findspot, excavation, and historical people are not depicted. Independent field corroboration and oral-read signoff remain open.

Render using the Vox Director repository from its root:

```bash
python3 projects/atlas-understory-3d/sample/render_sample.py
```

Requires Pillow, DejaVu fonts, and `ffmpeg` on `PATH`. The runner invokes `scripts/kenburns.py` to create the individual animated clips, then adds the captions and narration.
