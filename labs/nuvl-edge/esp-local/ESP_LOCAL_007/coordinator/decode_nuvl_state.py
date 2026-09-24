#!/usr/bin/env python3
"""Decode a raw nuvl_state partition dump the same way
ESP_LOCAL_007_CONCURRENT.c's validate_state_record() does:

    uint32_t magic;       // must be 0x4E55564C
    uint16_t version;     // must be 1
    uint8_t  state;       // 1 = UNSPENT, 2 = SPENT
    uint8_t  reserved;    // must be 0
    uint8_t  authority_id[32];
    uint32_t crc32;       // CRC-32/zlib over the preceding 40 bytes

Scans the whole dump for the magic bytes rather than assuming a fixed
offset, since NVS entry placement isn't guaranteed to stay put across
writes. Verifies CRC exactly as the firmware does (nuvl_crc32() uses the
standard reflected CRC-32 with init/final 0xFFFFFFFF -- the same
algorithm as zlib.crc32/binascii.crc32).
"""
import struct
import sys
import zlib

MAGIC = 0x4E55564C
STATE_NAMES = {1: "UNSPENT", 2: "SPENT"}


def decode(path):
    data = open(path, "rb").read()
    magic_bytes = struct.pack("<I", MAGIC)

    found = []
    start = 0
    while True:
        idx = data.find(magic_bytes, start)
        if idx == -1:
            break
        found.append(idx)
        start = idx + 1

    if not found:
        print(f"{path}: no NUVL magic found in {len(data)} bytes")
        return

    for idx in found:
        record = data[idx:idx + 44]
        if len(record) < 44:
            continue

        magic, version, state, reserved = struct.unpack_from("<IHBB", record, 0)
        authority_id = record[8:40]
        stored_crc = struct.unpack_from("<I", record, 40)[0]
        computed_crc = zlib.crc32(record[0:40]) & 0xFFFFFFFF

        print(f"{path}  @offset {idx}")
        print(f"  magic     = 0x{magic:08X} ({'OK' if magic == MAGIC else 'MISMATCH'})")
        print(f"  version   = {version} ({'OK' if version == 1 else 'MISMATCH'})")
        print(f"  state     = {state} ({STATE_NAMES.get(state, 'INVALID')})")
        print(f"  reserved  = {reserved} ({'OK' if reserved == 0 else 'MISMATCH'})")
        print(f"  authority_id = {authority_id.hex()}")
        print(f"  crc stored   = {stored_crc:08x}")
        print(f"  crc computed = {computed_crc:08x} ({'OK' if stored_crc == computed_crc else 'MISMATCH'})")
        print()


if __name__ == "__main__":
    for p in sys.argv[1:]:
        decode(p)
