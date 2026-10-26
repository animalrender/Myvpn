#!/usr/bin/env python3
"""Probes the endpoints that could turn a server's opaque `value` blob into a usable config.

`/api/protocols` and `/api/v2/protocols` return `value` = base64 of high-entropy data (length a
multiple of 16) plus, in v2, `configKey`/`routeKey`/`endpointKey` (64 hex each). This script tries
the plausible "resolve this server" shapes — with the exact baseline headers — and reports every
answer through workflow annotations.

Usage: PROBE_CERT=/tmp/keys/testkey.x509.pem python3 tools/probe-decode.py
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


def headers(extra=None):
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
    if extra:
        h.update({k: v for k, v in extra.items() if v})
    return h


def request(path, body=None, method=None, extra=None, timeout=30):
    data = None if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
    req = urllib.request.Request(BASE + path, data=data, headers=headers(extra), method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            return response.status, raw
    except urllib.error.HTTPError as error:
        return error.code, error.read() or b""
    except Exception as error:  # noqa: BLE001 - the report must survive any failure
        return -1, str(error).encode()


def short(raw, limit=260):
    text = raw.decode("utf-8", "replace").replace("\n", " ")
    return text[:limit]


def items(path="/api/v2/protocols"):
    status, raw = request(path)
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception:  # noqa: BLE001
        return []
    data = payload.get("data")
    return data if isinstance(data, list) else []


def main():
    log("== baseline headers:", json.dumps(headers(), ensure_ascii=False))
    sample = None
    for item in items():
        if isinstance(item, dict) and item.get("endpointKey"):
            sample = item
            break
    if sample is None:
        log("!! /api/v2/protocols gave no item with endpointKey; nothing to probe")
        return 1
    pid = sample.get("id")
    sid = sample.get("serverId")
    value = sample.get("value", "")
    ck, rk, ek = sample.get("configKey"), sample.get("routeKey"), sample.get("endpointKey")
    log(f"== sample: id={pid} serverId={sid} valueLen={len(value)} name={sample.get('name')}")
    log(f"   configKey={ck}\n   routeKey={rk}\n   endpointKey={ek}")

    body = {
        "deviceId": DEVICE_ID,
        "protocolId": pid,
        "serverId": sid,
        "id": pid,
        "configKey": ck,
        "routeKey": rk,
        "endpointKey": ek,
        "value": value,
        "telemetryIdentityVersion": 2,
    }

    attempts = [
        ("POST", "/api/v2/protocols", body),
        ("POST", "/api/protocols", body),
        ("POST", "/api/config", body),
        ("POST", "/api/configs", body),
        ("POST", "/api/v2/configs", body),
        ("POST", "/api/connect", body),
        ("POST", "/api/connection", body),
        ("POST", "/api/decode", body),
        ("POST", "/api/decrypt", body),
        ("POST", "/api/protocol", body),
        ("POST", "/api/proxy", body),
        ("POST", "/api/proxy/config", body),
        ("POST", "/api/config/resolve", body),
        ("GET", f"/api/configs?deviceId={DEVICE_ID}&protocolId={pid}&serverId={sid}", None),
        ("GET", f"/api/v2/configs?deviceId={DEVICE_ID}&protocolId={pid}&serverId={sid}", None),
        ("GET", f"/api/config/{ck}", None),
        ("GET", f"/api/config/{ek}", None),
        ("GET", f"/api/configs/{pid}", None),
        ("GET", f"/api/v2/protocols/{pid}", None),
        ("GET", f"/api/protocols/{pid}", None),
        ("GET", f"/api/endpoint/{ek}", None),
        ("GET", f"/api/route/{rk}", None),
        ("GET", f"/api/config-key/{ck}", None),
        ("GET", f"/api/decode?value={urllib.parse.quote(value[:200])}", None),
        ("POST", "/api/protocols/resolve", {"id": pid, "deviceId": DEVICE_ID}),
        ("POST", "/api/v2/protocols/resolve", {"id": pid, "deviceId": DEVICE_ID}),
    ]

    interesting = []
    for method, path, payload in attempts:
        status, raw = request(path, payload, method)
        line = f"{method} {path.split('?')[0]} -> {status} | {short(raw)}"
        log(line)
        if status == 200 and raw:
            text = raw.decode("utf-8", "replace")
            if "vmess://" in text or "vless://" in text or "trojan://" in text or '"outbounds"' in text:
                interesting.append(line)

    log("")
    if interesting:
        log("== ANSWER FOUND (a response contains a usable config):")
        for line in interesting:
            log("   " + line)
    else:
        log("== no response contained a share link or an outbounds array")

    try:
        body_text = "\n".join(REPORT)
        print("::notice title=probe-decode::%s" % urllib.parse.quote(body_text[-5500:], safe=""))
    except Exception:  # noqa: BLE001
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
