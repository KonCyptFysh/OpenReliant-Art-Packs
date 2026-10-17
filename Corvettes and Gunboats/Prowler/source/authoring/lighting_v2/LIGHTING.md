# Prowler lighting and material revision 1.1

Ready for review on official OpenReliant 0.18.0; not approved or published.

The old intact-hull red lamp at local (-15.48, -57.69, -2156.43), intensity 8, is disabled. The original three exhaust attachments, four turret mounts, wreck lamp, geometry, UVs, normals and animation records are unchanged from the first restoration export.

The replacement local light sits aft of each nozzle: side pod 1 (6.418, -0.968, -780), side pod 2 (-10.572, 2.617, -791.5), central engine (-2.6, 289.3, -1640), each in its own native part frame. It follows forward thrust with 0.45-second rise and 0.22-second fall constants. Nozzle interiors heat over eight seconds and cool over fourteen seconds. Exact native face planes and normal directions restrict emission to the recessed interiors and local illumination to the nozzle/rim surfaces; exterior casings do not retain heat. All parts and all detail levels were sampled to exclude unrelated hull, support-arm and wreck surfaces. Simplified nozzles retain supported detail; coarse levels that omit the interiors omit their heat.

The cabin emission remains confined to the existing glass mask and mullions. Its RGB changes from (0.25, 0.43, 0.56) to (0.10, 0.16, 0.07), about 64% less encoded luminance. Base glass is dark muted green. The AL-47 stencil keeps its size, orientation and position, with a thin black outline, chips and scratches. Generated edits are composited only through local masks; surrounding hull texels and structural material maps are retained.

Cabin behaviour uses the Kurgen response: health dimming, an 8% armour-loss threshold within 0.35 seconds for hit flicker, and irregular power faults at or below 30% health with 3–6 seconds between bursts. Prowler health also includes its actual hull component. Its five damageable components are one hull and four turrets; the engine pods have no separate engine health. Engine-disable cuts drive, and retained nozzle heat cools naturally. Cloak, lights-off and destruction suppress the surface effect.

This is a scoped surface light, not a new scene light: it does not illuminate nearby ships or mounted turret models. Native plume response remains the engine's own. Enable MATERIALS, PER-PIXEL LIGHTING and MOD EFFECTS; BLOOM adds the halo. No engine binary or global shader is replaced. Adapted OpenReliant lighting code retains MPL-2.0 attribution. Revalidate against later engine shader versions.

Restart the Prowler launcher after installing. F5 cycles thrust through 0/50/100%, F6 applies a small review hit, F7 a large hit, F8 restores review armour, F9 toggles engine-disable. Hold full thrust for around 20 seconds, cut it, then watch the nozzle interiors cool. These controls exist only in mission 961. Press 7 for orbit, arrows to rotate, Shift+Up/Down to zoom.

Native model/mission validation, 36 response checks, all-detail nozzle-scope audit, official shader compilation, real-object functional integration, all three resolution-loader probes, and portable-source reopening pass. The isolated functional test uses a twofold response clock; the installed scripts use ordinary simulation time and contain no test module. Game appearance remains pending user review. Functional images are test evidence, not gallery photography.
