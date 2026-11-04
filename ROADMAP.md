# Roadmap

## Current state

- Golbez is playable.
- Locked battle graphics, field sprite, portrait, palette, stats, equipment, names, and spells are implemented and verified by `verify_golbez_lock.py`.
- Local React flag tester is available via `python3 local_webui.py`.

## Remaining work: finalize naming

The implementation still has FuSoYa-era names in parts of the randomizer. These do not affect the locked graphics/data, but should be cleaned up for a finished Golbez randomizer.

1. Fix objective text `Get FuSoYa` → `Get Golbez`.
2. Remove remaining `fusoya` keys from `character_rando.py`, `dialogue_rando.py`, `custom_weapon_rando.py`, and stale comments.
3. Update script/event handles:
   - `actor(#Fusoya)` / `%fusoya actor%`
   - `#FusoyaJoined`
   - `AxFusoya`
   - Lunar Palace/opening text
   - remove or convert FuSoYa-only room/challenge content
4. Update current flags/UI/presets/activity sprites.
5. Regenerate specs after flag/UI changes:
   ```sh
   cd FreeEnt
   bash compile_all_specs.sh
   ```
6. Rebuild and verify:
   ```sh
   python3 verify_golbez_lock.py path/to/generated.sfc
   ```

## Naming constraint

The playable slot key is `golbezpc_slot`. Do not rename it to `golbez_slot`; that name is already the boss slot (`0x11`).

The spellset identifiers `FusoyaWhite` / `FusoyaBlack` are still used internally. Renaming them changes generated patch ordering and the canonical build hash; do that only alongside a new verified locked baseline.

## Acceptance criteria

- `Cstart:golbez`, `Conly:golbez`, `Cno:golbez`, `Crestrict:golbez` work.
- No functional FuSoYa character/flag/objective handles remain.
- Golbez appears in character randomization, objectives, spoilers, and tracker.
- Lunar Palace grants Golbez.
- Every generated ROM passes `verify_golbez_lock.py`.
- Field, portrait, battle, stats, spells, equipment match the locked build.
