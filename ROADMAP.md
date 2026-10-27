# Roadmap

## Current state

- Golbez is playable.
- Locked battle graphics, field sprite, portrait, palette, stats, equipment, names, and spells are implemented and verified by `verify_golbez_lock.py`.
- Local React flag tester is available via `python3 local_webui.py`.

## Remaining work: finalize naming

The implementation still has FuSoYa-era names in parts of the randomizer. These do not affect the locked graphics/data, but should be cleaned up for a finished Golbez randomizer.

1. Rename `FreeEnt/fusoya_rando.py` to `FreeEnt/golbez_rando.py`; update imports/module lists.
2. Rename spellset identifiers from FuSoYa to Golbez, or keep numeric IDs and rename only labels consistently.
3. Fix objective text `Get FuSoYa` → `Get Golbez`.
4. Remove remaining `fusoya` keys from `character_rando.py`, `dialogue_rando.py`, `custom_weapon_rando.py`, and stale comments.
5. Update script/event handles:
   - `actor(#Fusoya)` / `%fusoya actor%`
   - `#FusoyaJoined`
   - `AxFusoya`
   - Lunar Palace/opening text
   - remove or convert FuSoYa-only room/challenge content
6. Update current flags/UI/presets/activity sprites.
7. Regenerate specs after flag/UI changes:
   ```sh
   cd FreeEnt
   bash compile_all_specs.sh
   ```
8. Rebuild and verify:
   ```sh
   python3 verify_golbez_lock.py path/to/generated.sfc
   ```

## Naming constraint

The playable slot key is `golbezpc_slot`. Do not rename it to `golbez_slot`; that name is already the boss slot (`0x11`).

## Acceptance criteria

- `Cstart:golbez`, `Conly:golbez`, `Cno:golbez`, `Crestrict:golbez` work.
- No functional FuSoYa character/flag/objective handles remain.
- Golbez appears in character randomization, objectives, spoilers, and tracker.
- Lunar Palace grants Golbez.
- Every generated ROM passes `verify_golbez_lock.py`.
- Field, portrait, battle, stats, spells, equipment match the locked build.
