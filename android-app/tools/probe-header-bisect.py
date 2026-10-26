#!/usr/bin/env python3
"""Differential probe: reproduce the on-device failure and isolate the wrong header.

The device (build 25) received `{"statusCode":400,"data":"Internal server error."}` for every
request. This script sends the *known-good* header set next to the header set that build emitted,
then flips one header at a time so the culprit is unambiguous.

Usage: PROBE_CERT=/tmp/keys/testkey.x509.pem python3 tools/probe-header-bisect.py
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
PKG = os.environ.get("PROBE_APP_NAME", "co.asiven.vixentvpn")
VERSION = os.environ.get("PROBE_VERSION_CODE", "1004220")
DEVICE = os.environ.get("PROBE_DEVICE_ID", "b2ef7de041e0ea3f")
REPORT = []


def log(*parts):
    line = " ".join(str(p) for p in parts)
    REPORT.append(line)
    print(line, flush=True)


def request(path, headers):
    req = urllib.request.Request(BASE + path, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=25, context=ssl.create_default_context()) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return -1, f"{type(exc).__name__}: {exc}"


def short(text, limit=120):
    return " ".join(text.split())[:limit]


def main():
    pem = os.environ.get("PROBE_CERT", "testkey.x509.pem")
    if not os.path.exists(pem):
        log(f"!! cert {pem} missing")
        return 1
    der = subprocess.run(
        ["openssl", "x509", "-in", pem, "-outform", "DER"], capture_output=True, check=True
    ).stdout

    md5_b64 = base64.b64encode(hashlib.md5(der).digest()).decode()
    sha_single = hashlib.sha256(der).hexdigest()
    sha_double = hashlib.sha256(hashlib.sha256(der).digest()).hexdigest()

    base_good = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; Pixel 7 Build/TQ3A.230805.001)",
        "app_name": PKG,
        "version_code": VERSION,
        "seen": "0",
        "sign": md5_b64,
        "sha_hexadecimal": sha_double,
    }

    def variant(**overrides):
        h = dict(base_good)
        for key, value in overrides.items():
            key = key.replace("__", "-")
            if value is None:
                h.pop(key, None)
            else:
                h[key] = value
        return h

    cases = [
        ("correct (baseline headers)", base_good),
        ("build25: admobSeen + sha256 sign + pkg-prefixed sha", variant(
            seen=None,
            admobSeen="false",
            sign=base64.b64encode(hashlib.sha256(der).digest()).decode(),
            sha_hexadecimal=f"{PKG},{sha_single}",
        )),
        ("only sign = Base64(SHA256(DER))", variant(sign=base64.b64encode(hashlib.sha256(der).digest()).decode())),
        ("only sha = pkg,hex(SHA256(DER))", variant(sha_hexadecimal=f"{PKG},{sha_single}", sign=md5_b64)),
        ("only sha = hex(SHA256(DER)) single hash", variant(sha_hexadecimal=sha_single)),
        ("only seen missing, admobSeen: false", variant(seen=None, admobSeen="false")),
        ("only Content-Type missing", variant(**{"Content-Type": None})),
        ("only UA okhttp/3.12.13", variant(**{"User-Agent": "okhttp/3.12.13"})),
        ("only token header empty", variant(token="")),
        ("only Authorization bearer garbage", variant(Authorization="bearer Internal server error.")),
        ("only token=Internal server error.", variant(token="Internal server error.")),
    ]

    for label, headers in cases:
        status, text = request("/api/protocols", headers)
        try:
            payload = json.loads(text)
            items = payload.get("data") if isinstance(payload.get("data"), list) else None
            verdict = f"items={len(items)}" if items is not None else f"status={payload.get('status')} msg={payload.get('data')}"
        except Exception:  # noqa: BLE001
            verdict = short(text)
        log(f"{label:52s} -> HTTP {status} | {verdict}")

    # same for the token call, which is the first request the app makes
    for label, headers in (("token: correct", base_good), ("token: build25", cases[1][1])):
        status, text = request(f"/api/token?deviceId={DEVICE}", headers)
        log(f"{label:52s} -> HTTP {status} | {short(text)}")

    blob = "\n".join(REPORT)[-7000:]
    print("\n::warning title=header-bisect::" + urllib.parse.quote(blob, safe=""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
