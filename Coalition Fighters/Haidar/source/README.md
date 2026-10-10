# Haidar editable source

Current scene: haidar_worn_pbr_v4.blend (artwork 1.3; accepted for this beta round). Earlier scenes, original inputs and UV layers remain as history. Artwork 1.1 remains rejected.

Haidar_Delivery_UV_v4 retains the existing layout with small local corner, central-body and wing registration corrections. Two nose faces, four lower-shoulder faces and one rear-roof triangle use a compact separate atlas, preserving sampled original artwork and fixtures. That isolation prevents local nose-gap removal from erasing valid panels that share the original texels. The lower shoulder strip is continued without the original V-coordinate wrap into unrelated artwork.

The roof has two metal struts calculated from the side struts along shared native vertices 28 and 31. Front/rear internal dividers are removed from colour, height and material masks. Frames have height +0.18; glass depth is -0.90 with a smooth 2.5-master-pixel chamfer and gasket. Pane interiors are flat and contain no painted reflections.

Generated paint repairs are composited only through the recorded thin-line and perimeter masks. Herringbone centre pixels are bit-identical. Original vertex coordinates, topology, native normals, hidden caps, part records and earlier UV layers are preserved. All current images are packed and also stored through relative resource paths; the snapshot was reopened and verified.

maps/corrections_v4 contains maps, references and masks. authoring/corrections_v4 contains the audit, build_revision.py, refine_review.py, repair_roof.py and final_panel.py, exact prompts and validation/export records. review/corrections_v4 contains supplied corrections and before/after authoring views. Treat the saved scene as authoritative; do not rerun recipes over later edits. See the pack-root approval record. The gallery photograph predates the final revision; the 3D preview uses the shipped native runtime.
