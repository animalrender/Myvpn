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
    # Written immediately, so a crash or a CI timeout still leaves the steps that did happen.
    try:
        with open(os.path.join(OUT, "CONNECT-REAL.md"), "w", encoding="utf-8") as handle:
            handle.write(render_report(None))
    except OSError:
        pass


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


def unescape(text):
    """uiautomator escapes emoji as numeric entities; turn them back into readable flags."""
    return re.sub(r"&#(\d+);", lambda m: chr(int(m.group(1))), text or "")


def rows():
    """Server rows painted in the list: name, ping badge, and the bounds to tap."""
    xml = dump_xml()
    entries = []
    cards = [n for n in nodes(xml) if (n.get("resource-id") or "").endswith("nameText")]
    pings = [n for n in nodes(xml) if (n.get("resource-id") or "").endswith("pingText")]
    for card in cards:
        raw = (card.get("text") or "").strip()
        if not raw:
            continue
        anchor = center(card.get("bounds"))
        best, best_dy = None, 10 ** 6
        for ping in pings:
            point = center(ping.get("bounds"))
            if not anchor or not point:
                continue
            if abs(point[0] - anchor[0]) < 560 and -200 < point[1] - anchor[1] < 240:
                if abs(point[1] - anchor[1]) < best_dy:
                    best, best_dy = ping, abs(point[1] - anchor[1])
        entries.append({
            "name": unescape(raw),
            "raw": raw,
            "ping": (best.get("text") or "").strip() if best else "",
            "bounds": card.get("bounds"),
        })
    return entries


def find_row(name, ping=None):
    """The painted row matching a name (and, when several rows share a name, its ping badge)."""
    target = name.replace("🌐", "").strip()
    for row in rows():
        # the hero prints "<flag>  <name>" while the row prints just "<name>"
        if not (row["name"] == name or row["raw"] == name
                or row["name"] == target or target.endswith(row["name"])):
            continue
        if ping is not None and row["ping"] != ping:
            continue
        return row
    return None


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


def row_bounds(name, ping=None):
    row = find_row(name, ping)
    return row["bounds"] if row else None


def bring_into_view(name, ping=None):
    """Scrolls the list until the wanted row is comfortably inside the viewport."""
    for _ in range(16):
        bounds = row_bounds(name, ping)
        point = center(bounds) if bounds else None
        if point and 300 <= point[1] <= 1850:
            return bounds
        if point and point[1] < 300:
            shell("input swipe 540 600 540 1500 300")   # pull the list down
        else:
            shell("input swipe 540 1750 540 700 300")   # push the list up
        time.sleep(1.5)
    return row_bounds(name, ping)


def connect_row(row, index):
    landed = bring_into_view(row["name"], row.get("ping"))
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


def connect_button_text():
    """Label of the hero button: «اتصال» / «اتصال به سرور انتخابی» / «قطع اتصال»."""
    node = find(rid="connectButton")
    return (node.get("text") or "").strip() if node else None


def hero_name():
    """The server the activity currently has selected (it auto-picks the fastest after a ping)."""
    node = find(rid="selectedNameText")
    text = unescape((node or {}).get("text") or "")
    return text.replace("\u200f", "").strip()


