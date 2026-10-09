# Expanded HUD development probes (30163d9)

These are editable test fixtures, not player runtime files. Use only a separate
copy of the game profile. Do not copy these folders into the live campaign mods.
The production export contains none of these probes.

- `interactive`: observation-only player script. Logs radar range/zoom and
  replacement state, power shares, full/synchronised firing, missile choice,
  subtarget label and gun charge. Exercise V, U, I, [, Ctrl+G, F and period with
  their default bindings. A Mirage starts with FULL GUNS in mission 991; F first
  turns it off. A subtarget selection must report a non-nil subtarget before
  claiming that fallback was exercised.
- `state-sweep`: global on_step changes the isolated player's shield/armour,
  velocity, fuel and countermeasure values; the player script observes them and
  switches to chase at frame 260, back at 330. It is intentionally synthetic.
  Global scripts own simulation writes; player scripts own HUD reads.
  `state-sweep-verified` exposed missing pieces in sprites/text. A constant 0.35
  state and a variant restoring the initial player position each step were
  visually clean. Restricting decoding to one picture per frame or retaining
  native gauges did not remove the fault. Its cause is unresolved; it also
  appeared during the ordinary Mirage control check, so it is not exclusively
  movement-related. Do not describe this as a confirmed image-cache bug.
- `objective-scene`: derived mission fixture with objective 0 current. It is
  deliberately named mission1.dte to use the game's localized objective text,
  "Rendezvous with Convoy". Compile named_objective.zig against the pinned
  upstream src/root.zig using its Zig version, passing the destination DTE path.
  Load as mission 1 in the isolated profile only. This overrides campaign mission
  1 while enabled; it must never be included in a community mod export.

Machine-specific harnesses, logs and captures are retained under ignored
`.local/api-expansion/`; the portable catalogue is tracking/hud-api-expansion.json.
No upstream source was edited to run these probes.
