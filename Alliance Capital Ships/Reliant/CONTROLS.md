# Review controls

## Patriot launch and landing

Run `tools/launch-reliant-flight-test.sh`, or `tools/launch-reliant-test.sh --flight`.

- C → 1 Base → 1 Permission to land: native bridge response, landing cutscene and mission end. If the review doors are moving or held open, their cycle closes first; the normal landing delay starts afterwards.
- A: primary target (Reliant). W: nearest friendly.
- + / −: throttle. Backspace: stop. Tab: afterburner.
- Mouse/joystick or arrows: steering. 1: cockpit. 6: target camera. 7: external. 0: screenshot. F1: your bindings.

## Close inspection

Run `tools/launch-reliant-test.sh`; add `--doors` for the door demonstration.

- Arrows: orbit. Shift+Up/Down: zoom. Ctrl+arrows: pan.
- Page Up/Down: whole ship, bridge and engine focus. Home: reset.
- Alt+arrows: rotate the ship in the light. Alt+comma/period: roll. Alt+Home: reset orientation.
- F4: detailed/native camera. F5: thrust. F6/F7: small/heavy hull hit. F8: restore armour. F9: disable engines. F10: critical hull damage. F12: destroy the actual engine component (restart to restore).

Inspection controls affect only the inspection missions. Normal gameplay flight and camera controls are preserved.
