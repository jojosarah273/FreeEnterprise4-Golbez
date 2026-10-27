#!/usr/bin/env python3
"""Verify the locked Golbez reference data and a generated ROM.

Usage:
    python3 verify_golbez_lock.py [rom.sfc]

With no ROM argument, only the reference blob hashes are checked.
With a ROM, every locked region is checked at its exact address.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REF = ROOT / "golbez_reference"
MANIFEST = REF / "LOCKED_MANIFEST.json"
EXPECTED_BUILD_SHA1 = "a8ae9f5d1a5d8ca4d437c4478c1318352db4f1d0"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def check_reference() -> dict:
    if not MANIFEST.is_file():
        fail(f"missing manifest: {MANIFEST}")
    manifest = json.loads(MANIFEST.read_text())

    for group in ("blobs", "locked_vanilla"):
        for name, meta in manifest[group].items():
            path = REF / name
            if not path.is_file():
                fail(f"missing reference file: {name}")
            data = path.read_bytes()
            if len(data) != meta["size"]:
                fail(f"{name}: size {len(data)} != {meta['size']}")
            if sha256(data) != meta["sha256"]:
                fail(f"{name}: sha256 mismatch")
    print("PASS: reference blobs match LOCKED_MANIFEST.json")
    return manifest


def check_rom(manifest: dict, rom_path: Path) -> None:
    rom = rom_path.read_bytes()

    for name, meta in manifest["blobs"].items():
        start = meta["address"]
        data = (REF / name).read_bytes()
        actual = rom[start:start + len(data)]
        if actual != data:
            fail(f"{rom_path.name}: {name} differs at 0x{start:06X}")

    for name, meta in manifest["locked_vanilla"].items():
        start = meta["address"]
        data = (REF / name).read_bytes()
        actual = rom[start:start + len(data)]
        if actual != data:
            fail(f"{rom_path.name}: {name} was changed at 0x{start:06X}")

    if len(rom) > 0x0AB307 and rom[0x0AB307] != 0x03:
        fail(f"{rom_path.name}: map palette selector 0x0AB307 must be 0x03")

    print(f"PASS: {rom_path.name} contains every locked Golbez region")
    if hashlib.sha1(rom).hexdigest() == EXPECTED_BUILD_SHA1:
        print(f"PASS: exact reference build sha1 {EXPECTED_BUILD_SHA1}")


def main() -> None:
    manifest = check_reference()
    if len(sys.argv) > 1:
        check_rom(manifest, Path(sys.argv[1]))
    elif (ROOT / "golbez_exact_playable.sfc").is_file():
        check_rom(manifest, ROOT / "golbez_exact_playable.sfc")


if __name__ == "__main__":
    main()
