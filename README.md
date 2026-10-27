# FreeEnterprise4-Golbez

A Golbez-focused fork of [FreeEnterprise4](https://github.com/HungryTenor/FreeEnterprise4), the open-source randomizer for **Final Fantasy IV (US)**.

The goal of this fork is to make **Golbez a real playable character in place of FuSoYa**, with exact battle graphics, field sprite, portrait, stats, spells, equipment, names, and objectives.

## No ROMs are included

This repository does **not** contain `ff2.smc`, save states, or generated `.sfc` ROMs. You must supply your own legally obtained **FF2 US v1.1 headerless ROM** as `ff2.smc` in the project root.

The small files under `golbez_reference/` are the project’s locked reference data used by the generator. They are not a complete game ROM.

## Status

- Golbez is playable.
- Locked Golbez battle graphics, field sprite, portrait, palette, stats, equipment, names, and spell lists are implemented.
- Generated ROMs are checked against `golbez_reference/LOCKED_MANIFEST.json` at build time.
- Remaining work is the final FuSoYa→Golbez naming cleanup in the randomizer/UI; see `ROADMAP.md`.

## Setup

Requirements: Python 3.7+, pip, and a headerless FF2 US v1.1 ROM.

```sh
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
```

Place your ROM here:

```text
./ff2.smc
```

## Generate a ROM

Canonical Golbez quickstart build:

```sh
python3 -m FreeEnt ff2.smc make \
  -s GOLBEZ1 -q -r \
  -f 'Onone Kmain Pnone Crelaxed/only:cecil,golbez/Cstart:golbez Tvanilla Svanilla Bvanilla Evanilla Gnone/-vanilla:fashion' \
  -o golbez_exact_playable.sfc
```

## Local web UI

A local flagset tester is included. It serves the original FreeEnterprise React flag editor, restricted to flags supported by this source tree:

```sh
python3 local_webui.py
```

Open:

```text
http://127.0.0.1:8099/make
```

See `LOCAL_WEBUI.md` for details.

## Locked Golbez data

The authoritative specification is **`GOLBEZ_LOCKED_SPEC.md`**.

Key points:

- Exact locked Golbez battle sheet at `0x0D6800` and battle palette at `0x0E7EA0`.
- Vanilla `CharTileTbl` / `CharAnimPoseTbl`; no `$f077` or special-pose hacks.
- Verified working field sprite and portrait blocks for the FuSoYa slot.
- Exact GOLBEZ stats, items, names, and spell lists.
- Build-time guard fails if any locked region changes.

Verify a build with:

```sh
python3 verify_golbez_lock.py path/to/generated.sfc
```

## Documentation

- `START_HERE.md` — quick project entry point.
- `GOLBEZ_LOCKED_SPEC.md` — locked graphics/data specification.
- `ROADMAP.md` — remaining randomizer naming cleanup.
- `LOCAL_WEBUI.md` — local web UI usage.

## Credits and license

Based on [FreeEnterprise4](https://github.com/HungryTenor/FreeEnterprise4), distributed under the MIT License. See `LICENSE`.

Final Fantasy IV is © Square Enix. This project does not distribute the game ROM.
