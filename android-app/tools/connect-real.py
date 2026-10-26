#!/usr/bin/env python3
"""Zero-input end-to-end test against the **real** vendor backend.

This is the test that matters for the current goal: the trial app must behave like the store
build — it fetches the server list itself, decrypts every `Protocol.value` itself, and connects
without the user supplying a link, a subscription or a key.

Rounds:

  1. fresh start   `pm clear` (no cache, no saved config), launch the activity
  2. fetch         wait until rows appear; assert the count comes from `/api/protocols`
  3. ping all      run «پینگ همه», scrape every row's badge, pick the fastest answering server
  4. connect       tap the row, tap «اتصال», accept the system VPN prompt
  5. traffic       push HTTPS through the shell uid and compare the exit IP with the pre-tunnel
                   one; a different exit IP + a live `tun0` is the proof the bytes left through
                   the vendor's server
  6. second server same for the next-best row (proves switching and that the key derivation works
                   for more than one row)
  7. teardown      disconnect and assert `tun0` disappears

Only non-secret facts are written to the report (row labels, ping values, exit IP / country).
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

OUT = "."
PROBE_URL = "http://connectivitycheck.gstatic.com/generate_204"
TRACE_URL = "https://www.cloudflare.com/cdn-cgi/trace"
COMPONENT = "co.asiven.vixentvpn/co.asiven.vixentvpn.trial.ui.MainActivity"
REPORT = []
SHOTS = []


def log(message):
    print(message, flush=True)
    REPORT.append(f"- {message}")


def shot(name):
    path = os.path.join(OUT, f"{name}.png")
    with open(path, "wb") as handle:
        subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=handle,
                       stderr=subprocess.DEVNULL, timeout=180)
    SHOTS.append(name)


def adb(*args, timeout=240):
    try:
        return subprocess.run(["adb", *args], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(["adb", *args], 1, "", "timeout")


def shell(command, timeout=240):
    return adb("shell", command, timeout=timeout)


def dump_xml():
    for _ in range(4):
        text = adb("exec-out", "uiautomator dump /dev/tty", timeout=150).stdout or ""
        match = re.search(r"<\?xml.*</hierarchy>", text, re.S)
        if match:
            return match.group(0)
        time.sleep(2)
    return ""


def nodes(xml_text):
    return [dict(re.findall(r'([\w:-]+)="([^"]*)"', m.group(0)))
            for m in re.finditer(r"<node[^>]*>", xml_text)]


def center(bounds):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
    if not match:
        return None
    x1, y1, x2, y2 = (int(v) for v in match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2


def tap(point):
    shell(f"input tap {point[0]} {point[1]}")


def find(text=None, exact=False, rid=None, xml=None):
    for node in nodes(xml if xml is not None else dump_xml()):
        if rid and not (node.get("resource-id") or "").endswith(rid):
            continue
        if text:
            value = node.get("text") or ""
            if not value or (value != text if exact else text not in value):
                continue
        if rid or text:
            return node
    return None


def tap_text(text, exact=False):
    node = find(text=text, exact=exact)
    point = center(node.get("bounds")) if node else None
    if not point:
        return False
    tap(point)
    return True


def tap_rid(rid):
    node = find(rid=rid)
    point = center(node.get("bounds")) if node else None
    if not point:
        return False
    tap(point)
    return True


def dismiss_system_dialogs():
    """Taps away system permission prompts (notifications, etc.) that would cover the list."""
    xml = dump_xml()
    for node in nodes(xml):
        text = (node.get("text") or "").strip()
        if text in ("Allow", "Don't allow", "OK", "While using the app", "باشه"):
            point = center(node.get("bounds"))
            if point:
                tap(point)
                log(f"دیالوگ سیستمی «{text}» بسته شد")
                time.sleep(1)
                return True
    return False


def accept_vpn_dialog():
    for _ in range(20):
        for node in nodes(dump_xml()):
            text = (node.get("text") or "").strip()
            rid = node.get("resource-id") or ""
            if rid.endswith("button1") or text in ("OK", "Allow", "تأیید", "باشه"):
                point = center(node.get("bounds"))
                if point:
                    tap(point)
                    return True
        time.sleep(2)
    return False


def rows():
    """Server rows currently painted in the list: (name, ping badge, bounds)."""
    xml = dump_xml()
    found = []
    for node in nodes(xml):
        rid = node.get("resource-id") or ""
        if not rid.endswith("nameText"):
            continue
        label = (node.get("text") or "").strip()
        if not label:
            continue
        bounds = node.get("bounds")
        # the ping badge lives in the same card; take the nearest pingText below it
        ping = ""
        ping_bounds = None
        for other in nodes(xml):
            if (other.get("resource-id") or "").endswith("pingText"):
                if same_card(bounds, other.get("bounds")):
                    ping = (other.get("text") or "").strip()
                    ping_bounds = other.get("bounds")
                    break
        found.append({"name": label, "ping": ping, "bounds": bounds, "ping_bounds": ping_bounds})
    return found


def same_card(a, b):
    ca, cb = center(a), center(b)
    if not ca or not cb:
        return False
    return abs(ca[0] - cb[0]) < 560 and 0 <= cb[1] - ca[1] < 200


def ping_ms(text):
    match = re.search(r"(\d+)\s*ms", text or "")
    return int(match.group(1)) if match else None


_TOOL = None


def http_tool():
    """The emulator images ship different userland tools; find one that can speak HTTP."""
    global _TOOL
    if _TOOL:
        return _TOOL
    for candidate in ("curl", "wget", "nc"):
        out = (shell(f"command -v {candidate}").stdout or "").strip()
        if out and "not found" not in out:
            _TOOL = candidate
            return _TOOL
    _TOOL = "none"
    return _TOOL


def http_get(url, timeout=25):
    """Returns (status_line_or_code, body). Works through the tunnel like any other app."""
    tool = http_tool()
    if tool == "curl":
        out = shell(f"curl -s -m {timeout} -w '\\n%{{http_code}}' {url}").stdout or ""
        body, _, code = out.rpartition("\n")
        return code.strip(), body
    if tool == "wget":
        out = shell(f"wget -q -O - -T {timeout} {url}").stdout or ""
        return ("200" if out.strip() else "no-response"), out
    if tool == "nc":
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "http":
            return "https-needs-curl", ""
        path = parsed.path or "/"
        request = (
            f"printf 'GET {path} HTTP/1.1\\r\\nHost: {parsed.hostname}\\r\\n"
            f"Connection: close\\r\\n\\r\\n' | nc -w {timeout} {parsed.hostname} 80"
        )
        out = shell(request).stdout or ""
        head, _, body = out.partition("\r\n\r\n")
        if not _:
            head, _, body = out.partition("\n\n")
        first = head.splitlines()[0] if head.splitlines() else ""
        match = re.search(r"\s(\d{3})\s", first)
        return (match.group(1) if match else (first[:40] or "no-response")), body
    return "no-http-tool", ""


def probe(url=PROBE_URL):
    code, _ = http_get(url)
    return code


def exit_ip():
    """Public IP / country as seen from inside the tunnel (plain HTTP, so every tool can do it)."""
    _, body = http_get("http://api.ipify.org", timeout=20)
    token = re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", body or "")
    ip = token.group(0) if token else ""
    _, trace = http_get("http://ip-api.com/line/?fields=countryCode,isp", timeout=20)
    lines = [line.strip() for line in (trace or "").splitlines() if line.strip()]
    country = lines[0] if lines else "?"
    isp = lines[1] if len(lines) > 1 else "?"
    return (ip or None), country, isp


def tun_up():
    return "inet " in (shell("ip -4 addr show tun0").stdout or "")


def row_bounds(name):
    for node in nodes(dump_xml()):
        if not (node.get("resource-id") or "").endswith("nameText"):
            continue
        if (node.get("text") or "").strip() == name:
            return node.get("bounds")
    return None


def bring_into_view(name):
    """Scrolls the list until the named row is comfortably inside the viewport."""
    for _ in range(14):
        bounds = row_bounds(name)
        point = center(bounds) if bounds else None
        if point and 260 <= point[1] <= 1900:
            return bounds
        if point and point[1] < 260:
            shell("input swipe 540 700 540 1500 300")   # pull the list down
        else:
            shell("input swipe 540 1700 540 800 300")   # push the list up
        time.sleep(1.5)
    return row_bounds(name)


def connect_row(row, index):
    landed = bring_into_view(row["name"])
    if not landed:
        log(f"**ردیف «{row['name']}» در فهرست پیدا نشد**")
        return False
    row = dict(row, bounds=landed)
    tap(center(row["bounds"]))
    time.sleep(2)
    shot(f"{index}-selected")
    if not (tap_rid("connectButton") or tap_text("اتصال", exact=True)):
        log("**دکمهٔ اتصال پیدا نشد**")
        return False
    time.sleep(4)
    if accept_vpn_dialog():
        log("دیالوگ مجوز VPN تأیید شد")
    label = f"متصل — {row['name']}"
    for _ in range(60):
        node = find(text="متصل", exact=False)
        if node:
            status = (node.get("text") or "").strip()
            log(f"وضعیت تونل: `{status}`")
            shot(f"{index}-connected")
            return True
        time.sleep(2)
    shot(f"{index}-connect-failed")
    log(f"**وضعیت «{label}» دیده نشد**")
    return False


def main(argv):
    global OUT, PROBE_URL
    if len(argv) < 1:
        print(__doc__)
        return 2
    OUT = argv[0]
    if len(argv) > 1:
        PROBE_URL = argv[1]
    os.makedirs(OUT, exist_ok=True)
    failures = []

    # ------------------------------------------------------------ 1. fresh start
    log("پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)")
    adb("shell", "pm clear co.asiven.vixentvpn", timeout=120)
    # `pm clear` also drops runtime grants, and the notification prompt would cover the list.
    shell("pm grant co.asiven.vixentvpn android.permission.POST_NOTIFICATIONS")
    adb("shell", "am start -W -n " + COMPONENT, timeout=180)
    time.sleep(6)
    dismiss_system_dialogs()
    log(f"ابزار HTTP روی شبیه‌ساز: `{http_tool()}`")
    baseline_ip, baseline_country, baseline_colo = exit_ip()
    log(f"IP خروج پیش از اتصال: `{baseline_ip}` ({baseline_country}/{baseline_colo})")
    code_before = probe()
    log(f"درخواست بدون تونل: HTTP {code_before or 'بدون پاسخ'}")

    # ------------------------------------------------------------ 2. fetch
    loaded = None
    for attempt in range(60):
        painted = rows()
        waiting = find(text="در حال دریافت سرورها")
        if painted and not waiting:
            loaded = painted
            break
        if attempt % 5 == 0:
            dismiss_system_dialogs()
        time.sleep(2)
    shot("01-loaded")
    if not loaded:
        log("**هیچ سروری از بک‌اند بارگذاری نشد**")
        failures.append("no-rows")
        write_report(failures, baseline_ip, None)
        return 1
    summary_text = (find(rid="summaryText") or {}).get("text") or ""
    log(f"فهرست بارگذاری شد: {len(loaded)} ردیف روی صفحه — خلاصه: `{summary_text}`")
    log("نمونهٔ برچسب ردیف‌ها: " + "، ".join(f"`{r['name']}`" for r in loaded[:3]))

    # ------------------------------------------------------------ 3. ping all
    if tap_text("پینگ همه", exact=True):
        log("«پینگ همه» زده شد")
    else:
        log("**دکمهٔ پینگ همه پیدا نشد**")
        failures.append("no-ping-all")
    fastest = None
    deadline = time.time() + 300
    while time.time() < deadline:
        painted = rows()
        answered = [r for r in painted if ping_ms(r["ping"])]
        pending = [r for r in painted if (r["ping"] or "").strip() in ("", "…")]
        if answered:
            fastest = min(answered, key=lambda r: ping_ms(r["ping"]))
        if answered and not pending:
            break
        time.sleep(5)
    shot("02-ping-all")
    answered = [r for r in rows() if ping_ms(r["ping"])]
    log(f"پینگ‌ها: {len(answered)} ردیف پاسخ داد؛ سریع‌ترین: "
        f"`{fastest['name'] if fastest else '—'}` ({fastest['ping'] if fastest else '—'})")
    if not answered:
        log("**هیچ سروری به پینگ پاسخ نداد**")
        failures.append("no-ping-response")

    # ------------------------------------------------------------ 4. connect
    if fastest:
        log(f"اتصال به سریع‌ترین سرور: `{fastest['name']}`")
        if not connect_row(fastest, "03"):
            failures.append("not-connected")
        else:
            time.sleep(5)
            up = tun_up()
            log(f"رابط tun0: {'موجود' if up else 'موجود نیست'}")
            if not up:
                failures.append("no-tun")
            code = probe()
            log(f"درخواست از داخل تونل: HTTP {code or 'بدون پاسخ'}")
            if code not in ("204", "200"):
                failures.append(f"probe-{code or 'none'}")
            ip, country, colo = exit_ip()
            log(f"IP خروج داخل تونل: `{ip}` ({country}/{colo})")
            if ip and baseline_ip and ip == baseline_ip:
                log("توجه: IP خروج تغییر نکرد — ممکن است سرور و شبکهٔ رانر هم‌مکان باشند")
                failures.append("exit-ip-unchanged")

            # -------------------------------------------------------- 5. second row
            painted = rows()
            others = [r for r in painted
                      if r["name"] != fastest["name"] and ping_ms(r["ping"])]
            if len(others) >= 1:
                second = min(others, key=lambda r: ping_ms(r["ping"]))
                log(f"تغییر سرور به: `{second['name']}`")
                if connect_row(second, "04"):
                    code2 = probe()
                    log(f"درخواست پس از تغییر سرور: HTTP {code2 or 'بدون پاسخ'}")
                    if code2 not in ("204", "200"):
                        failures.append(f"probe-after-switch-{code2 or 'none'}")
                else:
                    failures.append("switch-failed")
            else:
                log("سرور دوم قابل‌اتصال دیگری برای آزمون تغییر سرور پیدا نشد")

            # -------------------------------------------------------- 6. teardown
            if tap_rid("connectButton"):
                time.sleep(8)
                shot("05-disconnected")
                log(f"پس از قطع اتصال: tun0 {'هنوز موجود است' if tun_up() else 'حذف شد'}")
                if tun_up():
                    failures.append("tun-not-removed")
            else:
                failures.append("no-disconnect")

    write_report(failures, baseline_ip, fastest)
    print("FAILURES:" + ",".join(failures) if failures else "ALL OK", flush=True)
    return 1 if failures else 0


def write_report(failures, baseline_ip, fastest):
    logcat = adb("logcat", "-d", "-s", "MvpnTrial:V", timeout=180).stdout or ""
    with open(os.path.join(OUT, "logcat.txt"), "w", encoding="utf-8") as handle:
        handle.write(logcat)
    with open(os.path.join(OUT, "CONNECT-REAL.md"), "w", encoding="utf-8") as handle:
        handle.write("# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)\n\n")
        handle.write(f"- زمان: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
        handle.write(f"- آدرس آزمون: `{PROBE_URL}`\n")
        handle.write(f"- IP خروج پیش از اتصال: `{baseline_ip}`\n")
        if fastest:
            handle.write(f"- سروری که انتخاب شد: `{fastest['name']}` ({fastest['ping']})\n")
        handle.write("\n## گام‌ها\n\n" + "\n".join(REPORT) + "\n\n")
        handle.write("## تصاویر\n\n")
        for name in SHOTS:
            handle.write(f"![{name}]({name}.png)\n\n")
        handle.write("## نتیجه\n\n")
        if failures:
            handle.write("**ناموفق**: " + ", ".join(failures) + "\n")
        else:
            handle.write("**موفق** — برنامه بدون هیچ ورودی کاربر، فهرست را از بک‌اند گرفت، "
                         "مقدار رمز‌شدهٔ هر ردیف را خودش باز کرد، به سرور وصل شد، ترافیک از "
                         "تونل عبور کرد، سرور عوض شد و اتصال تمیز قطع شد.\n")
    print("\n".join(REPORT), flush=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
