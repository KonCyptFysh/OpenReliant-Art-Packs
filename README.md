# KonCyptFysh Art Packs

Independent **StarLancer artwork by KonCyptFysh**, packaged for compatibility with OpenReliant. OpenReliant is a separate project.

**[Browse the art-pack gallery](https://koncyptfysh.github.io/OpenReliant-Art-Packs/)** · **[Individual downloads](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/releases)** · **[Report an issue](https://github.com/KonCyptFysh/OpenReliant-Art-Packs/issues/new/choose)**

The gallery provides in-game screenshots and rotatable model previews where available. Open an asset to choose its livery; current ship artwork uses **Worn Paint**. Unreleased artwork is marked **Coming soon**. The progress bar tracks available assets and packs against the planned collection, counting each asset once. Published beta art can still have documented texture refinements outstanding. Custom emissives remain a planned later update.

## Browse the collection

- [Fighters & Bombers](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?group=small-combat-craft#collection)
- [Fleet Warships](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?group=fleet-warships#collection)
- [Transports and Support](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?group=transports-and-support#collection)
- [Satellites and Defence](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?group=satellites-and-defence#collection)
- [Stations and Infrastructure](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?group=stations-and-infrastructure#collection)
- [Weapons and Components](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?group=weapons-and-components#collection)
- [Environment and Planets](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?group=environment-and-planets#collection)
- [Cockpits](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?group=cockpits#collection)
- [HUD, Art Packs and Mission Mods](https://koncyptfysh.github.io/OpenReliant-Art-Packs/?group=hud-and-mission-mods#collection)

Filter each group by type, faction or availability. Named vessels with unconfirmed shared artwork remain visible while their contribution to progress awaits an inventory check. See [catalogue structure, liveries and dependencies](CATALOGUE.md) for the data model and counting rules.

## Download only what you need

Each released ship has its own ZIP and checksum. Install the ZIP's `mods` folder beside `resource.hog` in your existing game-data directory. Keep each mod's files flat inside its own folder. Use the OpenReliant version listed for each pack and your own installed StarLancer copy. All current ship, ordnance and HUD downloads target OpenReliant 0.8.1. See [INSTALL.md](INSTALL.md) and the [0.8.1 package update](COMPATIBILITY_0_8.md).

Use the named ZIP from a release, not GitHub's automatic source-code archive. The hierarchy here is for browsing and editing; it is not copied wholesale into the game.

Some future mods require another pack. Their gallery items show **Requires**, link to the prerequisite where it is catalogued, and explain the load order. Install and enable each prerequisite above its dependent mod in OpenReliant's MODS screen. The planned vanilla mission damage-indicator mod requires the **Friends and Foes** art pack.

## Editable sources

Each asset folder contains its current editable `source/`, game-ready `mods/`, inventories and validation notes. Large artwork uses Git LFS. The small website previews under `docs/` use regular Git so the gallery can serve them directly.

See [WORKFLOW.md](WORKFLOW.md) for preparing, testing and publishing one asset at a time. The earlier all-fighters upload has been replaced by this hierarchy; the same issue tracker is retained.

[Credits](CREDITS.md) · [Licensing status](LICENSING.md)
