# Cinematic 3D documentary lane

This is an optional visual lane for a user who explicitly wants cinematic three-dimensional documentary imagery rather than the repo's default flat paper-collage posters. Keep the normal Vox editorial discipline—strong focal hierarchy, clean composition, intentional graphic-safe space, clear labels in post—while rendering the image plates as coherent, physically based 3D scenes. Do not put titles or important facts inside generated imagery; typeset them after the image/video stage.

## Still-image prompt contract

`styles.compose_cinematic_3d_prompt()` supplies a shared look: feature-documentary VFX craft, physically plausible scale/materials/global illumination, deep teal and midnight-navy shadows, cool blue-green ambient fill, motivated volumetric light, restrained amber highlights, controlled contrast, and naturalistic lens/focus falloff. Each shot must then specify:

1. **One scene** with only the visual subject needed for that beat.
2. **Framing** and focal hierarchy; reserve space for editorial titles/captions.
3. **Lighting** motivated by the scene, not generic glow effects.
4. **Evidence boundaries** specific to the shot.
5. **No baked text**—all titles, charts, maps, citations, and captions are added as verified post graphics.

For this Alexandria project, generated images may illustrate abstract environments or generic processes only. They must not present the reported ring, engraving, museum objects, exact findspot, palace plan, excavation, historical people, or invented inscriptions as documentary evidence. A generic material surface must not resolve into the actual described object. Maps and diagrams require a verified source/plan and explicit labeling; no generative reconstruction from speculation.

## Motion prompt contract

`clips.cinematic_3d_prompt()` asks for one continuous cinematic shot with a single camera move and restrained, physically coherent environmental action. Preserve geometry, scale, material, lighting direction, and image composition. Do not add objects or generate text. Prefer short, varied shots with distinct purpose over one long AI move; use post-production cuts and typography to carry the narrative.

## Quality control

- Review every anchor at full resolution before deriving dependent keyframes.
- Reject visual drift, invented archaeological details, changing silhouettes, fake readable inscriptions, and incorrect material/object identity.
- Review first and last frames of every generated clip for morphing, object emergence, camera resets, flicker, and text artifacts.
- Keep evidence labels and captions as deterministic overlays.
- Do not claim independent corroboration or narration signoff that has not occurred.

The stages are still the repository's own `keyframes.py` → `clips.py` → `audio.py` → `assemble.py`. The `cinematic_3d` style value selects this lane; default collage projects are unchanged.
