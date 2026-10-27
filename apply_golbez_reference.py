#!/usr/bin/env python3
"""Apply the locked Golbez data to an existing generated ROM.

Usage:
    python3 apply_golbez_reference.py input.sfc output.sfc

The generator already applies this automatically. This tool is useful for
repairing an older build.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REF = ROOT / "golbez_reference"

BLOBS = [
    ("battle_sheet_G.bin", 0x0D6800),
    ("battle_pal_G.bin", 0x0E7EA0),
    ("working_map_sheet.bin", 0x0DA700),
    ("working_portrait.bin", 0x0EE740),
    ("working_portrait_pal.bin", 0x0687A0),
    ("working_map_pal.bin", 0x068030),
    ("working_map_pal_dup.bin", 0x0680E0),
    ("levelptr_G.bin", 0x07B524),
    ("charitem_G.bin", 0x079070),
    ("item_name_G.bin", 0x078276),
    ("spells_G.bin", 0x07C700),
    ("levelup_G.bin", 0x07C400),
    ("stats_G.bin", 0x07AA80),
]


def apply(input_path: Path, output_path: Path) -> None:
    rom = bytearray(input_path.read_bytes())
    for name, address in BLOBS:
        data = (REF / name).read_bytes()
        rom[address:address + len(data)] = data
        print(f"{name:24s} -> 0x{address:06X} ({len(data)} bytes)")

    vanilla_path = ROOT / "ff2.smc"
    if vanilla_path.exists():
        vanilla = vanilla_path.read_bytes()
        for start, size in [
            (0x06F961, 0x100),  # CharTileTbl
            (0x09FB81, 0x100),  # CharAnimPoseTbl
            (0x016064, 0x02),   # $f077 threshold
            (0x01636A, 0x02),   # idle phase gate
            (0x01636F, 0x03),   # idle phase timer
        ]:
            rom[start:start + size] = vanilla[start:start + size]
    rom[0x0AB307] = 0x03
    output_path.write_bytes(rom)
    print(f"\nwrote {output_path} ({len(rom)} bytes)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    apply(Path(sys.argv[1]), Path(sys.argv[2]))
