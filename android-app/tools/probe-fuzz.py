#!/usr/bin/env python3
"""Fourth probe: endpoint discovery + payload determinism checks.

* fuzzes a wordlist of plausible API paths and reports every 200 that is not a
  known placeholder (so a plaintext config endpoint can be found);
* checks whether `/api/protocols` values are stable across requests and whether
  they depend on the device id / signature headers.

Usage: PROBE_CERT=/tmp/keys/testkey.x509.pem python3 tools/probe-fuzz.py
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
DEVICE_A = os.environ.get("PROBE_DEVICE_ID", "b2ef7de041e0ea3f")
DEVICE_B = "9c1f4a77c0de1b28"
UA = "Dalvik/2.1.0 (Linux; U; Android 13; Pixel 7 Build/TQ3A.230805.001)"
REPORT = []

WORDS = """
token setting protocols configs config server servers location locations
sub subscription subs v2ray v2rayng link links free paid premium price prices
usage ping test user users device devices register login auth app apps version
update banner banners ads admob social sponsor policy privacy operator
operators isp region regions country countries city cities node nodes relay
relays proxy proxies connect connection connectinfo info data list items
all available speed latency status health geo ip host hosts port ports uuid
vless vmess trojan shadowssocks ss shadowsocks configbyid byid byserver
protocolById protocolByServer getConfig getProtocols getServers fetch fetchConfig
""".split()

PREFIXES = ["/api/", "/api/v1/", "/api/v2/", "/"]


def log(*parts):
    line = " ".join(str(p) for p in parts)
    REPORT.append(line)
    print(line, flush=True)


def cert_der(path):
    return subprocess.run(
        ["openssl", "x509", "-in", path, "-outform", "DER"], capture_output=True, check=True
    ).stdout


def headers(der, device=None, sign=True, sha=True):
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": UA,
        "app_name": APP_NAME,
        "version_code": VERSION_CODE,
        "seen": "0",
    }
    if sign:
        h["sign"] = base64.b64encode(hashlib.md5(der).digest()).decode()
    if sha:
        h["sha_hexadecimal"] = hashlib.sha256(hashlib.sha256(der).digest()).hexdigest()
    return h


def request(method, path, hdrs, body=None, timeout=20):
    req = urllib.request.Request(
        BASE + path, data=(body.encode() if isinstance(body, str) else body), headers=hdrs, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return -1, f"{type(exc).__name__}: {exc}"


def short(text, limit=150):
    return " ".join(text.split())[:limit]


def main():
    pem = os.environ.get("PROBE_CERT", "testkey.x509.pem")
    if not os.path.exists(pem):
        log(f"!! cert {pem} missing")
        return 1
    der = cert_der(pem)
    full = headers(der)

    # ---- 1. endpoint discovery -------------------------------------------------
    found = []
    known_ok = 0
    for prefix in PREFIXES:
        for word in WORDS:
            path = prefix + word
            status, text = request("GET", path, full)
            if status == 200:
                known_ok += 1
                if '"status":true' in text and '"data":null' not in text and len(text) > 80:
                    found.append((path, len(text), short(text, 180)))
    log(f"fuzz: {len(PREFIXES) * len(WORDS)} paths, {known_ok} returned 200, {len(found)} carried data")
    for path, size, preview in found:
        log(f"  DATA {path} ({size}B) | {preview}")

    # ---- 2. header / device dependence of /api/protocols ----------------------
    variants = {
        "sign+sha": headers(der, sign=True, sha=True),
        "only-sign": headers(der, sign=True, sha=False),
        "only-sha": headers(der, sign=False, sha=True),
        "no-sign": headers(der, sign=False, sha=False),
    }
    sample = {}
    for name, h in variants.items():
        status, text = request("GET", "/api/protocols", h)
        try:
            data = json.loads(text).get("data")
        except Exception:  # noqa: BLE001
            data = None
        if isinstance(data, list) and data:
            first = data[0]
            sample[name] = first.get("value", "")[:48]
            log(f"protocols[{name}] -> {status}, items={len(data)}, id={first.get('id')} value[:48]={sample[name]}")
        else:
            log(f"protocols[{name}] -> {status} | {short(text)}")

    # same id, different device id: does the value for the same protocol change?
    status, text = request("GET", "/api/protocols", full)
    try:
        items = json.loads(text).get("data") or []
    except Exception:  # noqa: BLE001
        items = []
    if items:
        pid = items[0].get("id")
        for attempt in range(3):
            status, text = request("GET", f"/api/protocols/{pid}", full)
            try:
                again = (json.loads(text).get("data") or [{}])[0]
            except Exception:  # noqa: BLE001
                again = {}
            log(f"repeat#{attempt} id={again.get('id')} value[:48]={str(again.get('value'))[:48]}")
        # same request twice, compare first item value
        status, t1 = request("GET", "/api/protocols", full)
        status, t2 = request("GET", "/api/protocols", full)
        v1 = (json.loads(t1).get("data") or [{}])[0].get("value", "")
        v2 = (json.loads(t2).get("data") or [{}])[0].get("value", "")
        log(f"determinism: same-first-item={v1 == v2} same-length={len(v1) == len(v2)} len={len(v1)}")
        # value shape: base64 alphabet? hex?
        alphabet = set(v1)
        log(f"value charset sample: {'base64' if alphabet <= set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=') else 'other'}, len={len(v1)}")

    blob = "\n".join(REPORT)[-7000:]
    print("\n::warning title=fuzz-report::" + urllib.parse.quote(blob, safe=""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
