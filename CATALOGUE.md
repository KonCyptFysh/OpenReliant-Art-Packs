# Catalogue structure and progress

`catalog.json` is the source for the gallery. Run `python3 tools/build_site.py`
after editing it; the validated copy is written to `docs/catalog.json` for
GitHub Pages. The website and data remain buildless. Existing release URLs,
mod folder names, editable sources, screenshots and GLBs are preserved.

## Groups and categories

The sidebar shows an expanded hierarchy: select a broad group to see all its
assets, or select an indented category directly. Both levels remain clickable.
The menu scrolls independently on desktop and stays vertically scrollable on
small screens. Faction, ship class and alternative names are separate metadata.

| Group | Categories covered |
| --- | --- |
| Fighters & Bombers | Alliance fighters, Coalition fighters, torpedo bombers |
| Fleet warships | Corvettes, fleet destroyers, command ships, cruisers, carriers, supercarriers |
| Transports and support | Freight, shuttles, troop and assault transports, cargo handling, rescue, replenishment, engineering, research, civilian liners, prison ships |
| Satellites and defence | Early-warning satellites, defence satellites, heavy weapon platforms |
| Stations and infrastructure | Fleet bases, shipyards, supply depots, mining, research, command stations, warp gates |
| Weapons and components | Existing ordnance pack, cargo, escape equipment, mission objects, mines, weapon mounts, propulsion, sensors, structural parts |
| Environment and planets | The existing environment collection, retained for future work |
| Cockpits | Cockpit interiors, emissive screens, buttons and illuminated controls |
| HUD and mission mods | HUD artwork, supporting art packs, mission modifications |

The catalogue categorisation does not require moving published source or
runtime folders. Keep an existing entry's `id` and `folder` stable. The historic
fighter and bomber category links remain usable. Named carrier classes and
cruiser families belong in `shipClass`; they do not imply identical geometry
or textures.

Cockpit restoration is a **long-term** plan. The dedicated `cockpits` group
initially tracks one **Coming soon** pack, `cockpit-retextures-and-emissives`,
under `cockpit-interiors`, with `milestone: "long-term"`. Its scope covers
interior textures and emissive screens, buttons and illuminated controls.
It counts as one planned pack until unique cockpit models and shared materials
have been inventoried; do not assume a separate cockpit asset for every fighter.

## What the progress bar measures

Progress counts **available catalogue assets and packs out of explicitly
tracked planned assets and packs**. Each entry contributes once, regardless
of the number of liveries, photographs or model poses. Existing multi-object
packs, including ordnance and the HUD, each remain one delivery unit.

`available` means an individual beta release has been published and verified.
It does not mean every texture refinement, emissive map or platform test is
finished. Preserve the existing known-work and validation notes.

A newly planned asset uses `status: "coming-soon"` and
`workStatus: "planned"`. It has no published download metadata. Its card opens
normally, shows its category and plan, and displays **Coming soon**.

Some named capital vessels have not yet been mapped to their underlying
models and texture sets. These entries remain visible and searchable with
`entryType: "named-vessel"`, `scopeStatus: "pending-audit"` and
`countsTowardProgress: false`. They are excluded from the percentage until
that scope is established. After inspection, either make a distinct asset
count toward progress or retain the name on the matching asset. Do not count
a class, a hull and its aliases as three completed ships.

Shared-component entries are explicit planned packs, not a claim that each
engine, turret or hatch in the original game has already been inventoried.
The catalogue's inventory notes and sources record that boundary.

## Liveries

Schema 2 keeps a ship's identity at the asset level and its presentations in
`liveries`. Current ship and ordnance artwork is named **Worn Paint**. The
existing HUD is a standalone pack and does not need a paint selector.

```json
{
  "id": "example-ship",
  "name": "Example Ship",
  "category": "torpedo-bombers",
  "status": "coming-soon",
  "workStatus": "planned",
  "defaultLivery": "worn-paint",
  "liveries": [
    {
      "id": "worn-paint",
      "name": "Worn Paint",
      "status": "coming-soon"
    }
  ]
}
```

