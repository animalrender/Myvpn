#!/usr/bin/env python3
"""Pulls complete protocol rows (headers exactly like the analysed client) and stores them.

The `value` field of `/api/protocols` is an encrypted blob; this tool keeps a handful of
complete rows — together with every response header and every key the API exposes
(`configKey`, `routeKey`, `endpointKey`) — so the payload can be attacked offline.
"""

import base64
import hashlib
import json
import os
import ssl
import sys
import urllib.request

BASE = "https://managev1.xyz"
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "probe-rows")
APP_NAME = "co.asiven.vixentvpn"
VERSION_CODE = "1004220"


def sign_headers():
    cert_path = os.environ.get("PROBE_CERT", "/tmp/keys/testkey.x509.pem")
    der = ssl.PEM_cert_to_DER_cert(open(cert_path).read())
    der = base64.b64decode(der)
    sign = base64.b64encode(hashlib.md5(der).digest()).decode()
    sha = hashlib.sha256(hashlib.sha256(der).digest()).hexdigest()
    return {
        "Content-Type": "application/json",
        "app_name": APP_NAME,
        "version_code": VERSION_CODE,
        "seen": "0",
        "sign": sign,
        "sha_hexadecimal": sha,
        "User-Agent": "okhttp/4.12.0",
    }


def get(path):
    request = urllib.request.Request(BASE + path, headers=sign_headers())
    with urllib.request.urlopen(request, timeout=45) as response:
        body = response.read()
        return json.loads(body), dict(response.headers)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    report = {}
    for name, path in (("v1", "/api/protocols"), ("v2", "/api/v2/protocols")):
        try:
            payload, headers = get(path)
        except Exception as error:  # noqa: BLE001
            print(f"!! {path}: {error}")
            continue
        rows = payload.get("data")
        if isinstance(rows, dict):
            rows = rows.get("data") or rows.get("protocols") or []
        if not isinstance(rows, list):
            print(f"!! {path}: unexpected payload {type(rows)}")
            continue
        sample = rows[:5]
        with open(os.path.join(OUT_DIR, f"{name}.json"), "w", encoding="utf-8") as handle:
            json.dump({"headers": headers, "rows": sample}, handle, ensure_ascii=False, indent=1)
        print(f"== {path}: {len(rows)} rows, headers={len(headers)}")
        for header in sorted(headers):
            print(f"   {header}: {headers[header][:120]}")
        for row in sample:
            print(f"   row keys: {sorted(row.keys())}")
        report[name] = {
            "rows": len(rows),
            "keys": sorted({k for row in rows for k in row}),
            "value_lengths": [len(row.get("value") or "") for row in sample],
        }
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
