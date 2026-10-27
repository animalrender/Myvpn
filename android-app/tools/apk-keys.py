#!/usr/bin/env python3
"""Reproduces every key and cipher that `base.apk` (co.asiven.vixentvpn 3.2.0, `1004220`) uses.

Two independent ciphers live in the APK.

1. **ScKit string cipher** — `Lˊـˉˋـﹶ/…;->יٴˊˆᐧٴﹶˈʽٴᵔˋᴵˎᵔיﹳˈˈ(String, String)`.
   Every user-visible literal, log tag and native field/method name is stored as
   `ScKit-<hex>` and decrypted on first touch:

       algorithm   : AES/ECB/PKCS5Padding (16-byte block, `Cipher.getInstance("AES")`)
       passphrase  : the second argument, **including** its `ScKit-` prefix
       AES key     : encodePass() == lower(MD5(passphrase))[8:24]  (16 ASCII chars)
       ciphertext  : first argument minus the `ScKit-` prefix, hex decoded

   Example: `ScKit-4c24019abf6ca137fa83af683f558bb9` + `ScKit-fa103df02f265218`
            -> "Serializing "

2. **URL / config cipher** — `Lz/d;->v(String, String)String`, duplicated as `Ll3/a;->m`.

       algorithm   : AES/CBC/PKCS5Padding, `Base64.decode(src, 1)`, key == IV == first 16 bytes
       only vendor caller: `Lk4/d;->f(String)` passes the package name, therefore

           "co.asiven.vixentvpn" + tyBT242ubuxXa/YbRfrkGQVlNflSzufT6Q7TJTa5t0M=
               -> https://managev1.xyz

Usage:
    pip install pycryptodome androguard
    python3 apk-keys.py --apk-dir /tmp/apk                  # summary + samples
    python3 apk-keys.py --apk-dir /tmp/apk --dump sckit.tsv  # ciphertext <TAB> plaintext
    python3 apk-keys.py --config-blob tyBT242ubuxXa/...      # only the URL cipher
"""

import argparse
import collections
import re
import base64
import hashlib
import logging
import os
import sys

try:
    from Crypto.Cipher import AES
except ImportError:  # pragma: no cover - dependency hint
    sys.exit("pycryptodome is required: pip install pycryptodome")

CONFIG_BLOB = "tyBT242ubuxXa/YbRfrkGQVlNflSzufT6Q7TJTa5t0M="
PACKAGE = "co.asiven.vixentvpn"
# The method name is enough to recognise the call site and it survives the packer's mangling of
# the class name (which is a long run of Arabic/Persian diacritics).
SCKIT_METHOD = "יٴˊˆᐧٴﹶˈʽᴵٴᵔˋᴵˎᵔיﹳˈˈ"
LITERAL_RE = re.compile(r'"(ScKit-[0-9a-fA-F]+)"')


def sckit_decrypt(payload: str, passphrase: str):
    """AES/ECB/PKCS#7 with key = lower(MD5(passphrase))[8:24]; returns None when it is not a
    ScKit literal (odd hex, wrong block size or invalid padding)."""
    if not payload.startswith("ScKit-") or not passphrase.startswith("ScKit-"):
        return None
    body = payload[len("ScKit-"):]
    if len(body) % 2:
        body = "0" + body
    try:
        ciphertext = bytes.fromhex(body)
    except ValueError:
        return None
    if not ciphertext or len(ciphertext) % 16:
        return None
    key = hashlib.md5(passphrase.encode()).hexdigest().lower()[8:24].encode()
    plain = AES.new(key, AES.MODE_ECB).decrypt(ciphertext)
    pad = plain[-1]
    if not (1 <= pad <= 16 and plain[-pad:] == bytes([pad]) * pad):
        return None
    return plain[:-pad].decode("utf-8", "replace")


def vendor_decrypt(blob: str, key_material: str):
    """`Lz/d;->v`: AES/CBC/PKCS5 with key == IV == first 16 bytes of `key_material`."""
    padded = (key_material.encode() + b"\x00" * 16)[:16]
    data = base64.b64decode(blob + "=" * (-len(blob) % 4))
    plain = AES.new(padded, AES.MODE_CBC, iv=padded).decrypt(data)
    pad = plain[-1]
    if 1 <= pad <= 16 and plain[-pad:] == bytes([pad]) * pad:
        plain = plain[:-pad]
    return plain.decode("utf-8", "replace")


def collect_call_sites(dex_path):
    """Returns the `(ciphertext, passphrase)` pairs that the ScKit routine is invoked with.

    The pairing has to come from the bytecode: the two `const-string`s are adjacent to the
    `invoke-static` and the passphrase is different for almost every literal, so a byte-level
    proximity heuristic cannot work (the string pool is shared by the whole file).
    """
    logging.disable(logging.CRITICAL)
    from androguard.core.dex import DEX

    with open(dex_path, "rb") as handle:
        dex = DEX(handle.read())

    pairs = []
    for klass in dex.get_classes():
        for method in klass.get_methods():
            code = method.get_code()
            if not code:
                continue
            instructions = list(code.get_bc().get_instructions())
            for index, instruction in enumerate(instructions):
                output = instruction.get_output() or ""
                if f"->{SCKIT_METHOD}(" not in output:
                    continue
                literals = []
                for previous in reversed(instructions[max(0, index - 6):index]):
                    found = LITERAL_RE.findall(previous.get_output() or "")
                    literals.extend(found)
                    if len(literals) >= 2:
                        break
                if len(literals) >= 2:
                    pairs.append((literals[1], literals[0]))
    return pairs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apk-dir", help="unzipped APK directory (classes*.dex and lib/)")
    parser.add_argument("--config-blob", default=CONFIG_BLOB, help="base64 blob fed to Lz/d;->v")
    parser.add_argument("--package", default=PACKAGE, help="key material for Lz/d;->v")
    parser.add_argument("--dump", help="write `ciphertext<TAB>plaintext` to this file")
    arguments = parser.parse_args()

    print(f"[Lz/d;->v] key=IV=first16({arguments.package!r}) "
          f"-> {vendor_decrypt(arguments.config_blob, arguments.package)!r}")
    if not arguments.apk_dir:
        return 0

    total = failed = 0
    corpus = {}
    for name in sorted(os.listdir(arguments.apk_dir)):
        path = os.path.join(arguments.apk_dir, name)
        if not (name.startswith("classes") and name.endswith(".dex")):
            continue
        pairs = collect_call_sites(path)
        ok = 0
        failures = collections.Counter()
        for cipher, passphrase in pairs:
            plain = sckit_decrypt(cipher, passphrase)
            if plain is None:
                failures["not-ScKit"] += 1
                continue
            ok += 1
            corpus[cipher] = plain
        total += len(pairs)
        failed += sum(failures.values())
        print(f"[ScKit] {name}: {len(pairs)} call sites, {ok} decrypted, "
              f"{sum(failures.values())} not ScKit")

    print(f"[ScKit] total call sites: {total}, unique plaintexts: {len(corpus)}")
    for sample in sorted(corpus.values(), key=len)[:5]:
        print(f"   {sample[:100]!r}")

    if arguments.dump:
        with open(arguments.dump, "w", encoding="utf-8") as handle:
            for cipher, plain in sorted(corpus.items()):
                handle.write(f"{cipher}\t{plain}\n")
        print(f"wrote {arguments.dump}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
