# Intake, belly and nose surface correction

Start from the latest v6 source scene. Set PHOENIX_WORKSPACE to the canonical worn directory and OPENRELIANT_SLTOOL to the official 0.7.0 validator. The build asserts its starting scene and preserves all earlier UV layers; do not run it blindly over later manual edits.

The relief uses inspected polygon boundaries and regular fin centres from the existing artwork. The belly uses a shared world-space projection. The nose uses selected full-area UV islands and a local bake of existing Phoenix bronze wear, with preserved original material outside the forward blend. No native mesh geometry is changed. The exporter appends a repair material to the affected native parts and retains all existing loadout material indices.

Checks cover main-map locality, preserved colour/glazing, contained relief, shared belly edges, native face data and all unrelated native chunks. The installed revision 7.0 appearance was reviewed and approved by the user for publication.
