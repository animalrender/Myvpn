#!/usr/bin/env python3
"""Dumps the NetEase DCC (ApkDex2C) native method table of `libstub.so`.

The packer removes the method bodies from the dex, marks them `native` and registers C++
implementations from a table that is handed to `np/dcc/protect/EntryPoint` inside
`JNI_OnLoad`. The table is a plain (relocated) array, so it can be read statically:

    JNI_OnLoad -> EntryPoint(ctx, "np/dcc/protect/EntryPoint", table, ...)

    table[0]              : {"stub", "(I)V", <code>}          (JNI entry trampoline)
    table[1..]            : {class_name, methods*, count}     (24-byte records)
    methods[i]            : {name, signature, code_address}   (24-byte records)

Usage:
    python3 dcc-native-map.py /path/to/libstub.so            # human readable
    python3 dcc-native-map.py /path/to/libstub.so --json     # machine readable
    python3 dcc-native-map.py /path/to/libstub.so --class com/v2ray/ang/ui/MainActivity
"""

import argparse
import json
import struct
import sys

from elftools.elf.elffile import ELFFile

R_AARCH64_RELATIVE = 1027


class Image:
    def __init__(self, path):
        self.raw = bytearray(open(path, "rb").read())
        self.elf = ELFFile(open(path, "rb"))
        self.segments = [
            (s["p_vaddr"], s["p_vaddr"] + s["p_filesz"], s["p_offset"]) for s in self.elf.iter_segments()
        ]
        self._apply_relocations()

    def _offset(self, vaddr):
        for start, end, file_offset in self.segments:
            if start <= vaddr < end:
                return file_offset + vaddr - start
        return None

    def _apply_relocations(self):
        """Rebuild `.data.rel.ro` so the tables read like they do after the dynamic loader ran."""
        section = self.elf.get_section_by_name(".rela.dyn")
        if section is None:
            return
        for relocation in section.iter_relocations():
            if relocation["r_info_type"] != R_AARCH64_RELATIVE:
                continue
            offset = self._offset(relocation["r_offset"])
            if offset is None:
                continue
            struct.pack_into("<Q", self.raw, offset, relocation["r_addend"])

    def read(self, vaddr, size=64):
        offset = self._offset(vaddr)
        return bytes(self.raw[offset:offset + size]) if offset is not None else b""

    def qword(self, vaddr):
        data = self.read(vaddr, 8)
        return struct.unpack("<Q", data)[0] if len(data) == 8 else 0

    def cstring(self, vaddr, limit=200):
        if not vaddr:
            return None
        data = self.read(vaddr, limit).split(b"\x00")[0]
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return None


def is_text_ptr(image, value):
    text = image.elf.get_section_by_name(".text")
    return bool(text) and text["sh_addr"] <= value < text["sh_addr"] + text["sh_size"]


def find_table(image):
    """The entry point call is the only place that references the string `np/dcc/protect/EntryPoint`."""
    needle = b"np/dcc/protect/EntryPoint\x00"
    position = image.raw.find(needle)
    if position < 0:
        raise SystemExit("np/dcc/protect/EntryPoint not found — not a DCC protected library?")
    # Resolve the file position to a virtual address, then look for the data.rel.ro block that
    # follows the same shape: {class, methods, count} triples with sane pointers.
    return position


def scan_records(image, start, limit=64):
    """Return the (class, methods, count) triples starting at `start`."""
    records = []
    address = start
    while len(records) < limit:
        name = image.cstring(image.qword(address))
        methods = image.qword(address + 8)
        count = image.qword(address + 16)
        in_method_area = any(
            section["sh_addr"] <= methods < section["sh_addr"] + section["sh_size"]
            for name in (".data", ".data.rel.ro")
            for section in [image.elf.get_section_by_name(name)] if section is not None
        )
        if not name or "/" not in name or not in_method_area or not 0 <= count < 500:
            break
        records.append((address, name, methods, count))
        address += 24
    return records


def guess_table_start(image):
    """Try every 8-byte aligned candidate between `.data.rel.ro` and `.data` and keep the
    longest valid chain (the class table lives in `.data.rel.ro`, its method arrays in `.data`)."""
    sections = [s for s in (image.elf.get_section_by_name(".data.rel.ro"),
                            image.elf.get_section_by_name(".data")) if s is not None]
    if not sections:
        raise SystemExit("no .data section")
    start = min(s["sh_addr"] for s in sections)
    end = max(s["sh_addr"] + s["sh_size"] for s in sections)
    best = ([], 0)
    for candidate in range(start, end, 8):
        records = scan_records(image, candidate)
        if len(records) > best[1]:
            best = (records, len(records))
    return best[0]


def methods_of(image, record):
    _, name, methods, count = record
    out = []
    for index in range(count):
        entry = methods + index * 24
        out.append(
            {
                "name": image.cstring(image.qword(entry)),
                "signature": image.cstring(image.qword(entry + 8)),
                "code": image.qword(entry + 16),
            }
        )
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("library")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--class", dest="klass")
    arguments = parser.parse_args()

    image = Image(arguments.library)
    find_table(image)  # sanity check only: the marker has to exist
    records = guess_table_start(image)
    if not records:
        raise SystemExit("no DCC table found")

    classes = [{"class": record[1], "methods": methods_of(image, record)} for record in records]
    if arguments.klass:
        classes = [entry for entry in classes if entry["class"] == arguments.klass]

    if arguments.json:
        json.dump(classes, sys.stdout, indent=1)
        print()
        return 0

    total = sum(len(entry["methods"]) for entry in classes)
    print(f"{len(classes)} classes / {total} native methods")
    for entry in classes:
        print(f"\n## {entry['class']}  ({len(entry['methods'])})")
        for method in entry["methods"]:
            code = f"0x{method['code']:x}" if method["code"] else "-"
            print(f"   {method['name']}{method['signature']}  {code}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
