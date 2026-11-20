#!/usr/bin/env python3
"""Apply the locked Golbez data to an existing generated ROM.

Usage:
    python3 apply_golbez_reference.py input.sfc output.sfc

The generator already applies this automatically. This tool is useful for
repairing an older build. Locked regions and addresses come from
golbez_reference/LOCKED_MANIFEST.json via FreeEnt.golbez_lock, so there is
a single source of truth.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from FreeEnt import golbez_lock


def apply(input_path: Path, output_path: Path) -> None:
    rom = bytearray(input_path.read_bytes())

    for name, address, data in golbez_lock.blob_list():
        rom[address:address + len(data)] = data
        print(f"{name:24s} -> 0x{address:06X} ({len(data)} bytes)")

    # Vanilla regions Golbez depends on: restore from the vanilla ROM if
    # it is available locally.
    vanilla_path = ROOT / "ff2.smc"
    manifest = golbez_lock.load_manifest()
    if vanilla_path.exists():
        vanilla = vanilla_path.read_bytes()
        for name, meta in manifest["locked_vanilla"].items():
            start = meta["address"]
            size = meta["size"]
            rom[start:start + size] = vanilla[start:start + size]
            print(f"{name:24s} -> 0x{start:06X} (restored vanilla)")
    else:
        print("note: ff2.smc not found; locked vanilla regions left as-is")

    rom[golbez_lock.MAP_PALETTE_SELECTOR_ADDRESS] = golbez_lock.MAP_PALETTE_SELECTOR_VALUE

    # Verify the result exactly like a fresh build.
    for name, meta in manifest["locked_vanilla"].items():
        data = (ROOT / "golbez_reference" / name).read_bytes()
        start = meta["address"]
        if rom[start:start + len(data)] != data:
            raise RuntimeError(f"Golbez lock failed: {name} changed at 0x{start:06X}")

    output_path.write_bytes(rom)
    print(f"\nwrote {output_path} ({len(rom)} bytes)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        raise SystemExit(2)
    apply(Path(sys.argv[1]), Path(sys.argv[2]))
