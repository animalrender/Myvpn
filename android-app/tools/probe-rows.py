#!/usr/bin/env python3
"""Header-variant probe for `/api/protocols` + `/api/v2/protocols`.

The vendor client sends a small, fully-known header set (see
`Lco/nevisa/commonlib/volley/VolleyHelper;->initHeaders`): `app_name`, `version_code`,
`seen`, `sign` = base64(MD5(signing-cert)), `sha_hexadecimal`, optional `Authorization`.
The backend answers with an opaque base64 `value`, and the analysed APK has **no** decryptor
for it (it hands `value` straight to `AngConfigManager.importBatchConfig`, which needs plain
`inbounds`/`outbounds` JSON). This probe asks a closed list of header variants whether any of
them makes the backend return a usable plaintext value, and it stores the raw answers so the
ciphertext can be studied offline.
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
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "probe-rows")
APP_NAME = "co.asiven.vixentvpn"
VERSION_CODE = "1004220"


def base_headers():
    cert_path = os.environ.get("PROBE_CERT", "/tmp/keys/testkey.x509.pem")
    der = base64.b64decode(ssl.PEM_cert_to_DER_cert(open(cert_path).read()))
    return {
        "Content-Type": "application/json",
        "app_name": APP_NAME,
        "version_code": VERSION_CODE,
        "seen": "0",
        "sign": base64.b64encode(hashlib.md5(der).digest()).decode(),
        "sha_hexadecimal": hashlib.sha256(hashlib.sha256(der).digest()).hexdigest(),
        "User-Agent": "okhttp/4.12.0",
    }


def variants(base):
    def without(*keys):
        return {k: v for k, v in base.items() if k not in keys}

    yield "baseline", base
    yield "no-sign", without("sign", "sha_hexadecimal")
    yield "bad-sign", {**base, "sign": base64.b64encode(b"\x00" * 16).decode()}
    yield "bad-sha", {**base, "sha_hexadecimal": "0" * 64}
    yield "seen-1", {**base, "seen": "1"}
    yield "no-app-name", without("app_name")
    yield "v2-telemetry", {**base, "telemetry_identity_version": "2", "telemetryIdentityVersion": "2"}
    yield "old-version", {**base, "version_code": "1004210"}
    yield "no-compression", {**base, "Accept-Encoding": "identity"}


def fetch(path, headers):
    request = urllib.request.Request(BASE + path, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return response.status, response.read(), dict(response.headers)
    except urllib.error.HTTPError as error:
        return error.code, error.read(), dict(error.headers or {})
    except Exception as error:  # noqa: BLE001
        return None, str(error).encode(), {}


def rows_of(raw):
    try:
        payload = json.loads(raw)
    except Exception:  # noqa: BLE001
        return [], None
    rows = payload.get("data") if isinstance(payload, dict) else None
    if isinstance(rows, dict):
        rows = rows.get("data") or rows.get("protocols") or []
    return (rows if isinstance(rows, list) else []), payload


def classify(value):
    if not isinstance(value, str) or not value:
        return "empty"
    if "://" in value[:64]:
        return "link"
    if value.lstrip()[:1] in "{[":
        return "json"
    if value.startswith("ScKit-"):
        return "sckit"
    alphabet = value.replace("=", "").replace("\n", "")
    if alphabet and all(ch.isalnum() or ch in "+/-_" for ch in alphabet):
        return "base64"
    return "other"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    base = base_headers()
    report = {"variants": {}, "notes": []}
    fingerprints = {}
    for name, headers in variants(base):
        entry = {"headers": headers, "endpoints": {}}
        for endpoint in ("/api/protocols", "/api/v2/protocols"):
            status, raw, resp_headers = fetch(endpoint, headers)
            rows, payload = rows_of(raw)
            info = {
                "status": status,
                "bytes": len(raw),
                "rows": len(rows),
                "value_kinds": sorted({classify(row.get("value")) for row in rows[:8]}),
                "first_value_head": (rows[0].get("value") or "")[:48] if rows else "",
            }
            if rows:
                fingerprints.setdefault(endpoint, {})[name] = [
                    (row.get("id"), (row.get("value") or "")[:24]) for row in rows[:3]
                ]
            if isinstance(payload, dict):
                info["payload_keys"] = sorted(payload)
            if rows:
                info["row_keys"] = sorted({k for row in rows for k in row})
                info["sample"] = rows[:3]
            info["response_headers"] = {k: str(v) for k, v in resp_headers.items()}
            if status != 200:
                info["body_head"] = raw[:300].decode("utf-8", "replace")
            entry["endpoints"][endpoint] = info
            print(f"[{name}] {endpoint} -> status={status} rows={len(rows)} "
                  f"kinds={info['value_kinds']} head={info['first_value_head']!r}")
        report["variants"][name] = entry

    # Is `value` deterministic for a row id, or freshly encrypted per request?
    for endpoint, per_variant in fingerprints.items():
        first = next(iter(per_variant.items()), None)
        if not first:
            continue
        name, sample = first
        same = all(per_variant.get(other) == sample for other in per_variant)
        report["notes"].append(f"{endpoint}: value identical across all variants = {same}")
        print(f"== {endpoint}: value identical across variants = {same}")

    with open(os.path.join(OUT_DIR, "variants.json"), "w", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=1)

    # Keep one clean sample per endpoint for the offline key sweep.
    for endpoint, name in (("/api/protocols", "v1"), ("/api/v2/protocols", "v2")):
        entry = report["variants"].get("baseline", {}).get("endpoints", {}).get(endpoint) or {}
        if entry.get("sample"):
            with open(os.path.join(OUT_DIR, f"{name}.json"), "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "request_headers": base,
                        "response_headers": entry.get("response_headers", {}),
                        "rows": entry["sample"],
                    },
                    handle,
                    ensure_ascii=False,
                    indent=1,
                )
    return 0


if __name__ == "__main__":
    sys.exit(main())
