#!/usr/bin/env python3
"""Seventh probe: does an older `version_code` still get plaintext configs?

The backend encrypts `value` for current clients. Legacy client versions often
keep a compatibility path that returns plaintext links, so sweep a range of
version codes / app names / hint parameters and look for anything readable.

Usage: PROBE_CERT=/tmp/keys/testkey.x509.pem python3 tools/probe-version-sweep.py
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
UA = "Dalvik/2.1.0 (Linux; U; Android 13; Pixel 7 Build/TQ3A.230805.001"
APP_NAMES = ["co.asiven.vixentvpn", "co.asiven.vixentvpn.debug", "co.dev"]
VERSIONS = ["1", "10", "1000", "1004000", "1004100", "1004200", "1004210", "1004220", "4220", "3", "320", "9999999"]
PATHS = ["/api/protocols", "/api/v2/protocols"]
REPORT = []


def log(*parts):
    line = " ".join(str(p) for p in parts)
    REPORT.append(line)
    print(line, flush=True)


def headers(der, app_name, version):
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": UA,
        "app_name": app_name,
        "version_code": version,
        "seen": "0",
        "sign": base64.b64encode(hashlib.md5(der).digest()).decode(),
        "sha_hexadecimal": hashlib.sha256(hashlib.sha256(der).digest()).hexdigest(),
    }


def get(path, hdrs):
    req = urllib.request.Request(BASE + path, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context()) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return -1, f"{type(exc).__name__}: {exc}"


def classify(value):
    """Describe what the `value` blob looks like."""
    if not value:
        return "empty"
    head = value[:64]
    if value.startswith("ScKit-"):
        return "ScKit-hex"
    if any(tok in value for tok in ("vmess://", "vless://", "trojan://", "ss://")):
        return "URI-PLAINTEXT"
    if value.lstrip().startswith("{"):
        return "JSON-PLAINTEXT"
    alphabet = set(value)
    if alphabet <= set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="):
        return f"base64(len={len(value)})"
    return f"other(len={len(value)},head={head[:24]})"


def main():
    pem = os.environ.get("PROBE_CERT", "testkey.x509.pem")
    if not os.path.exists(pem):
        log(f"!! cert {pem} missing")
        return 1
    der = subprocess.run(
        ["openssl", "x509", "-in", pem, "-outform", "DER"], capture_output=True, check=True
    ).stdout

    interesting = 0
    for app_name in APP_NAMES:
        for version in VERSIONS:
            for path in PATHS:
                status, text = get(path, headers(der, app_name, version))
                try:
                    payload = json.loads(text)
                except Exception:  # noqa: BLE001
                    log(f"{app_name} v{version} {path} -> {status} | {' '.join(text.split())[:110]}")
                    continue
                data = payload.get("data")
                if isinstance(data, list) and data:
                    kinds = {classify(str(it.get("value") or "")) for it in data[:8]}
                    log(f"{app_name} v{version} {path} -> {status} items={len(data)} value-shapes={sorted(kinds)}")
                    if any(k in ("URI-PLAINTEXT", "JSON-PLAINTEXT", "ScKit-hex") for k in kinds):
                        interesting += 1
                        it = data[0]
                        log("   SAMPLE " + json.dumps({k: (v if not isinstance(v, str) or len(v) < 120 else v[:120] + "…") for k, v in it.items()}, ensure_ascii=False)[:600])
                else:
                    log(f"{app_name} v{version} {path} -> {status} | {' '.join(text.split())[:110]}")

    # hint parameters on the default version
    h = headers(der, "co.asiven.vixentvpn", "1004220")
    for path in ("/api/protocols?plain=1", "/api/protocols?raw=1", "/api/protocols?v=1",
                 "/api/v2/protocols?plain=1", "/api/v2/protocols?raw=1", "/api/protocols?decrypt=1"):
        status, text = get(path, h)
        try:
            data = json.loads(text).get("data")
        except Exception:  # noqa: BLE001
            data = None
        shape = classify(str((data or [{}])[0].get("value") or "")) if isinstance(data, list) and data else "-"
        log(f"hint {path} -> {status} shape={shape}")

    log(f"interesting responses: {interesting}")
    blob = "\n".join(REPORT)[-7000:]
    print("\n::warning title=version-sweep::" + urllib.parse.quote(blob, safe=""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
