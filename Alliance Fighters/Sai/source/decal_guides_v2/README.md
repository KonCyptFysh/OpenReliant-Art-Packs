# Sai decal layout, revision 2

Use the current scene `../sai_worn_pbr_v2.blend`, active UV layer **Sai_Left_Right_UV_v2**.

- Body/tail atlas: 8192 × 4096, `../maps/decals_v2/sai_sam1_basecolor_lr_v2.png`.
- Fin atlas: 4096 × 2048, `../maps/decals_v2/sai_sam2_basecolor_lr_v2.png`.
- Each atlas has independent LEFT/PORT (first half) and RIGHT/STARBOARD (second half) areas. Right-side artwork and UVs were flipped together. New lettering should be drawn normally in each side's space, never mirrored as text. The existing livery retains its original appearance.
- Overlay the matching transparent `*_uv_overlay.png` or SVG to locate faces. Labelled SVGs name each part and face. `*_decals_blank.png` is a transparent layer at the exact atlas size.
- Keep guide lines and labels out of the final artwork. Paint decals on separate layers; send those layers back for assembly. Do not paint the outer repeat-padding strips.
- In the body sheet, the old nose lettering area is approximately x=1629..2245, y=2837..4048 on the LEFT; x=5947..6563 on the RIGHT. The old tail lettering area is approximately x=248..1274, y=507..1103 on the LEFT; x=6918..7944 on the RIGHT. These are placement guides; use the mesh/UV overlay for exact boundaries.

The geometry, normals, fin animation and existing eleven finest-model UV repairs are retained. Every distance model uses the new side layout. The two halves are separate, but repeated details within a given side still share their original UV islands; this is not a fully unique lightmap unwrap. No Japanese characters are included in this revision.
