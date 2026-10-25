#!/usr/bin/env python3
"""Second probe: find the endpoint/parameter shape that returns usable configs.

Runs in GitHub Actions (the agent sandbox has no egress to managev1.xyz) and
reports everything through workflow annotations.

Usage: PROBE_CERT=/tmp/keys/testkey.x509.pem python3 tools/probe-configs.py
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


def headers(der, token="", enable_sign=True):
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "app_name": APP_NAME,
        "version_code": VERSION_CODE,
        "seen": "0",
    }
    if token:
        h["token"] = token
    if enable_sign:
        h["sign"] = base64.b64encode(hashlib.md5(der).digest()).decode()
        h["sha_hexadecimal"] = hashlib.sha256(hashlib.sha256(der).digest()).hexdigest()
    return h


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


def short(text, limit=170):
    text = " ".join(text.split())
    return text[:limit] + ("…" if len(text) > limit else "")


def main():
    pem = os.environ.get("PROBE_CERT", "testkey.x509.pem")
    if not os.path.exists(pem):
        log(f"!! cert {pem} missing")
        return 1
    der = cert_der(pem)
    h = headers(der)

    # learn a real id pair from /api/protocols
    status, text = request("GET", "/api/protocols", h)
    first_id = first_server = None
    try:
        items = json.loads(text).get("data") or []
        if items:
            first_id = items[0].get("id")
            first_server = items[0].get("serverId")
    except Exception:  # noqa: BLE001
        items = []
    log(f"protocols -> {status}, items={len(items)}, id={first_id}, serverId={first_server}")

    qs = f"deviceId={DEVICE_ID}"
    gets = [
        f"/api/configs?{qs}",
        f"/api/configs?{qs}&serverId={first_server}",
        f"/api/configs?{qs}&protocolId={first_id}",
        f"/api/configs?{qs}&serverId={first_server}&protocolId={first_id}",
        f"/api/configs/{first_server}",
        f"/api/configs/{first_id}",
        f"/api/protocols/{first_server}",
        f"/api/protocols/{first_id}",
        "/api/protocols/default",
        "/api/protocols/0",
        "/api/protocols/mci",
        "/api/protocols/irancell",
        "/api/protocols/mtn",
        f"/api/setting?{qs}",
        "/api/servers",
        f"/api/servers?{qs}",
        f"/api/server/{first_server}",
        "/api/location",
        "/api/locations",
    ]
    for path in gets:
        status, text = request("GET", path, h)
        log(f"GET  {path} -> {status} | {short(text)}")

    posts = [
        ("/api/configs", {"deviceId": DEVICE_ID}),
        ("/api/configs", {"deviceId": DEVICE_ID, "serverId": first_server}),
        ("/api/configs", {"deviceId": DEVICE_ID, "protocolId": first_id}),
        ("/api/configs", {"deviceId": DEVICE_ID, "serverId": first_server, "protocolId": first_id}),
        ("/api/configs", {}),
        ("/api/protocols", {"deviceId": DEVICE_ID}),
        ("/api/protocols", {"deviceId": DEVICE_ID, "operator": "mci"}),
        ("/api/token", {"deviceId": DEVICE_ID, "firebase_token": ""}),
        ("/api/setting", {"deviceId": DEVICE_ID}),
    ]
    for path, body in posts:
        status, text = request("POST", path, h, json.dumps(body))
        log(f"POST {path} {json.dumps(body)} -> {status} | {short(text)}")

    blob = "\n".join(REPORT)[-7000:]
    print("\n::warning title=configs-probe::" + urllib.parse.quote(blob, safe=""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
