#!/usr/bin/env python3
"""Sixth probe: cross-check v1/v2 payloads and try every plausible key pairing.

Hypothesis under test: the per-item `configKey` / `routeKey` / `endpointKey` from
`/api/v2/protocols` are the AES material for the `value` blobs (either the v2 blob
itself or the legacy v1 blob for the same server).

Usage: PROBE_CERT=/tmp/keys/testkey.x509.pem python3 tools/probe-v2b.py
"""
import base64
import binascii
import hashlib
import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

from Crypto.Cipher import AES

BASE = os.environ.get("PROBE_BASE", "https://managev1.xyz")
APP_NAME = os.environ.get("PROBE_APP_NAME", "co.asiven.vixentvpn")
VERSION_CODE = os.environ.get("PROBE_VERSION_CODE", "1004220")
UA = "Dalvik/2.1.0 (Linux; U; Android 13; Pixel 7 Build/TQ3A.230805.001"
REPORT = []


def log(*parts):
    line = " ".join(str(p) for p in parts)
    REPORT.append(line)
    print(line, flush=True)


def headers(der):
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": UA,
        "app_name": APP_NAME,
        "version_code": VERSION_CODE,
        "seen": "0",
        "sign": base64.b64encode(hashlib.md5(der).digest()).decode(),
        "sha_hexadecimal": hashlib.sha256(hashlib.sha256(der).digest()).hexdigest(),
    }


