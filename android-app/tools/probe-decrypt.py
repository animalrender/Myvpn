#!/usr/bin/env python3
"""Verifies the decryption of `Protocol.value` for **every** row of `/api/protocols`.

`value` is `AES/CBC/PKCS5Padding` (base64) whose passphrase is the row id rendered as
`"key_<id>"` and right-padded with NULs to 16 bytes; the IV equals the key. The plaintext is a
share link or a full Xray config.

This probe prints **aggregates only** (counts per scheme / outbound protocol, badge of the
decrypted size) — never hosts, ports, uuids or keys — so the log can live in a public repo.
"""

import base64
import collections
import hashlib
import json
import os
import sys
import urllib.request

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

BASE = "https://managev1.xyz"
APP_NAME = "co.asiven.vixentvpn"
VERSION_CODE = "1004220"
PATH = "/api/v2/protocols"


def headers():
    import ssl

    cert = os.environ.get("PROBE_CERT", "/tmp/keys/testkey.x509.pem")
    der = base64.b64decode(ssl.PEM_cert_to_DER_cert(open(cert).read()))
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "app_name": APP_NAME,
        "version_code": VERSION_CODE,
        "seen": "0",
        "sign": base64.b64encode(hashlib.md5(der).digest()).decode(),
        "sha_hexadecimal": hashlib.sha256(hashlib.sha256(der).digest()).hexdigest(),
        "User-Agent": "okhttp/4.12.0",
    }


def key_for(protocol_id):
    raw = ("key_%d" % protocol_id).encode()
    return raw[:16].ljust(16, b"\0")


def decrypt(value_b64, protocol_id):
    data = base64.b64decode(value_b64 + "=" * (-len(value_b64) % 4))
    if not data or len(data) % 16:
        return None
    key = key_for(protocol_id)
    out = Cipher(algorithms.AES(key), modes.CBC(key)).decryptor().update(data)
    pad = out[-1]
    plain = out[:-pad] if 0 < pad <= 16 else out
    return plain.decode("utf-8", "replace")


def describe(plain):
    text = plain.strip()
    if text.startswith("{"):
        try:
            obj = json.loads(text)
        except Exception:
            return "json-invalid", {}
        outs = obj.get("outbounds") or []
        proto = outs[0].get("protocol") if outs and isinstance(outs[0], dict) else "?"
        stream = (outs[0].get("streamSettings") or {}) if outs and isinstance(outs[0], dict) else {}
        nets = stream.get("network", "?")
        sec = stream.get("security", "?")
        return "json", {"protocol": proto, "network": nets, "security": sec,
                        "inbounds": len(obj.get("inbounds") or []),
                        "outbounds": len(outs)}
    scheme = text.split("://", 1)[0].lower() if "://" in text else "unknown"
    return scheme, {"length": len(text), "has_remark": "#" in text}


def main():
    request = urllib.request.Request(BASE + PATH, headers=headers())
    with urllib.request.urlopen(request, timeout=40) as response:
        payload = json.loads(response.read())
    rows = payload.get("data") or []
    print(f"rows: {len(rows)}")

    kinds = collections.Counter()
    protos = collections.Counter()
    fails = []
    detail = []
    for row in rows:
        rid = row.get("id")
        plain = decrypt(row.get("value") or "", rid)
        if plain is None:
            fails.append((rid, "cipher-error"))
            continue
        kind, meta = describe(plain)
        kinds[kind] += 1
        detail.append((rid, row.get("price"), kind, meta))
        if kind == "json":
            protos["%s/%s/%s" % (meta["protocol"], meta["network"], meta["security"])] += 1
        else:
            protos["%s:%s" % (kind, "uri")] += 1
        if kind in ("unknown", "json-invalid"):
            fails.append((rid, kind, plain[:60].replace("\n", " ")))

    print("scheme counts:", dict(kinds))
    print("transport counts:", dict(protos))
    print("failures:", len(fails))
    for row in fails[:20]:
        print("  ", row)
    printable_ratio = sum(1 for k in kinds if not k.startswith("json")) / max(1, len(rows))
    print("decrypt-coverage: %.2f%%" % (100 * (len(rows) - len(fails)) / max(1, len(rows))))
    print("share-link share: %.2f%%" % (100 * printable_ratio))

    # Per-row composition (no hosts, no uuids, no keys — only the shape of each payload), so the
    # client can tell in advance which rows its core can dial.
    with open(os.environ.get("DECRYPT_DETAIL", "/tmp/decrypt-detail.txt"), "w",
              encoding="utf-8") as handle:
        handle.write("# id, price, scheme, transport/security (یا طول لینک)\n")
        for rid, price, kind, meta in detail:
            if kind == "json":
                handle.write("%s,%s,json,%s/%s/%s,outbounds=%s,inbounds=%s\n" % (
                    rid, price, meta.get("protocol"), meta.get("network"),
                    meta.get("security"), meta.get("outbounds"), meta.get("inbounds")))
            else:
                handle.write("%s,%s,%s,len=%s,remark=%s\n" % (
                    rid, price, kind, meta.get("length"), meta.get("has_remark")))
    print("detail written for %d rows" % len(detail))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
