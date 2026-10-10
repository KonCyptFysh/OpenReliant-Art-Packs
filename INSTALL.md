# Installing an individual art pack

1. Install OpenReliant 0.8.1 with your own copy of StarLancer.
2. Download the named ZIP for the ship or art pack you want. Its `.sha256` file verifies the download.
3. Close OpenReliant and back up the previous version of that mod outside the game's `mods` folder.
4. Extract the ZIP and place its mod folder inside your game-data directory's `mods` folder beside `resource.hog`. **Replace the previous folder instead of merging files** so obsolete green/red texture copies are removed. The final path is `mods/<mod-folder>/mod.ini`, with its loadable files alongside it.
5. Keep one copy of each replacement active. Move older equivalent folders or HOG archives outside `mods` before replacing them.
6. Start OpenReliant, enable the mod in GAME OPTIONS → MODS, then restart after changing its enabled state or order.

Each ship is an independent download. The category folders and editable sources in this repository are not installed into the game. Ship artwork does not require the separate HUD pack.

## Packs with dependencies

Check an item's **Requires** section before downloading. Install and enable each required pack, then place it **above the dependent mod** in GAME OPTIONS → MODS. Restart after changing the order or enabled state. OpenReliant skips a dependent mod when its prerequisite is missing, disabled or loaded later, and the MODS screen explains the problem.

The planned **Vanilla Mission Damage Indicators** mod requires the planned **Friends and Foes** art pack. It selects green, left-side indicators for friendly Kamovs and red, right-side indicators for McGann. Both entries remain Coming soon until their own packages are published. Existing independent ship texture packs do not acquire this requirement.

Dependency names refer to the actual folder under `mods` or the basename of a `.hog` archive. Keep those names intact when installing. See the [native dependency model and authoring notes](CATALOGUE.md#native-openreliant-dependencies).

## Removing or upgrading a pack

To remove a pack, close the game and move only its mod folder outside `mods`, or disable it and restart. Restore the backed-up folder to roll back.

The 0.8.1 ship and ordnance update passed native-file and texture-loader checks. Existing artwork reviews and gallery photographs used earlier engine versions; this update did not repeat gameplay or GPU-rendering captures. Individual pack notes disclose unfinished art and untested gameplay or platforms. Report the pack version, engine version, ship and mission with any issue.

## Recommissioned HUD beta

The HUD requires OpenReliant 0.8.1 and Mod Effects enabled. See
[HUD installation and shader compatibility](HUD/Recommissioned/INSTALL.md).
