#!/usr/bin/env python3
"""Third probe: follow the 405 signals.

Two answers from the backend are informative:

  POST /api/protocols          -> 200 {"statusCode":200,"status":true,"data":0}
  POST /api/protocols/resolve  -> 405   (the route exists, the method does not match)
  POST /api/v2/protocols       -> 405   (same)

A 405 usually carries an `Allow` header naming the permitted methods, and a route that exists but
rejects POST is very likely a GET with the right query parameters. This script reads the `Allow`
header of every 405 and then walks the GET variants that could hand out a usable config.

Usage: PROBE_CERT=/tmp/keys/testkey.x509.pem python3 tools/probe-resolve.py
"""
import base64
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = os.environ.get("PROBE_BASE", "https://managev1.xyz")
APP_NAME = os.environ.get("PROBE_APP_NAME", "co.asiven.vixentvpn")
VERSION_CODE = os.environ.get("PROBE_VERSION_CODE", "1004220")
DEVICE_ID = os.environ.get("PROBE_DEVICE_ID", "b2ef7de041e0ea3f")
CERT = os.environ.get("PROBE_CERT", "")
REPORT = []


def log(*parts):
    line = " ".join(str(p) for p in parts)
    REPORT.append(line)
    print(line, flush=True)


def cert_der(path):
    if not path or not os.path.exists(path):
        return b""
    return subprocess.run(
        ["openssl", "x509", "-in", path, "-outform", "DER"], capture_output=True, check=True
    ).stdout


DER = cert_der(CERT)


def headers():
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; Pixel 7 Build/TQ3A.230805.001)",
        "app_name": APP_NAME,
        "version_code": VERSION_CODE,
        "seen": "0",
    }
    if DER:
        h["sign"] = base64.b64encode(hashlib.md5(DER).digest()).decode()
        h["sha_hexadecimal"] = hashlib.sha256(hashlib.sha256(DER).digest()).hexdigest()
    return h


def call(method, path, payload=None, timeout=30):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(BASE + path, data=data, headers=headers(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read() or b"", dict(error.headers or {})
    except Exception as error:  # noqa: BLE001
        return -1, str(error).encode(), {}


def short(raw, limit=200):
    return raw.decode("utf-8", "replace").replace("\n", " ")[:limit]


def sample_item():
    status, raw, _ = call("GET", "/api/v2/protocols")
    try:
        data = json.loads(raw.decode()).get("data") or []
    except Exception:  # noqa: BLE001
        return None
    for item in data:
        if isinstance(item, dict) and item.get("endpointKey"):
            return item
    return None


def main():
    item = sample_item()
    if not item:
        log("!! no sample item")
        return 1
    pid, sid = item.get("id"), item.get("serverId")
    ck, rk, ek = item.get("configKey"), item.get("routeKey"), item.get("endpointKey")
    value = item.get("value", "")
    log(f"== sample id={pid} serverId={sid} valueLen={len(value)}")

    # ---- phase A: which methods are allowed on the routes that answered 405?
    log("")
    log("== phase A: method matrix (reading the Allow header of every 405)")
    for path in ["/api/protocols", "/api/v2/protocols", "/api/protocols/resolve",
                 "/api/v2/protocols/resolve", "/api/token", "/api/setting"]:
        for method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            payload = {"id": pid, "protocolId": pid, "serverId": sid, "deviceId": DEVICE_ID} if method != "GET" else None
            status, raw, hdrs = call(method, path, payload)
            allow = hdrs.get("Allow") or hdrs.get("allow") or ""
            log(f"{method:6s} {path:26s} -> {status} allow={allow or '-'} | {short(raw, 90)}")

    # ---- phase B: GET variants that could return the resolved config
    log("")
    log("== phase B: GET variants")
    queries = {
        "id": pid,
        "protocolId": pid,
        "serverId": sid,
        "deviceId": DEVICE_ID,
        "configKey": ck,
        "routeKey": rk,
        "endpointKey": ek,
    }
    qs_all = urllib.parse.urlencode(queries)
    paths = [
        f"/api/protocols/resolve?{qs_all}",
        f"/api/v2/protocols/resolve?{qs_all}",
        f"/api/protocols/resolve?deviceId={DEVICE_ID}&protocolId={pid}",
        f"/api/v2/protocols/resolve?deviceId={DEVICE_ID}&protocolId={pid}",
        f"/api/protocols/resolve?endpointKey={ek}",
        f"/api/protocols/config?{qs_all}",
        f"/api/protocols/{pid}/config?deviceId={DEVICE_ID}",
        f"/api/protocols/{pid}/value?deviceId={DEVICE_ID}",
        f"/api/protocols/{pid}/decode?deviceId={DEVICE_ID}",
        f"/api/v2/protocols/{pid}/config?deviceId={DEVICE_ID}",
        f"/api/v2/protocols/{ek}",
        f"/api/v2/protocols?deviceId={DEVICE_ID}&protocolId={pid}",
        f"/api/v2/protocols?endpointKey={ek}",
        f"/api/protocols?deviceId={DEVICE_ID}&protocolId={pid}",
        f"/api/protocols?endpointKey={ek}",
        f"/api/protocols?configKey={ck}",
        f"/api/protocols?plain=true",
        f"/api/v2/protocols?plain=true",
        f"/api/protocols?decoded=true",
        f"/api/v2/protocols?decoded=true",
    ]
    hits = []
    for path in paths:
        status, raw, _ = call("GET", path)
        text = raw.decode("utf-8", "replace")
        usable = any(s in text for s in ("vmess://", "vless://", "trojan://", '"outbounds"', "ss://"))
        log(f"GET {path.split('?')[0]}?{path.split('?')[1][:70]} -> {status} | {short(raw, 150)}")
        if usable:
            hits.append(path)

    # ---- phase C: POST /api/protocols returns data:0 — does the body change it?
    log("")
    log("== phase C: POST /api/protocols body shapes")
    bodies = [
        {},
        {"id": pid},
        {"protocolId": pid},
        {"protocolId": pid, "deviceId": DEVICE_ID},
        {"serverId": sid},
        {"serverId": sid, "protocolId": pid, "deviceId": DEVICE_ID},
        {"deviceId": DEVICE_ID},
        [pid],
        [sid],
    ]
    for body in bodies:
        status, raw, _ = call("POST", "/api/protocols", body)
        log(f"POST /api/protocols {json.dumps(body)[:60]:62s} -> {status} | {short(raw, 120)}")

    log("")
    if hits:
        log("== ANSWER FOUND:")
        for hit in hits:
            log("   " + hit)
    else:
        log("== still no endpoint that returns a usable config")

    print("::notice title=probe-resolve::%s" % urllib.parse.quote("\n".join(REPORT)[-5500:], safe=""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