def get(path, hdrs):
    req = urllib.request.Request(BASE + path, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return -1, f"{type(exc).__name__}: {exc}"


def load(path, hdrs):
    status, text = get(path, hdrs)
    try:
        data = json.loads(text).get("data")
    except Exception:  # noqa: BLE001
        data = None
    return status, (data if isinstance(data, list) else []), text


def maybe_plain(pt):
    if pt[:2] == b"\x1f\x8b":
        import zlib

        try:
            return "GZIP " + repr(zlib.decompress(pt, 31)[:100])
        except Exception:  # noqa: BLE001
            return None
    try:
        txt = pt.decode("utf-8")
    except Exception:  # noqa: BLE001
        return None
    if len(txt) < 16:
        return None
    printable = sum(1 for ch in txt if ch.isprintable() or ch in "\n\t\r ")
    if printable / len(txt) < 0.98:
        return None
    if ("{" in txt and "}" in txt) or "://" in txt or "outbounds" in txt:
        return txt[:140].replace("\n", " ")
    return None


def try_decrypt(label, b64value, keys):
    try:
        ct = base64.b64decode(b64value + "=" * (-len(b64value) % 4))
    except Exception:  # noqa: BLE001
        return 0
    if len(ct) < 32:
        return 0
    hits = 0
    for name, key in keys.items():
        modes = [("ECB", None), ("CBC0", b"\0" * 16)]
        if len(ct) >= 16:
            modes += [("CBCct", ct[:16]), ("CBCk", key[:16])]
        for mode, iv in modes:
            try:
                pt = (
                    AES.new(key, AES.MODE_ECB).decrypt(ct)
                    if iv is None
                    else AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
                )
            except Exception:  # noqa: BLE001
                continue
            n = pt[-1]
            body = pt[:-n] if 1 <= n <= 16 and pt[-n:] == bytes([n]) * n else pt
            res = maybe_plain(body) or maybe_plain(pt)
            if res:
                log(f"  HIT {label} key={name} mode={mode} -> {res}")
                hits += 1
        for mode in ("CTR", "CFB", "OFB"):
            for ivname, iv in (("iv0", b"\0" * 16), ("ivct", ct[:16])):
                try:
                    if mode == "CTR":
                        pt = AES.new(key, AES.MODE_CTR, nonce=b"", initial_value=int.from_bytes(iv, "big")).decrypt(ct)
                    elif mode == "CFB":
                        pt = AES.new(key, AES.MODE_CFB, iv=iv).decrypt(ct)
                    else:
                        pt = AES.new(key, AES.MODE_OFB, iv=iv).decrypt(ct)
                except Exception:  # noqa: BLE001
                    continue
                res = maybe_plain(pt)
                if res:
                    log(f"  HIT {label} key={name} mode={mode}/{ivname} -> {res}")
                    hits += 1
    return hits


def keys_from(item):
    keys = {}
    for field in ("configKey", "routeKey", "endpointKey"):
        hexv = str(item.get(field) or "")
        if len(hexv) < 32:
            continue
        try:
            raw = binascii.unhexlify(hexv)
        except Exception:  # noqa: BLE001
            continue
        if len(raw) in (16, 24, 32):
            keys[field + ":hex"] = raw
        if len(hexv) in (16, 24, 32):
            keys[field + ":ascii"] = hexv.encode()
        keys[field + ":md5hex824"] = hashlib.md5(hexv.encode()).hexdigest()[8:24].encode()
        keys[field + ":sha16"] = hashlib.sha256(hexv.encode()).digest()[:16]
    ck = str(item.get("configKey") or "")
    rk = str(item.get("routeKey") or "")
    ek = str(item.get("endpointKey") or "")
    for name, s in (("ck+rk", ck + rk), ("rk+ck", rk + ck), ("ck+ek", ck + ek), ("ckrk ek", ck + rk + ek)):
        keys[name + ":md5"] = hashlib.md5(s.encode()).digest()
        keys[name + ":sha16"] = hashlib.sha256(s.encode()).digest()[:16]
    return keys


def main():
    pem = os.environ.get("PROBE_CERT", "testkey.x509.pem")
    if not os.path.exists(pem):
        log(f"!! cert {pem} missing")
        return 1
    der = subprocess.run(
        ["openssl", "x509", "-in", pem, "-outform", "DER"], capture_output=True, check=True
    ).stdout
    h = headers(der)

    # extra endpoint shapes before the heavy part
    for path in (
        "/api/v3/protocols",
        "/api/v4/protocols",
        "/api/v2/configs",
        "/api/v2/servers",
        "/api/v2/setting",
        "/api/v1/protocols",
    ):
        status, text = get(path, h)
        log(f"GET {path} -> {status} | {' '.join(text.split())[:140]}")

    st1, v1, _ = load("/api/protocols", h)
    st2, v2, raw2 = load("/api/v2/protocols", h)
    log(f"v1: {st1} {len(v1)} items; v2: {st2} {len(v2)} items")

    by_server_v1 = {}
    for it in v1:
        by_server_v1.setdefault(it.get("serverId"), it)
    by_server_v2 = {}
    for it in v2:
        by_server_v2.setdefault(it.get("serverId"), it)
    shared = sorted(set(by_server_v1) & set(by_server_v2), key=lambda x: (x is None, x))
    log(f"servers present in both: {len(shared)} -> {shared[:12]}")

    total = 0
    for sid in shared[:6]:
        a, b = by_server_v1[sid], by_server_v2[sid]
        total += try_decrypt(f"v1/sid={sid}", str(a.get("value") or ""), keys_from(b))
        total += try_decrypt(f"v2/sid={sid}", str(b.get("value") or ""), keys_from(b))
        total += try_decrypt(f"v1/sid={sid}/v1keys", str(a.get("value") or ""), keys_from(a))
        total += try_decrypt(f"v2/sid={sid}/v1keys", str(b.get("value") or ""), keys_from(a))
    log(f"decrypt hits: {total}")

    # what do the keys look like when decoded? (are they hex of ASCII text?)
    if v2:
        sample = v2[0]
        for field in ("configKey", "routeKey", "endpointKey"):
            hexv = str(sample.get(field) or "")
            try:
                raw = binascii.unhexlify(hexv)
            except Exception:  # noqa: BLE001
                continue
            printable = sum(1 for c in raw if 32 <= c < 127)
            log(f"{field}: len={len(hexv)} raw={len(raw)}B printable_bytes={printable} first16={raw[:16].hex()}")

    blob = "\n".join(REPORT)[-7000:]
    print("\n::warning title=v2b-report::" + urllib.parse.quote(blob, safe=""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