When a livery is ready, place its own `preview`, `model`, `images`, preview
labels, `modFolder`, engine requirement, artwork revision and verified release
metadata in that livery object. `preview` must be the first `images` entry when
an image gallery is present. The shared asset can retain its `folder` and
description; an individual livery may override them.

Add restored paint or another livery as another object with a stable `id` and
display `name`. Its media and download are independent. The selector updates
the model, photographs, download details and requirements together, resets
the photograph position, and invalidates an older pending model load. Missing
media does not inherit another livery's pictures or model. A future livery may
remain **Coming soon** while Worn Paint stays available.

The asset-level `status` is `available` when at least one livery is available.
Keep `defaultLivery` pointed at an available livery in that case. A second
released livery does not increase the headline completed-asset count.

## Native OpenReliant dependencies

OpenReliant declares mandatory dependencies through **`Requires` in the
`[Mod]` section of `mod.ini`**. Each value is an installed **mod directory name
or HOG archive basename**, compared without case sensitivity. It is not the
mod's display title or a version range.

Catalogue `requires` is an array of those exact native names. Put shared
requirements at the asset level and additional livery-specific requirements
on the livery. The website combines them. When publishing a pack, the combined
set must match the packaged manifest; the build checks this against `mod.ini`.
A required pack already represented here must be available before a dependent
pack can be marked available. External prerequisites can use their native name
without inventing a local gallery entry or download.

### Planned Friends and Foes integration

The catalogue reserves `friends-and-foes` as the planned art pack's mod folder
name and `vanilla-mission-damage-indicators` for the planned mission mod. These
are planned packages, not new released downloads.

The mission mod's catalogue metadata contains:

```json
"requires": ["friends-and-foes"]
```

Its eventual native manifest must contain:

```ini
[Mod]
Name=Vanilla Mission Damage Indicators
Requires=friends-and-foes
```

The mission changes use **green, left-side indicators for the friendly Kamovs**
and **red, right-side indicators for McGann**. Friends and Foes supplies the
required artwork; the mission mod chooses those indicators. This requirement
does not apply to every ship texture pack.

Install and enable the prerequisite, place it **above** the dependent mod in
OpenReliant's MODS screen, and restart after changing the enabled state or
order. A missing, disabled or later-loaded prerequisite causes OpenReliant to
skip the dependent mod. The gallery describes this requirement; it cannot
inspect a visitor's local installation.

Basic dependency enforcement arrived in OpenReliant 0.7. Existing releases in
this catalogue continue to target 0.8.1. Confirm the actual engine requirement
for the future mission implementation before release; the dependency feature's
minimum alone does not establish HUD or scripting compatibility. Older 0.6.x
loaders do not enforce these requirements.

Do not add native `Depends`, `LoadAfter`, optional-dependency flags or mod
version constraints. `Version` is pack metadata, while `OpenReliant` specifies
a minimum engine version. The dependency model is documented in the
[official modding guide](https://github.com/OpenReliant/openreliant/blob/main/docs/guide/modding.md)
and implemented by the
[loader inspected for this change](https://github.com/OpenReliant/openreliant/blob/078600bec9b372601a21cc84f32124f6316e73d2/src/engine/game/bigfile/mods.zig).

## Checks before publishing the gallery

Run the catalogue validator and its regression tests, then the JavaScript
behaviour checks:

```sh
python3 -m unittest discover -s tools -p 'test_build_site.py'
node --test tools/test_catalogue.mjs
python3 tools/build_site.py
```

Review the catalogue on desktop and mobile when browser preview is available:
filters, old deep links, Coming soon entries, livery changes, both preview
modes, screenshot navigation, dependency links and download targets. Do not
change an available status merely to make a percentage look complete.
