# Beta limits and deferred work

- Artwork and lighting accepted for this beta round; later refinements can follow feedback.
- Requires official OpenReliant 0.18.0. The surface shader uses engine lighting helpers; future shader changes need revalidation.
- Dynamic turret/barrel emissives and their firing-state mission are deferred pending shot identity and per-mounted-part surface controls. No workaround ships.
- Engine illumination affects the Kurgen hull, not other nearby ships or mounted turret models. True light spill remains a separate deferred feature request.
- The Kurgen has no separate engine components. Coarsest detail levels omit procedural nozzle heat; native exhaust plumes keep their standard response.
- Full campaign, damage-distance transitions, save/load through every mission and other platforms are not exhaustively tested.
- The browser preview uses reduced maps and static lighting, without game-state effects, exhaust particles or native firing animation. Use the engine photo and included review mission for runtime appearance.
