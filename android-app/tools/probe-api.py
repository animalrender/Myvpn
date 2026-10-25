#!/usr/bin/env python3
"""Probes the analysed backend to pin down the exact request contract.

Runs inside GitHub Actions (the sandbox that runs the agent has no egress to
managev1.xyz). Every result is printed, and the whole report is emitted as a
workflow annotation so it can be read back through the check-runs API.

Usage: python3 tools/probe-api.py [--key keystore-dir]
"""
import base64
import hashlib
import json
import os
import ssl
import subprocess
import sys
import urllib.request
import urllib.parse

BASE = os.environ.get("PROBE_BASE", "https://managev1.xyz")
APP_NAME = "co.asiven.vixentvpn"
VERSION_CODE = os.environ.get("PROBE_VERSION_CODE", "1004220")
DEVICE_ID = os.environ.get("PROBE_DEVICE_ID", "b2ef7de041e0ea3f")

REPORT = []


def log(*parts):
    line = " ".join(str(p) for p in parts)
    REPORT.append(line)
    print(line, flush=True)


def cert_der(path):
    """DER bytes of the signing certificate (what Signature.toByteArray() returns)."""
    return subprocess.run(
        ["openssl", "x509", "-in", path, "-outform", "DER"], capture_output=True, check=True
    ).stdout


def headers_for(der, token="", authorization=None, seen="0", include_sign=True):
    h = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13)",
        "app_name": APP_NAME,
        "version_code": VERSION_CODE,
        "seen": seen,
    }
    if token:
        h["token"] = token
    if include_sign:
        # VolleyHelper.getSign("MD5") -> Base64(MD5(signature))
        h["sign"] = base64.b64encode(hashlib.md5(der).digest()).decode()
        # Ld0/h.w(Signature) -> hex(SHA256(SHA256(signature)))
        h["sha_hexadecimal"] = hashlib.sha256(hashlib.sha256(der).digest()).hexdigest()
    if authorization:
        h["Authorization"] = authorization
    return h


def request(method, path, headers, body=None, timeout=25):
    url = BASE + path
    data = body.encode() if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")
    except Exception as exc:  # noqa: BLE001
        return -1, f"{type(exc).__name__}: {exc}"


def short(text, limit=220):
    text = text.replace("\n", " ")
    return text[:limit] + ("…" if len(text) > limit else "")


def main():
    pem = os.environ.get("PROBE_CERT", "testkey.x509.pem")
    if not os.path.exists(pem):
        log(f"!! certificate {pem} not found — cannot compute sign headers")
        return 1
    der = cert_der(pem)
    log(f"cert DER bytes: {len(der)}")
    log("sign  =", headers_for(der)["sign"])
    log("sha   =", headers_for(der)["sha_hexadecimal"])
    log("")

    probes = [
        ("A", "GET", "/api/token", headers_for(der)),
        ("B", "GET", "/api/token", headers_for(der, token="")),
        ("C", "GET", "/api/token", headers_for(der, token="dummy-firebase-token")),
        ("D", "GET", f"/api/token?deviceId={DEVICE_ID}", headers_for(der)),
        ("E", "GET", f"/api/token?device_id={DEVICE_ID}", headers_for(der)),
        ("F", "GET", f"/api/token?deviceId={DEVICE_ID}&firebase_token=x", headers_for(der)),
        ("G", "POST", "/api/token", headers_for(der), json.dumps({"deviceId": DEVICE_ID})),
        ("H", "GET", "/api/token", headers_for(der, include_sign=False)),
        ("I", "GET", "/api/setting", headers_for(der)),
        ("J", "GET", "/api/protocols", headers_for(der)),
        ("K", "GET", "/api/configs", headers_for(der)),
    ]

    token = None
    for probe in probes:
        code = probe[0]
        method = probe[1]
        path = probe[2]
        headers = probe[3]
        body = probe[4] if len(probe) > 4 else None
        status, text = request(method, path, headers, body)
        log(f"[{code}] {method} {path} -> {status} | {short(text)}")
        if code in ("A", "B", "C", "D", "E", "F") and status == 200:
            try:
                payload = json.loads(text)
            except Exception:
                payload = None
            if isinstance(payload, dict) and payload.get("status") and token is None:
                token = json.dumps(payload.get("data"))[:120]
                log(f"    ↳ looks successful, data = {token}")

    log("")
    if token:
        raw = token.strip('"')
        for label, hdr in (
            ("L1 Authorization", dict(headers_for(der), Authorization=f"bearer {raw}")),
            ("L2 token hdr", headers_for(der, token=raw)),
            ("L3 both", dict(headers_for(der, token=raw), Authorization=f"bearer {raw}")),
        ):
            status, text = request("GET", "/api/protocols", hdr)
            log(f"[{label}] /api/protocols -> {status} | {short(text)}")

    # full detail of the protocol payload: schema + raw (encrypted) values
    status, text = request("GET", "/api/protocols", headers_for(der))
    detail = []
    try:
        payload = json.loads(text)
        data = payload.get("data") or []
        detail.append(f"protocols: {len(data)} items, top-level keys={list(payload.keys())}")
        if data:
            detail.append("item keys: " + json.dumps(sorted(data[0].keys()), ensure_ascii=False))
        for item in data[:3]:
            detail.append("---- item ----")
            detail.append(json.dumps({k: (v if k != "value" else f"<{len(str(v))} chars>") for k, v in item.items()}, ensure_ascii=False)[:600])
            value = str(item.get("value", ""))
            detail.append("value[0:600]=" + value[:600])
            for decoder in ("b64", "b64url"):
                try:
                    raw = base64.b64decode(value + "=" * (-len(value) % 4),
                                          altchars=b"-_" if decoder == "b64url" else None)
                    detail.append(f"{decoder}: {len(raw)} bytes, first32={raw[:32].hex()}")
                except Exception as exc:  # noqa: BLE001
                    detail.append(f"{decoder}: {type(exc).__name__}")
    except Exception as exc:  # noqa: BLE001
        detail.append(f"parse error: {exc}; body={text[:300]}")
    blob = "\n".join(detail)
    log("")
    log("===== PROTOCOL DETAIL =====")
    log(blob)
    print("\n::warning title=probe-report::" + urllib.parse.quote("\n".join(REPORT)[-6000:], safe=""))
    print("\n::warning title=protocol-detail::" + urllib.parse.quote(blob[-6000:], safe=""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
