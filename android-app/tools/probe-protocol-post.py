#!/usr/bin/env python3
"""Third probe: POST /api/protocols expects a protocol id — find the right body shape
and check whether the response carries a usable (plaintext) config.

Usage: PROBE_CERT=/tmp/keys/testkey.x509.pem python3 tools/probe-protocol-post.py
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
DEVICE_ID = os.environ.get("PROBE_DEVICE_ID", "b2ef7de041e0ea3f")
REPORT = []


def log(*parts):
    line = " ".join(str(p) for p in parts)
    REPORT.append(line)
    print(line, flush=True)


def cert_der(path):
    return subprocess.run(
        ["openssl", "x509", "-in", path, "-outform", "DER"], capture_output=True, check=True
    ).stdout


def headers(der):
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; Pixel 7 Build/TQ3A.230805.001)",
        "app_name": APP_NAME,
        "version_code": VERSION_CODE,
        "seen": "0",
        "sign": base64.b64encode(hashlib.md5(der).digest()).decode(),
        "sha_hexadecimal": hashlib.sha256(hashlib.sha256(der).digest()).hexdigest(),
    }


def request(method, path, hdrs, body=None, timeout=25):
    req = urllib.request.Request(
        BASE + path,
        data=(body.encode() if isinstance(body, str) else body),
        headers=hdrs,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return -1, f"{type(exc).__name__}: {exc}"


def short(text, limit=260):
    return " ".join(text.split())[:limit]


def main():
    pem = os.environ.get("PROBE_CERT", "testkey.x509.pem")
    if not os.path.exists(pem):
        log(f"!! cert {pem} missing")
        return 1
    h = headers(cert_der(pem))
    status, text = request("GET", "/api/protocols", h)
    items = json.loads(text).get("data") or []
    log(f"protocols -> {status}, items={len(items)}")
    if not items:
        print("\n::warning title=post-probe::" + urllib.parse.quote("no items", safe=""))
        return 1
    item = items[0]
    pid, sid = item["id"], item.get("serverId")
    log(f"sample: id={pid} serverId={sid} name={item.get('name')} price={item.get('price')} usage={item.get('usage')}")

    bodies = [
        {"id": pid},
        {"id": pid, "deviceId": DEVICE_ID},
        {"deviceId": DEVICE_ID, "protocolId": pid},
        {"protocol_id": pid},
        {"protocolId": pid},
        {"id": pid, "serverId": sid},
        {"id": pid, "deviceId": DEVICE_ID, "serverId": sid},
        {"data": {"id": pid}},
        {"protocol": {"id": pid}},
    ]
    for body in bodies:
        status, text = request("POST", "/api/protocols", h, json.dumps(body))
        log(f"POST /api/protocols {json.dumps(body)} -> {status} | {short(text)}")

    for path in (f"/api/protocols/{pid}", "/api/protocols"):
        for body in (json.dumps({"id": pid}), "{}"):
            status, text = request("POST", path, h, body)
            log(f"POST {path} {body} -> {status} | {short(text)}")

    # token + setting with device id (maybe setting is per-device)
    for path, body in (
        (f"/api/token?deviceId={DEVICE_ID}", None),
        (f"/api/token?deviceId={DEVICE_ID}&firebase_token=abc", None),
        ("/api/token", json.dumps({"deviceId": DEVICE_ID, "firebase_token": "abc"})),
    ):
        method = "POST" if body else "GET"
        status, text = request(method, path, h, body)
        log(f"{method} {path} -> {status} | {short(text)}")

    blob = "\n".join(REPORT)[-7000:]
    print("\n::warning title=post-probe::" + urllib.parse.quote(blob, safe=""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
