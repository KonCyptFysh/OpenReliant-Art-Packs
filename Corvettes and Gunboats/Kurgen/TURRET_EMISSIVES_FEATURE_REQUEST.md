# Feature request: per-barrel shot events and independent mounted-turret surfaces

Draft for OpenReliant, checked against the official v0.18.0 source and declarations on 17 October 2026. Not submitted. Dynamic turret effects are deferred pending supported APIs.

## Problem and intended result

The Kurgen has three instances of the shared `10_Rus_STUR.SHP` small turret. Each turret has two separately animated gun parts with muzzle attachments. An art mod should be able to illuminate only the barrel that actually fires, retain heat independently on that barrel, and leave the ship's existing hull-lighting surface active.

The proposed artwork has three zones:

- **Muzzle:** an intense flash per shot, strong heat accumulation under sustained fire, and a reasonably slow cooldown.
- **Side barrel vents:** an energy pulse moving toward the muzzle for each shot, plus sustained heat with a quicker cooldown than the muzzle.
- **Rear barrel vent beside the turret body:** a fainter shot response, a slower buildup to hot, and a reasonably quick cooldown.

One ship-wide firing signal would illuminate idle turrets and the wrong barrel. A special single-turret surrogate would not validate the shared asset in its real use. The user prefers an engine feature request and has deferred the effects rather than accepting either workaround.

## Missing API capabilities

1. **Identify the actual emitting muzzle.** Extend the successful-shot event with the existing turret handle (nullable for fixed weapons), a stable barrel/part and muzzle-attachment identifier, and documented event timing. A current muzzle transform would also support correctly located visual effects. The event must distinguish alternating barrels and concurrent shots from multiple identical mounts. It should represent emitted shots, not trigger demand or an estimated firing timer.
2. **Set a surface on an individual mounted turret and barrel.** Provide instance-local surface assignment and parameters for the mounted model, with overrides for its gun parts. Preserve independent hull, turret-base and barrel surfaces; provide reset-to-default behavior. Reuse shared geometry and textures instead of copying a texture for every mount. Document identifiers across aiming, recoil, LOD changes, destruction and saved games, and which script contexts may update the surfaces.

The mod can calculate flashes, travelling pulses, heat accumulation and cooling in Luau. No built-in heat policy is needed. The existing parameter budget needs to be documented for each independently controlled part so masks and thermal channels can be designed around it.

## Source evidence in v0.18.0

- [`bullet_fire`](https://github.com/OpenReliant/openreliant/blob/v0.18.0/src/engine/hooks.zig): public fields are owner, gun type and heard. An internal `_muzzle` exists but is not exposed to scripts.
- [`guns.Muzzle` and firing flow](https://github.com/OpenReliant/openreliant/blob/v0.18.0/src/engine/game/guns.zig): the engine already retains model, part and attachment information and fires through the native gun-animation path.
- [`setSurface`](https://github.com/OpenReliant/openreliant/blob/v0.18.0/src/scripting/shaders.zig): `object:set_surface` assigns the object's top-level model parts; it does not assign the separately mounted turret models.
- [`Turret` binding](https://github.com/OpenReliant/openreliant/blob/v0.18.0/src/scripting/turrets.zig): turret handles and targeting exist, but no barrel enumeration or surface assignment is exposed.

## Acceptance test

Use a normal mission with the actual Kurgen and its native animated turrets. Exercise idle, isolated shots, alternating barrels, short bursts, sustained fire and cooldown. Two turrets firing at different times must keep independent pulse and heat states; a second ship using the same asset must remain independent. Also check aiming/recoil, destroyed mounts, LOD transitions, pause/time scaling, save/load and coexistence with the existing cabin/engine shader. A purpose-built firing-state mission can be delivered once these APIs are available.

Light cast onto nearby ships is a separate deferred engine-lighting request; emissive control alone does not provide it.
