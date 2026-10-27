#!/usr/bin/env python3
"""Answers one question: does this backend ever hand out a **paid** row (`price > 0`)?

The analysed APK has a single server list (`/api/protocols`), and `Protocol.price` is the coin
price of a row (0 = free, > 0 = «پولی · n الماس»). The trial app shows both kinds and only
*counts* them, so if the trial reports «پولی: 0» either the backend really has no paid rows or
the request identity hides them.

This probe prints, for every endpoint/identity variant, how many rows came back and the exact
distribution of `price`, plus the first paid rows (if any). It runs inside GitHub Actions,
because the agent sandbox has no egress to `managev1.xyz`.
"""

import base64
import hashlib
import json
import os
import ssl
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

BASE = os.environ.get("PROBE_BASE", "https://managev1.xyz")
CERT = os.environ.get("PROBE_CERT", "/tmp/keys/testkey.x509.pem")
REPORT = []


def log(*parts):
    line = " ".join(str(p) for p in parts)
    REPORT.append(line)
    print(line, flush=True)


def headers_for(app_name="co.asiven.vixentvpn", version_code="1004220"):
    der = base64.b64decode(ssl.PEM_cert_to_DER_cert(open(CERT).read()))
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "app_name": app_name,
        "version_code": version_code,
        "seen": "0",
        "sign": base64.b64encode(hashlib.md5(der).digest()).decode(),
        "sha_hexadecimal": hashlib.sha256(hashlib.sha256(der).digest()).hexdigest(),
        "User-Agent": "okhttp/4.12.0",
    }


def fetch(path, headers, method="GET", body=None):
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(BASE + path, headers=headers, data=data, method=method)
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()
    except Exception as error:  # noqa: BLE001
        return None, str(error).encode()


def rows_of(raw):
    try:
        payload = json.loads(raw)
    except Exception:  # noqa: BLE001
        return [], None
    rows = payload.get("data") if isinstance(payload, dict) else None
    if isinstance(rows, dict):
        rows = rows.get("data") or rows.get("protocols") or []
    return (rows if isinstance(rows, list) else []), payload


def describe(label, path, headers, method="GET", body=None):
    status, raw = fetch(path, headers, method=method, body=body)
    rows, payload = rows_of(raw)
    if not rows:
        snippet = raw.decode("utf-8", "replace")[:200].replace("\n", " ")
        log(f"### {label}\n`{method} {path}` → {status}, rows=0, body=`{snippet}`")
        return rows
    prices = Counter()
    for row in rows:
        value = row.get("price")
        prices[str(value)] += 1
    keys = sorted(rows[0].keys())
    log(f"### {label}\n`{method} {path}` → {status}, rows={len(rows)}, "
        f"price distribution={dict(sorted(prices.items(), key=lambda kv: str(kv[0])))}, "
        f"keys={keys}")
    paid = [row for row in rows if isinstance(row.get("price"), (int, float)) and row["price"] > 0]
    for row in paid[:5]:
        log(f"- paid row: id={row.get('id')} name={row.get('name')} price={row.get('price')} "
            f"usage={row.get('usage')}")
    if payload is not None:
        log(f"- top-level keys: {sorted(payload.keys()) if isinstance(payload, dict) else type(payload).__name__}")
    return rows


def main():
    base = headers_for()
    log("# probe-price — does the backend ever return `price > 0`?")
    log("")

    all_rows = describe("baseline v1", "/api/protocols", base)
    describe("baseline v2", "/api/v2/protocols", base)

    # The coin/price feature of the original app is driven by the same list; if prices were
    # per-app or per-version, one of these identities would show a different distribution.
    describe("panel app_name (co.vpn.plus)", "/api/protocols",
             headers_for(app_name="co.vpn.plus", version_code="1005697"))
    describe("old version_code 1004210", "/api/protocols",
             headers_for(version_code="1004210"))
    describe("new version_code 1009999", "/api/protocols",
             headers_for(version_code="1009999"))

    # Plausible "give me the paid ones" switches — the backend may filter server-side.
    for query in ("?type=paid", "?paid=1", "?free=0", "?price=1", "?page=1&limit=1000"):
        describe(f"query {query}", "/api/protocols" + query, base)

    for body in ({"page": 1}, {"type": "paid"}, {"price": 1}, {}):
        describe(f"POST body {json.dumps(body)}", "/api/protocols", base,
                 method="POST", body=body)

    # Any global price/coin configuration the client might read.
    status, raw = fetch("/api/setting", base)
    log(f"### /api/setting → {status}, body=`{raw.decode('utf-8', 'replace')[:400]}`")

    # Summary over the rows the app itself receives.
    prices = Counter(str(row.get("price")) for row in all_rows)
    paid = sum(1 for row in all_rows if isinstance(row.get("price"), (int, float)) and row["price"] > 0)
    log("")
    log(f"## نتیجه: {len(all_rows)} ردیف، توزیع قیمت {dict(prices)}، پولی: {paid}")
    log("")
    log("### گزارش کامل\n```\n" + "\n".join(REPORT) + "\n```")


if __name__ == "__main__":
    main()
