# Reliant editable source

Start from `reliant_worn_pbr_v11.blend` for the ship and `reliant_hangar_v11.blend` for the separate native launch hangar. Both preserve packed material images. `maps/` retains the current exterior and interior authoring maps. `originals/` preserves native reference models and original atlases. `authoring/` records the reconstruction and refinement history, including prompts, registrations, recipes and checks.

Earlier records describe historical review states and rejected intermediate passes. The root `approval.json` and `release.json` describe the accepted release. Historical recipes contain substituted environment placeholders and are provenance rather than a one-command portable rebuild. Do not regenerate the current packed scenes from an older recipe.