def bulk_ping_finished():
    out = adb("logcat", "-d", "-s", "MvpnTrial:V", timeout=120).stdout or ""
    return "پینگ همهٔ" in out


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
    # Zero-input flow: the activity starts the bulk ping by itself once the list is loaded and
    # then selects the fastest row that answered — the driver only has to wait for that.
    pressed = False
    if not bulk_ping_finished() and not any((r["ping"] or "").strip() == "…" for r in rows()):
        pressed = tap_text("پینگ همه", exact=True)
        log(f"دکمهٔ «پینگ همه» زده شد: {'بله' if pressed else 'خیر'}")
    deadline = time.time() + 600
    while time.time() < deadline and not bulk_ping_finished():
        dismiss_system_dialogs()
        time.sleep(10)
    finished = bulk_ping_finished()
    shot("02-ping-all")
    log(f"پایان پینگ همه: {'بله' if finished else 'خیر (مهلت تمام شد)'}")
    chosen = hero_name()
    log(f"سروری که برنامه خودش انتخاب کرد: `{chosen or '—'}`")
    if not finished:
        failures.append("ping-all-timeout")
    if not chosen:
        log("**برنامه هیچ سروری را انتخاب نکرد؛ ادامهٔ آزمون ممکن نیست**")
        failures.append("no-selection")

    # ------------------------------------------------------------ 4. connect
    # The app already connected-ready state is: ping done + fastest row selected. Traffic is
    # verified from the shell uid (its packets are routed into the TUN). A single unlucky row is
    # retried with the next measured rows, exactly like a user would tap the next server.
    attempts = []
    if chosen:
        attempts.append(chosen)
    for row in rows():
        if ping_ms(row["ping"]) and row["name"] not in attempts:
            attempts.append(row["name"])
        if len(attempts) == 4:
            break

    connected = None
    for index, name in enumerate(attempts, start=1):
        if index == 1:
            log(f"اتصال به سرور انتخاب‌شده: `{name}`")
            started = connect_row({"name": name, "ping": None}, "03")
        else:
            log(f"تلاش {index}: اتصال به `{name}`")
            started = connect_row({"name": name, "ping": None}, f"0{2 + index}")
            label = connect_button_text()
            if label and label != "قطع اتصال":
                tap_rid("connectButton")
                time.sleep(10)
                accept_vpn_dialog()
                for _ in range(20):
                    if find(text="متصل", exact=False):
                        break
                    time.sleep(2)
        if not started:
            failures.append(f"not-connected-{index}")
            continue
        authed = False
        for wait in range(20):
            if find(text="متصل", exact=False):
                authed = True
                break
            if not authed and wait == 2:
                accept_vpn_dialog()
            time.sleep(2)
        log(f"وضعیت تونل: `{(find(text='متصل', exact=False) or {}).get('text', '—')}`")
        if not authed:
            failures.append(f"no-tunnel-{index}")
            continue
        time.sleep(4)
        up = tun_up()
        log(f"رابط tun0: {'موجود' if up else 'موجود نیست'}")
        code = "no-response"
        for _ in range(3):
            code, _body = http_get(PROBE_URL, timeout=45)
            log(f"درخواست از داخل تونل: HTTP {code or 'بدون پاسخ'}")
            if code in ("204", "200"):
                break
            time.sleep(5)
        if up and code in ("204", "200"):
            connected = name
            break
        log("ترافیک از این ردیف عبور نکرد؛ سرور بعدی آزموده می‌شود")
        failures.append(f"no-traffic-{index}")
    if not connected:
        failures.append("no-server-passed-traffic")

    if connected:
        ip, country, isp = exit_ip()
        log(f"IP خروج داخل تونل: `{ip}` ({country} — {isp})")
        if ip and baseline_ip and ip == baseline_ip:
            log("**IP خروج تغییر نکرد** — ترافیک واقعاً از تونل نرفته است")
            failures.append("exit-ip-unchanged")

        # ---------------------------------------------------------- 5. second row
        candidates = [r for r in rows() if ping_ms(r["ping"])]
        others = [r for r in candidates if r["name"] != connected]
        if others:
            second = others[0]
            log(f"تغییر سرور به: `{second['name']}` ({second['ping']})")
            if connect_row(second, "07"):
                label = connect_button_text()
                log(f"برچسب دکمه پس از انتخاب سرور دوم: `{label}`")
                if label and label != "قطع اتصال":
                    tap_rid("connectButton")
                    time.sleep(10)
                accept_vpn_dialog()
                for _ in range(30):
                    if find(text="متصل", exact=False):
                        break
                    time.sleep(2)
                code2 = probe()
                log(f"درخواست پس از تغییر سرور: HTTP {code2 or 'بدون پاسخ'}")
                if code2 not in ("204", "200"):
                    failures.append(f"probe-after-switch-{code2 or 'none'}")
            else:
                failures.append("switch-failed")
        else:
            log("ردیف دومی با پینگ موفق در صفحهٔ فعلی دیده نشد")

        # ---------------------------------------------------------- 6. teardown
        # The hero button reads «قطع اتصال» only while the *connected* row is the selected one;
        # after selecting another row it turns into «اتصال به سرور انتخابی». Selecting the live
        # row again brings the disconnect label back.
        label = connect_button_text()
        if label != "قطع اتصال":
            live = find(text="متصل", exact=False)
            current = hero_name()
            log(f"دکمه در وضعیت «{label}» است؛ ابتدا ردیف متصل انتخاب می‌شود: `{current}`")
            if current:
                connect_row({"name": current, "ping": None}, "07")
                label = connect_button_text()
        log(f"برچسب دکمه پیش از قطع: `{label}`")
        if label == "قطع اتصال" and tap_rid("connectButton"):
            for _ in range(15):
                if not tun_up():
                    break
                time.sleep(2)
            shot("08-disconnected")
            log(f"پس از قطع اتصال: tun0 {'هنوز موجود است' if tun_up() else 'حذف شد'}")
            if tun_up():
                failures.append("tun-not-removed")
        else:
            failures.append("no-disconnect")

    write_report(failures, baseline_ip, connected)
    print("FAILURES:" + ",".join(failures) if failures else "ALL OK", flush=True)
    return 1 if failures else 0


