#!/usr/bin/env python3
"""Build an original, one-ship DTE inspection mission; no retail records are copied."""
from pathlib import Path
import argparse
import hashlib
import json
import struct


def inspection_mission() -> bytes:
    strings = bytearray()

    def name(text: str) -> int:
        at = len(strings)
        strings.extend(text.encode("ascii") + b"\0")
        return at

    start_name = name("(F)InspectionStart")
    player_name = name("Crusader - Inspection")
    group_name = name("(FG)Inspection")

    # DTE Ship: 0x4c bytes. No launch, pilot, formation or camera curve.
    ship = bytearray(0x4C)
    struct.pack_into("<IHH", ship, 0, 0, player_name, 0)
    ship[0x14:0x18] = bytes([0, 0xFF, 0, 0])
    struct.pack_into("<H", ship, 0x18, 3)  # Crusader
    struct.pack_into("<HBB", ship, 0x28, 0xFFFF, 0xFF, 0xFF)
    struct.pack_into("<IHH", ship, 0x30, 0xFFFFFFFF, 0xFFFF, 0xFFFF)
    ship[0x3C:0x48] = bytes.fromhex("ff ff 00 00 ff ff ff ff 00 00 00 00")

    group = struct.pack("<HHHHBBHII", 1, 0, group_name, 0, 0, 1, 0, 0, 0xFF19FFFF)
    objects = struct.pack("<BBHI", 0, 0, 0xFFFF, 0) + struct.pack("<BBHI", 1, 0, 0xFFFF, 0)
    # push_flight_group 0; CreateFlightGroup; push_byte 1; return.
    instructions = bytes.fromhex("2d 00 21 03 32 01 43")
    length = (2 + len(instructions) + 3) & ~3
    script = struct.pack("<H", length) + instructions
    script += b"\0" * (length - len(script))
    part = bytearray(0x1C)
    struct.pack_into("<H", part, 0, start_name)
    struct.pack_into("<H", part, 0x0A, 0)
    part[0x0C] = 1
    struct.pack_into("<H", part, 0x10, len(script) // 2)
    title = b"Recommissioned - Crusader Inspection"
    mission_name = struct.pack("<4sHH", b"ORMN", 1, len(title)) + title + b"\0"
    sections = {
        0: (len(strings), bytes(strings)),
        3: (1, bytes(ship)),
        4: (1, group),
        6: (len(script) // 2, script),
        7: (2, objects),
        8: (1, bytes(part)),
        10: (len(script), bytes(len(script))),
        21: (len(mission_name), mission_name),
    }
    image = bytearray(27 * 8)
    for index in range(27):
        if index in sections:
            count, payload = sections[index]
            image.extend(b"\0" * (-len(image) % 4))
            offset = len(image)
            image.extend(payload)
        else:
            count, offset = 0, 0xFFFF
        struct.pack_into("<HBBI", image, index * 8, count, 0, 15, offset)
    return bytes(image)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent / "mods/recommissioned-inspection/mission990.dte")
    args = parser.parse_args()
    data = inspection_mission()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(data)
    manifest = {
        "mission": 990,
        "name": "Recommissioned - Crusader Inspection",
        "player_ship_type": 3,
        "placed_ships": 1,
        "other_ships": 0,
        "triggers": 0,
        "script": "Create only the player's flight group; return.",
        "retail_mission_data_copied": False,
        "sha256": hashlib.sha256(data).hexdigest(),
        "status": "requires runtime verification",
    }
    audit = Path(__file__).resolve().parent / "audit"
    audit.mkdir(exist_ok=True)
    (audit / "inspection_mission.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Built {args.output}: {len(data)} bytes")


if __name__ == "__main__":
    main()
