# Kurgen lighting proof of concept — revision 1.5

Review build for official OpenReliant 0.18.0 or later. Not published. The approved
revision 1.2 artwork, window boundaries, UV repairs and structural materials remain.
The editable material scene is still `kurgen_worn_pbr_v3.blend`: the new behaviour
is authored in the runtime scripts and surface shader beside the native export.

## Behaviour

- Cabin brightness is normalized to a new ship's starting armour. Full health is
  fully lit; sustained brightness follows weakest-quadrant health raised to 1.25
  (50% health gives about 42% cabin brightness). It eases to its new level.
- At least 8 percentage points of armour loss within 0.35 seconds triggers three
  diminishing interruptions over 1.15 seconds. A three-second cooldown prevents
  repetitive strobing. Shield-only hits do not trigger it. Hits to a healthier
  quadrant are detected even when the weakest-quadrant health figure is unchanged.
- At or below 30% weakest-quadrant hull health, sustained power faults no longer
  need another hit. A burst of one to three brief interruptions is followed by
  3–14 seconds of steady light. Pulse widths, strengths and spacing vary too;
  these are pseudorandom events, not a looping animation. The longest continuous
  lit period stays below 15 seconds during normal simulation updates.
- Each ship has its own saved random stream seeded once from the game's mission
  random generator. The sequence survives save/load, stops advancing when paused,
  and stops entirely after repairs above 30%. Large-hit flicker remains separate.
- Forward thrust drives the broad red stern illumination. Rise time constant:
  0.45 seconds; fall: 0.22 seconds. Full throttle retains the original steady
  lamp's position, pure red color, range of 2000 model units and intensity 1.
- Nozzle interiors retain heat: eight-second heating and fourteen-second cooling time
  constants. A short burst leaves little stored heat; sustained thrust leaves
  a longer red/amber afterglow. Revision 1.5 increases the inner-petal weighting
  from 0.90–0.35 to 1.25–0.75, carrying more warmth toward the lip while retaining
  the boundary fade. The outer cowling does not receive the slow glow.
- Engine-disable forces thrust demand to zero; retained heat cools naturally.
  Reverse thrust does not light these forward-drive nozzles. Full forward throttle
  is the brightness ceiling, including an afterburner command.
- Ship destruction/ejection extinguishes the effect. Mission lights-off and cloak
  suppress it. Timings advance with simulation time, not paused presentation time.
- The native Kurgen has three turret components and no separate engine components
  or engine subtargets. No fictional engine-health value is inferred from a turret.

## Scope and rendering

The old static red spill comes from attachment 5 on the main hull: a steady light
at (-28.57457, 62.79725, -2572.32935), relative to that part. Its brightness alone
changes from 1 to 0. The rest of the SHP is byte-identical to revision 1.2, including
both exhaust attachments and all four blinking navigation lamps.

OpenReliant 0.18 has no script setter for an individual attached light's brightness.
The scoped surface function therefore recreates that lamp's contribution on the
Kurgen hull using its normal maps, roughness, metalness and the engine's lighting
helpers. It adds the difference between the lit surface with and without the lamp,
preserving the original full-throttle surface response. It does not cast light onto
nearby ships or mounted turret models. No global engine shader or engine binary is
replaced. This helper integration is checked against the 0.18.0 shader source;
future engine shader changes require revalidation.

Nozzle emission is procedural. Revision 1.4 extended the existing recessed-disk glow
onto the inward-sloping nozzle petals on both sides. Their original texture remains
visible, with the added glow tapering from the throat toward a cooler lip. Triangle
geometry selects the petals independently of the normal map; the outer casing gets
no slow thermal emission. LOD 1 uses its simplified interior faces. LOD 2 retains
only its existing disk effect; the coarsest three omit it entirely. A native triangle
audit checks all six detail levels and excludes exterior faces.
The existing bridge emissive maps are scaled without changing their boundaries.
No diffuse, normal, ORM or emissive bitmap has changed, and no 4K map is duplicated.

The native exhaust plumes still use the engine's own throttle response. The smoothed
response applies to the hull glow and the thermal response to the recessed disks and inner petals.
MATERIALS, PER-PIXEL LIGHTING and MOD EFFECTS must be enabled; BLOOM adds the halo.

## Inspecting it

Run `launch-kurgen-test.sh` and restart an already-running game to load this revision.
Mission 962 is quiet and stationary, with actual throttle and armour fields driving
the production effect. The following controls affect this review mission only:

| Key | Action |
| --- | --- |
| F5 | Cycle forward thrust through 0%, 50%, 100% |
| F6 | Remove 2% armour from the aft quadrant |
| F7 | Remove 15% armour from the aft quadrant |
| F8 | Restore all armour |
| F9 | Toggle engine-disable |
| 7 | Orbit camera |
| Arrow keys | Rotate the orbit camera |
| Shift + Up/Down | Zoom |

Start cold, use F5 twice, hold full thrust for roughly 20 seconds, then use F5 again.
The thermal half-life is now about 9.7 seconds (previously 4.2 seconds); watch for
at least 20 seconds after cutting thrust to compare the extended afterglow.
The broad red illumination should fall away quickly while the nozzle interiors cool.
Look at the bridge, try isolated F6 hits, then F7. Repeated F6 taps inside the short
damage window can collectively count as a substantial impact. Damage stops at 5%
in this inspection mission so the test ship survives. F8 restores health, not heat.
For sustained power faults, restore with F8, tap F7 five times to reach roughly
25% hull, and watch the windows for 30–60 seconds without further hits. Press F8
again to verify that the random faults stop.

## Validation and remaining review

The response model is tested for thresholds, cooldown, dimming, different hit
quadrants, engine disable, cold starts, pause, destruction and timestep independence.
The official engine compiles the GLSL and loads the production adapters. A separate
instrumented runtime test exercises the review controls against real object fields;
its response clock is accelerated tenfold to avoid a long software-rendered run.
The shipping scripts use ordinary simulation seconds. Test scripts and acceleration
are excluded from the installed mod.

Revision 1.5 slows the nozzle cooling, strengthens inner-petal emission and adds
critical-health power faults. Native models, maps and inspection controls remain
unchanged. The response model has 36 checks, including a four-minute low-health
sequence, save/load continuity, repair cancellation, pause, independent ships and
simulation timestep independence. The GLSL scope audit still selects no exterior
faces across all six detail levels. The instrumented official-engine run additionally
checks sustained faults through the real hull fields and the slower cooling.

Visual review of this tuning remains with the user. Earlier revisions remain in
exports/openreliant_0_18_v4 and exports/openreliant_0_18_v5. Diagnostic frames are
functional test evidence, not gallery photography. Nothing has been published.

## Deferred feature request: real engine light spill

The user wants engines to illuminate and produce material-dependent reflections
on another ship pulled up close behind them, particularly around larger ships.
Retain the existing smooth thrust response and slower nozzle afterglow when adding
scene lighting. Official 0.18.0 supports native point lights but exposes no per-light
brightness setter through ShipAttachment; object.lights is an all-lights switch.
A suitable individual-light intensity API is the preferred future request. Recheck
the current engine API when taking this forward. This is recorded for later: no
upstream issue has been submitted and this PoC still uses hull-only surface light.