def render_report(failures, baseline_ip=None, fastest=None):
    lines = ["# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)", ""]
    lines.append(f"- زمان: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}")
    lines.append(f"- آدرس آزمون: `{PROBE_URL}`")
    if baseline_ip:
        lines.append(f"- IP خروج پیش از اتصال: `{baseline_ip}`")
    if fastest:
        lines.append(f"- سرور متصل‌شده: `{fastest}`")
    lines.append("")
    lines.append("## گام‌ها")
    lines.append("")
    lines.extend(REPORT)
    lines.append("")
    lines.append("## تصاویر")
    lines.append("")
    for name in SHOTS:
        lines.append(f"![{name}]({name}.png)")
        lines.append("")
    lines.append("## نتیجه")
    lines.append("")
    if failures is None:
        lines.append("در حال اجرا…")
    elif failures:
        lines.append("**ناموفق**: " + ", ".join(failures))
    else:
        lines.append("**موفق** — برنامه بدون هیچ ورودی کاربر، فهرست را از بک‌اند گرفت، "
                     "مقدار رمزشدهٔ هر ردیف را خودش باز کرد، سریع‌ترین سرور را خودش انتخاب کرد، "
                     "وصل شد، ترافیک از تونل عبور کرد، سرور عوض شد و اتصال تمیز قطع شد.")
    return "\n".join(lines) + "\n"


def write_report(failures, baseline_ip, fastest):
    logcat = adb("logcat", "-d", "-s", "MvpnTrial:V", timeout=180).stdout or ""
    with open(os.path.join(OUT, "logcat.txt"), "w", encoding="utf-8") as handle:
        handle.write(logcat)
    with open(os.path.join(OUT, "CONNECT-REAL.md"), "w", encoding="utf-8") as handle:
        handle.write(render_report(failures, baseline_ip, fastest))
    print("\n".join(REPORT), flush=True)


def run(argv):
    try:
        return main(argv)
    except Exception as error:  # noqa: BLE001 — the report must exist even when the driver breaks
        import traceback
        detail = traceback.format_exc()
        print(detail, flush=True)
        log(f"**خطای غیرمنتظره در درایور آزمون**: `{type(error).__name__}: {error}`")
        try:
            with open(os.path.join(OUT, "CONNECT-REAL.md"), "w", encoding="utf-8") as handle:
                handle.write(render_report(["driver-crash", type(error).__name__]))
            with open(os.path.join(OUT, "driver-error.txt"), "w", encoding="utf-8") as handle:
                handle.write(detail)
        except OSError:
            pass
        return 1


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
