#!/usr/bin/env python3
"""Fifth probe: full schema dump of `/api/v2/protocols` (the rich config endpoint).

Usage: PROBE_CERT=/tmp/keys/testkey.x509.pem python3 tools/probe-v2.py
"""
import base64
import hashlib
import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

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


def shape(value, depth=0):
    """Compact structural description of a JSON value."""
    if isinstance(value, dict):
        inner = ", ".join(f"{k}: {shape(v, depth + 1)}" for k, v in list(value.items())[:14])
        return "{" + inner + "}"
    if isinstance(value, list):
        if not value:
            return "[]"
        return f"[{len(value)} x {shape(value[0], depth + 1)}]"
    if isinstance(value, str):
        return f"str({len(value)})"
    return type(value).__name__


def decrypt_matrix(der, item):
    """Try to turn `value` back into a config with the per-item keys from /api/v2."""
    import binascii

    from Crypto.Cipher import AES  # pycryptodome is available on the runner

    value = str(item.get("value") or "")
    log(f"decrypt matrix: value len={len(value)}")
    try:
        ct = base64.b64decode(value + "=" * (-len(value) % 4))
    except Exception as exc:  # noqa: BLE001
        log(f"  base64 error {exc}")
        return
    log(f"  ct bytes={len(ct)} aligned16={len(ct) % 16 == 0}")

    raw_keys = {}
    for field in ("configKey", "routeKey", "endpointKey"):
        hexv = str(item.get(field) or "")
        if len(hexv) >= 32:
            try:
                raw_keys[field + ":hex"] = binascii.unhexlify(hexv)
            except Exception:  # noqa: BLE001
                pass
            raw_keys[field + ":ascii"] = hexv.encode()
            raw_keys[field + ":md5hex824"] = hashlib.md5(hexv.encode()).hexdigest()[8:24].encode()
    keys = {}
    for name, kb in raw_keys.items():
        if len(kb) in (16, 24, 32):
            keys[name] = kb
    keys["md5(der)"] = hashlib.md5(der).digest()
    keys["sha256(der)"] = hashlib.sha256(der).digest()

    def describe(pt):
        if pt[:2] == b"\x1f\x8b":
            return "GZIP!"
        try:
            txt = pt.decode("utf-8")
        except Exception:  # noqa: BLE001
            return None
        pr = sum(1 for ch in txt if ch.isprintable() or ch in "\n\t\r ")
        if pr / max(1, len(txt)) > 0.92:
            return "TEXT " + txt[:150].replace("\n", " ")
        return None

    hits = 0
    for name, key in keys.items():
        modes = {"ECB": None, "CBC0": b"\0" * 16, "CBCct": ct[:16], "CBCkey": key[:16]}
        for mode, iv in modes.items():
            try:
                if mode == "ECB":
                    pt = AES.new(key, AES.MODE_ECB).decrypt(ct)
                else:
                    pt = AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
            except Exception:  # noqa: BLE001
                continue
            res = describe(pt)
            if res:
                hits += 1
                log(f"  HIT {name} {mode} -> {res}")
        for mode in ("CTR", "CFB", "OFB"):
            try:
                if mode == "CTR":
                    pt = AES.new(key, AES.MODE_CTR, nonce=b"", initial_value=int.from_bytes(ct[:16], "big")).decrypt(ct[16:])
                elif mode == "CFB":
                    pt = AES.new(key, AES.MODE_CFB, iv=ct[:16]).decrypt(ct[16:])
                else:
                    pt = AES.new(key, AES.MODE_OFB, iv=ct[:16]).decrypt(ct[16:])
            except Exception:  # noqa: BLE001
                continue
            res = describe(pt)
            if res:
                hits += 1
                log(f"  HIT {name} {mode}(iv=ct) -> {res}")
    log(f"  hits={hits}")


def main():
    pem = os.environ.get("PROBE_CERT", "testkey.x509.pem")
    if not os.path.exists(pem):
        log(f"!! cert {pem} missing")
        return 1
    der = subprocess.run(
        ["openssl", "x509", "-in", pem, "-outform", "DER"], capture_output=True, check=True
    ).stdout
    h = headers(der)

    status, text = get("/api/v2/protocols", h)
    log(f"GET /api/v2/protocols -> {status}, {len(text)} bytes")
    try:
        payload = json.loads(text)
    except Exception as exc:  # noqa: BLE001
        log(f"parse error {exc}: {text[:300]}")
        print("\n::warning title=v2-schema::" + urllib.parse.quote("\n".join(REPORT)[-7000:], safe=""))
        return 0

    data = payload.get("data")
    log(f"top keys: {list(payload.keys())}; status={payload.get('status')} statusCode={payload.get('statusCode')}")
    log(f"data type: {type(data).__name__}")
    items = data if isinstance(data, list) else []
    if isinstance(data, dict):
        log("data(keys)=" + ", ".join(list(data.keys())[:30]))
        for key in list(data.keys())[:6]:
            log(f"  {key} -> {shape(data[key])}")
        # try to find the list of servers inside
        for key, val in data.items():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                items = val
                log(f"  ↳ using data['{key}'] as item list ({len(val)} items)")
                break
    if items:
        log(f"items: {len(items)}")
        log("item shape: " + shape(items[0])[:3500])
        first = items[0]
        pretty = json.dumps(
            {k: (v if not isinstance(v, str) or len(v) < 300 else f"<{len(v)} chars>") for k, v in first.items()},
            ensure_ascii=False,
            indent=1,
        )
        log("first item (long strings elided):\n" + pretty[:3500])
        blob = json.dumps(first, ensure_ascii=False)
        for probe in ("vmess://", "vless://", "trojan://", "ss://", "hysteria", "outbounds", "inbounds"):
            log(f"first item contains {probe!r}: {probe in blob}")
        # print the raw first item truncated, so field names + short values are visible
        log("raw first item[:400]=" + blob[:400])
        decrypt_matrix(der, first)

    print("\n::warning title=v2-schema::" + urllib.parse.quote("\n".join(REPORT)[-7000:], safe=""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
