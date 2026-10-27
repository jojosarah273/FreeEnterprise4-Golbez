# Golbez Locked Specification

**Status: locked.** This is the authoritative specification for the Golbez replacement. Do not change these regions casually.

## Canonical build

| Item | Value |
|---|---|
| ROM | `golbez_exact_playable.sfc` |
| SHA-1 | `a8ae9f5d1a5d8ca4d437c4478c1318352db4f1d0` |
| SHA-256 | `838dcf0f0ec7fc8c4ff57106d1ea3585172dfd52fc6b45cfa0c8513ce1a633be` |
| Flags | `Onone Kmain Pnone Crelaxed/only:cecil,golbez/Cstart:golbez Tvanilla Svanilla Bvanilla Evanilla Gnone/-vanilla:fashion` |
| Quickstart | yes |
| Verifier | `python3 verify_golbez_lock.py` |

## Non-negotiable rules

1. Battle sheet at `0x0D6800` must be exactly `golbez_reference/battle_sheet_G.bin`.
2. Battle palette at `0x0E7EA0` must be exactly `golbez_reference/battle_pal_G.bin`.
3. `CharTileTbl` at `0x6F961` and `CharAnimPoseTbl` at `0x9FB81` must remain vanilla.
4. Do not re-enable `$f077`, special-pose, or idle-timer hacks. They break the battle sprite.
5. Field/map sprite and portrait must use the locked field/portrait blobs. Do not replace them with the battle-reference map/portrait data.
6. `0x0AB307` must be `0x03`.
7. Stats/items/names/spells must use the locked blobs.
8. Do not recolor, "improve", or regenerate a locked blob without a new verified capture.

## Locked data regions

All addresses are ROM offsets in the generated 2 MB ROM.

| File | Address | Size | Purpose |
|---|---:|---:|---|
| `battle_sheet_G.bin` | `0x0D6800` | `0x800` | Golbez battle sheet, normal 4bpp |
| `battle_pal_G.bin` | `0x0E7EA0` | `0x20` | Golbez battle palette |
| `working_map_sheet.bin` | `0x0DA700` | `0x300` | Golbez field sprite |
| `working_portrait.bin` | `0x0EE740` | `0x180` | Golbez portrait |
| `working_portrait_pal.bin` | `0x0687A0` | `0x30` | Portrait palette bank |
| `working_map_pal.bin` | `0x068030` | `0x10` | Map sprite palette |
| `working_map_pal_dup.bin` | `0x0680E0` | `0x10` | Duplicate map palette slot |
| `levelptr_G.bin` | `0x07B524` | `0x02` | Level-up pointer (`67 C2`) |
| `charitem_G.bin` | `0x079070` | `0x1B90` | Items, equipment, names, char props |
| `item_name_G.bin` | `0x078276` | `0x09` | Abyss/custom item name text |
| `spells_G.bin` | `0x07C700` | `0x220` | Learned/initial spell lists |
| `levelup_G.bin` | `0x07C400` | `0x100` | Level-up area (`FF` = unused) |
| `stats_G.bin` | `0x07AA80` | `0x20` | Golbez stats |

Also:

```text
0x0AB307 = 0x03
```

## Locked vanilla regions

These must match vanilla FF2 US. The generator verifies them after applying Golbez data.

| File | Address | Size | Meaning |
|---|---:|---:|---|
| `locked_tiletable.bin` | `0x06F961` | `0x100` | `CharTileTbl` |
| `locked_animtable.bin` | `0x09FB81` | `0x100` | `CharAnimPoseTbl` |
| `locked_f077.bin` | `0x016064` | `0x02` | `$f077` threshold (`0F 90`) |
| `locked_phase_gate.bin` | `0x01636A` | `0x02` | Idle phase gate |
| `locked_phase_timer.bin` | `0x01636F` | `0x03` | Idle phase timer |

## Exact stats

`stats_G.bin` / `0x7AA80`:

```text
93 0D 1E 00 00 00 00 9B 0B 9B 0B E6 00 E6 00
1E 14 21 1E 19 00 00 00 1A DF 01 00 10 00 1A DF 01
```

Decoded:

- axtor `0x13` + flags
- job `0x0D`
- level 30
- HP / max HP: 2971
- MP / max MP: 230
- STR 30, SPD 20, STA 33, INT 30, SPR 25

Level-up:

- `0x7B524` = `67 C2`
- `0x7C400:0x7C500` = `FF` (unused)

## Names, spells, equipment

These are contained in the locked blobs:

- `charitem_G.bin` (`0x79070:0x7AC00`) includes attack/item properties, item misc data, character/class names, character props, and equipment data.
- `spells_G.bin` (`0x7C700:0x7C920`) includes learned and initial spell lists.

Do not hand-edit individual values; replace the whole locked blob only through a verified manifest update.

## Build-time guard

`FreeEnt/generator.py`:

1. Writes every locked blob.
2. Verifies each write.
3. Verifies the locked vanilla tables/timer bytes.
4. Raises `RuntimeError` on any mismatch.

## Verification

```sh
python3 verify_golbez_lock.py
python3 verify_golbez_lock.py path/to/generated.sfc
```

Expected:

```text
PASS: reference blobs match LOCKED_MANIFEST.json
PASS: <rom> contains every locked Golbez region
PASS: exact reference build sha1 a8ae9f5d1a5d8ca4d437c4478c1318352db4f1d0
```

## Change protocol

If the locked result must change intentionally:

1. Produce a new verified reference capture.
2. Replace the relevant `golbez_reference/*.bin` files.
3. Recompute `LOCKED_MANIFEST.json` sizes and SHA-256 hashes.
4. Update `EXPECTED_BUILD_SHA1` in `verify_golbez_lock.py`.
5. Rebuild with the canonical flags.
6. Run the verifier and test battle/field/portrait/stats/spells.
7. Update this document.

## Regression symptoms

| Symptom | Likely cause |
|---|---|
| Battle sprite garbled | tile/animation table not vanilla, or wrong battle sheet/palette |
| Wrong pose layout | old `$f077`/Golbez-block hacks re-enabled |
| Field sprite wrong | wrong field blob, map palette, or `0x0AB307` |
| Portrait wrong | wrong portrait/portrait-palette blob |
| Only Cecil playable | wrong flags; use `only:cecil,golbez/Cstart:golbez` |
| Stats/spells/equipment wrong | locked data overridden after generation |
| Level-up behavior wrong | wrong level pointer/level-up blob |
