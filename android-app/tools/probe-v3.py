#!/usr/bin/env python3
"""Third-generation endpoint probe: is there *any* route that hands out a usable config?

Background: `value` from `/api/protocols` is AES-encrypted (deterministic per row, random IV,
no key inside either released APK), so the only way the official client could dial a row is a
second call that returns the plaintext. This probe enumerates the plausible shapes of that call
using the real row ids and the `configKey` / `routeKey` / `endpointKey` values from
`/api/v2/protocols`, and reports every non-404 answer with its first bytes.
"""

import base64
import hashlib
import json
import os
import ssl
import sys
import urllib.error
import urllib.request

BASE = "https://managev1.xyz"
APP_NAME = "co.asiven.vixentvpn"
VERSION_CODE = "1004220"


def headers():
    cert = os.environ.get("PROBE_CERT", "/tmp/keys/testkey.x509.pem")
    der = base64.b64decode(ssl.PEM_cert_to_DER_cert(open(cert).read()))
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "app_name": APP_NAME,
        "version_code": VERSION_CODE,
        "seen": "0",
        "sign": base64.b64encode(hashlib.md5(der).digest()).decode(),
        "sha_hexadecimal": hashlib.sha256(hashlib.sha256(der).digest()).hexdigest(),
        "User-Agent": "okhttp/4.12.0",
    }


def call(method, path, body=None):
    data = None
    hdrs = headers()
    if body is not None:
        data = json.dumps(body).encode()
    request = urllib.request.Request(BASE + path, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()
    except Exception as error:  # noqa: BLE001
        return -1, f"{type(error).__name__}: {error}".encode()


def main():
    status, raw = call("GET", "/api/v2/protocols")
    payload = json.loads(raw)
    rows = payload.get("data") or []
    if not rows:
        print("!! no rows")
        return 1
    interesting = []
    for row in rows[:3]:
        rid = row.get("id")
        server_id = row.get("serverId")
        ck, rk, ek = row.get("configKey"), row.get("routeKey"), row.get("endpointKey")
        print(f"== row id={rid} serverId={server_id} name={row.get('name')} "
              f"ck={len(ck or '')} rk={len(rk or '')} ek={len(ek or '')}")

        attempts = [
            ("GET", f"/api/protocols/{rid}", None),
            ("GET", f"/api/v2/protocols/{rid}", None),
            ("GET", f"/api/protocol/{rid}", None),
            ("GET", f"/api/protocols?id={rid}", None),
            ("GET", f"/api/v2/protocols?id={rid}", None),
            ("GET", f"/api/protocols/{rid}/config", None),
            ("GET", f"/api/v2/protocols/{rid}/config", None),
            ("GET", f"/api/protocols/config/{rid}", None),
            ("GET", f"/api/configs?id={rid}", None),
            ("GET", f"/api/configs?protocolId={rid}", None),
            ("GET", f"/api/configs?serverId={server_id}", None),
            ("GET", f"/api/configs?configKey={ck}", None),
            ("GET", f"/api/configs?routeKey={rk}", None),
            ("GET", f"/api/configs?endpointKey={ek}", None),
            ("GET", f"/api/v2/configs?protocolId={rid}", None),
            ("GET", f"/api/v2/configs/{rid}", None),
            ("GET", f"/api/endpoint/{ek}", None),
            ("GET", f"/api/route/{rk}", None),
            ("GET", f"/api/config/{ck}", None),
            ("GET", f"/api/v2/endpoint/{ek}", None),
            ("GET", f"/api/v2/route/{rk}", None),
            ("GET", f"/api/v2/config/{ck}", None),
            ("POST", "/api/configs", {"id": rid}),
            ("POST", "/api/configs", {"protocolId": rid}),
            ("POST", "/api/configs", {"protocolId": rid, "deviceId": "0"}),
            ("POST", "/api/configs", {"configKey": ck, "routeKey": rk, "endpointKey": ek}),
            ("POST", "/api/v2/configs", {"protocolId": rid}),
            ("POST", "/api/v2/protocols", {"id": rid}),
            ("POST", "/api/protocols", {"id": rid}),
            ("POST", "/api/protocols", {"protocolId": rid}),
            ("POST", "/api/decode", {"value": row.get("value")}),
            ("POST", "/api/v2/decode", {"value": row.get("value")}),
            ("POST", "/api/protocols/decode", {"value": row.get("value")}),
        ]
        for method, path, body in attempts:
            st, body_raw = call(method, path, body)
            text = body_raw[:160].decode("utf-8", "replace").replace("\n", " ")
            if st == 404:
                continue
            looks_useful = any(marker in text for marker in ("vmess://", "vless://", "trojan://", "ss://",
                                                             "inbounds", "outbounds", "shadowsocks"))
            flag = "*** USEFUL ***" if looks_useful else ""
            print(f"   {method:4s} {path:58s} -> {st} {flag} {text}")
            if st not in (-1, 404):
                interesting.append({"row": rid, "method": method, "path": path, "status": st, "body": text})
    print("\nSUMMARY non-404: %d" % len(interesting))
    print(json.dumps(interesting, ensure_ascii=False)[:6000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
