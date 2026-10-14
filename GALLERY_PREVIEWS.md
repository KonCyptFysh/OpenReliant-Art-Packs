# Ship gallery photography

Use `tracking/gallery-standard.json` for every ship publication. The user selected
an elevated front three-quarter view on 12 October 2026: upright, nose down-right,
native blue nebula behind it, consistent framing and current in-game materials.

All ship cards, ship photo galleries and the homepage hero use **fresh official
engine screenshots of the current repository runtime**. Never source these from
the user's Pictures folder, issue-report screenshots, an old review capture or a
Blender still. Preserve those originals as history; remove their live gallery links.
Do not alter the ship artwork to produce a gallery picture.

## Reproduce

The baseline is official OpenReliant 0.8.1. Use a licensed local StarLancer install.
`tools/capture_gallery.py --help` lists the required paths. It creates an isolated
capture game, links the original game data and one current repository mod at a time,
verifies the runtime manifest, captures and quits without changing personal settings.
Raw PNGs, exact engine hash and capture records go to each ship's named
`worn/review/gallery_standard_v1` and `worn/work/gallery_standard_v1` folders.

The common camera is `--watch 0 --watch-from 1.4,-1.4,1.4`, 45 degrees around and
35.264 degrees above the nose, 2560 by 1920, eight-sample antialiasing and seed 1.
The quiet fixture uses the authored Mirage inspection mission, with no combat,
movement, UI text or third-party visual effects. Normal photos are taken at tick 60;
articulated ships use their native stowed/deployed inspection missions,
with deployed/fighting captures at tick 450. The stowed/folded image goes first.
The capture script's ship-type table must include any newly published ship.

`tools/frame_gallery.py` crops the fresh captures to 4:3, centres the visible ship,
targets 76% of either frame dimension, and saves 1280 by 960 WebP at quality 94.
Only crop and downsample. Never mirror, repaint, recolour, sharpen or replace the sky.
The framing detector is a starting point: **inspect every final photo and the fleet
contact sheet**, including dark tips, separate parts and torpedoes. Reframe or
recapture any clipped or badly scaled result before publishing. Use matching crops
for alternate states where practical. No screenshot may retain cinematic bars.

Run the framer with `--publish-catalog` only after the whole published ship set has
current capture records. It updates the catalogue and
`tracking/gallery-standard-captures.json`; the website build checks each photo's
hash, camera, dimensions and artwork/runtime revision. A missing or stale capture
must block publication, rather than silently fall back to a user screenshot.

Keep source and runtime assets, beta ZIPs, release tags and checksums unchanged for
a gallery-only pass. Commit the images, provenance, catalogue and policy together;
verify the pushed files and live Pages deployment. HUD artwork and the ordnance
detail gallery have different purposes and are outside this ship camera rule.
