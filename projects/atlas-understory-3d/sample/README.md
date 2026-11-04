# Photo-stack motion sample v2

- Runtime: 39.32 seconds
- Frame: 1920×1080, 24 fps, H.264 + AAC
- Images: six generated 16:9 3D/collage anchor plates from `../anchors/`
- Motion: individually separated photo cards fly in, overlap, rotate, and settle into a growing stack; red thread draws and a needle pin travels to pin each new card
- Engine: Vox Director `scripts/motion.py` Layer/easing classes, with local Pillow compositing and ffmpeg encoding
- Audio: selected synthetic narration reused from the earlier sample; no music in this cut
- Captions: typeset paper cards with an always-visible non-evidence disclosure

This is a six-anchor style/motion sample, not the full documentary. It uses only anonymous environmental/material images. The reported ring, its engraving, museum objects, actual palace plan, exact findspot, excavation, and historical people are not depicted. Independent field corroboration and oral-read signoff remain open.

Render from the Vox Director repository root:

```bash
python3 projects/atlas-understory-3d/sample/animate_stack.py
```

Requires Pillow, DejaVu fonts, and `ffmpeg` on `PATH`. The previous whole-frame Ken Burns sample remains archived as v1; v2 is the stacked-photo animation pass.
