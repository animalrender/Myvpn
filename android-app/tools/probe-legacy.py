#!/usr/bin/env python3
"""Does the backend still hand out *plaintext* configs to the 3.1.4 client?

`Anotherversion(older).apk` (co.asiven.vixentvpn 3.1.4, versionCode 1004076) uses the exact same
API (`/api/protocols`, `/api/v2/protocols`) but its `Protocol.getValue()` is a plain field read,
i.e. that client can only work if the server sends a usable link/JSON. So sweep the values of
`version_code` the two released APKs send (and a few neighbours) and classify what comes back.
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
VERSIONS = ["1004076", "1004220", "1004221", "1004210", "1004300", "4076", "4220", "1000000"]
PATHS = ["/api/protocols", "/api/v2/protocols"]


def headers(version):
    cert = os.environ.get("PROBE_CERT", "/tmp/keys/testkey.x509.pem")
    der = base64.b64decode(ssl.PEM_cert_to_DER_cert(open(cert).read()))
    return {
        "Content-Type": "application/json",
        "app_name": APP_NAME,
        "version_code": version,
        "seen": "0",
        "sign": base64.b64encode(hashlib.md5(der).digest()).decode(),
        "sha_hexadecimal": hashlib.sha256(hashlib.sha256(der).digest()).hexdigest(),
        "User-Agent": "okhttp/4.12.0",
    }


def get(path, hdrs):
    request = urllib.request.Request(BASE + path, headers=hdrs)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()
    except Exception as error:  # noqa: BLE001
        return -1, f"{type(error).__name__}: {error}".encode()


def classify(value):
    if not isinstance(value, str) or not value:
        return "empty"
    head = value[:64]
    if "://" in head:
        return "LINK"
    if value.lstrip()[:1] in "{[":
        return "JSON"
    if value.startswith("ScKit-"):
        return "sckit"
    alphabet = value.replace("=", "").replace("\n", "")
    if alphabet and all(ch.isalnum() or ch in "+/-_" for ch in alphabet):
        return "base64"
    return "other"


def main():
    report = {}
    for version in VERSIONS:
        hdrs = headers(version)
        for path in PATHS:
            status, raw = get(path, hdrs)
            try:
                payload = json.loads(raw)
            except Exception:  # noqa: BLE001
                print(f"{version:>9} {path:18s} status={status} bytes={len(raw)} body={raw[:120]!r}")
                continue
            rows = payload.get("data") if isinstance(payload, dict) else None
            if isinstance(rows, dict):
                rows = rows.get("data") or []
            if not isinstance(rows, list):
                rows = []
            kinds = sorted({classify(row.get("value")) for row in rows}) if rows else []
            print(f"{version:>9} {path:18s} status={status} rows={len(rows)} kinds={kinds}")
            entry = {"status": status, "rows": len(rows), "kinds": kinds}
            if rows:
                sample = rows[0]
                entry["value_len"] = len(sample.get("value") or "")
                entry["value_head"] = (sample.get("value") or "")[:80]
                entry["row_keys"] = sorted(sample)
                print(f"            head={(sample.get('value') or '')[:48]!r} len={entry['value_len']}")
                if "LINK" in kinds or "JSON" in kinds:
                    entry["links"] = [
                        row.get("value")[:160] for row in rows[:5] if classify(row.get("value")) in ("LINK", "JSON")
                    ]
                    print("            *** plaintext:", entry["links"][:3])
            report[f"{version}{path}"] = entry
    print("REPORT " + json.dumps(report, ensure_ascii=False)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
