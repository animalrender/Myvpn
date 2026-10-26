#!/usr/bin/env python3
"""End-to-end connection test for MVPN Trial — runs on an Android emulator inside CI.

Unlike `ui-drive.py` (a generic screenshot walker) this script is a *functional* test.
It imports real configs, connects the tunnel, pushes traffic through it and asserts that the
traffic really left through the Xray server. Every observation is written to `CONNECT.md` in
the output directory, so the run can be reviewed from the repository without the Actions log.

Rounds:

  1. import      `adb shell am start -a android.intent.action.VIEW -d vless://…`
                 (the app registers those schemes, exactly like v2rayNG)
  2. connect     tap the imported row, tap «اتصال», accept the system VPN dialog
  3. tunnel      request a URL from the *shell* uid (its traffic is routed into the TUN) and
                 grep the Xray server access log — proof the bytes went through the tunnel
  4. stability   run «پینگ همه» while connected and assert the live server did not change
                 (the defect observed in the original APK)
  5. switch      import a second config, press «اتصال به سرور انتخابی» and assert the tunnel
                 moved to the new server (and that traffic still flows)
  6. teardown    tap «قطع اتصال» and assert tun0 is gone

Usage:
  connect-drive.py <out-dir> <access-log> <probe-url> <name>=<uri> [<name>=<uri> …]
"""

import os
import re
import subprocess
import sys
import time
import urllib.parse

OUT = "."
ACCESS_LOG = "/tmp/xray-access.log"
PROBE_URL = "https://www.gstatic.com/generate_204"
REPORT = []
SHOTS = []


def log(message):
    print(message, flush=True)
    REPORT.append(f"- {message}")


def shot(name):
    path = os.path.join(OUT, f"{name}.png")
    with open(path, "wb") as handle:
        subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=handle,
                       stderr=subprocess.DEVNULL, timeout=120)
    SHOTS.append(name)


def adb(*args, timeout=180):
    try:
        return subprocess.run(["adb", *args], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(["adb", *args], 1, "", "timeout")


def shell(command, timeout=180):
    return adb("shell", command, timeout=timeout)


def dump_xml():
    for _ in range(4):
        text = adb("exec-out", "uiautomator dump /dev/tty", timeout=120).stdout or ""
        match = re.search(r"<\?xml.*</hierarchy>", text, re.S)
        if match:
            return match.group(0)
        time.sleep(2)
    return ""


def nodes(xml_text):
    found = []
    for match in re.finditer(r"<node[^>]*>", xml_text):
        found.append(dict(re.findall(r'([\w:-]+)="([^"]*)"', match.group(0))))
    return found


def center(bounds):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
    if not match:
        return None
    x1, y1, x2, y2 = (int(v) for v in match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2


def tap(point):
    shell(f"input tap {point[0]} {point[1]}")


def find(text=None, desc=None, exact=False):
    for node in nodes(dump_xml()):
        if text:
            value = node.get("text", "")
            if value and (value == text if exact else text in value):
                return node
        if desc and desc in (node.get("content-desc") or ""):
            return node
    return None


def wait_for(text=None, desc=None, seconds=90, exact=False):
    deadline = time.time() + seconds
    while time.time() < deadline:
        node = find(text=text, desc=desc, exact=exact)
        if node:
            return node
        time.sleep(2)
    return None


def tap_text(text, exact=False):
    node = find(text=text, exact=exact)
    point = center(node.get("bounds")) if node else None
    if not point:
        return False
    tap(point)
    return True


def tap_desc(desc):
    node = find(desc=desc)
    point = center(node.get("bounds")) if node else None
    if not point:
        return False
    tap(point)
    return True


def accept_vpn_dialog():
    """The system VPN consent dialog belongs to com.android.vpndialogs, not to our app."""
    for _ in range(25):
        for node in nodes(dump_xml()):
            text = (node.get("text") or "").strip()
            if node.get("resource-id", "").endswith("button1") or text in ("OK", "Allow", "تأیید", "باشه"):
                point = center(node.get("bounds"))
                if point:
                    tap(point)
                    return True
        time.sleep(2)
    return False


def access_log_size():
    try:
        return os.path.getsize(ACCESS_LOG)
    except OSError:
        return 0


def access_log_new(offset):
    try:
        with open(ACCESS_LOG, "r", errors="replace") as handle:
            handle.seek(offset)
            return handle.read()
    except OSError:
        return ""


_TOOL = None


def shell_http_tool():
    """`curl` is present on the recent emulator images; toybox `nc` is the fallback."""
    global _TOOL
    if _TOOL:
        return _TOOL
    for candidate in ("curl", "nc"):
        out = (shell(f"command -v {candidate}").stdout or "").strip()
        if out and "not found" not in out:
            _TOOL = candidate
            return _TOOL
    _TOOL = "none"
    return _TOOL


def probe_from_shell(label, url=PROBE_URL):
    """Traffic generated by the `shell` uid is routed into the TUN, so it has to show up in the
    Xray server access log when the tunnel really works."""
    offset = access_log_size()
    tool = shell_http_tool()
    if tool == "curl":
        result = shell(f"curl -s -m 20 -o /dev/null -w '%{{http_code}}' {url}")
        code = (result.stdout or "").strip().splitlines()[-1] if result.stdout else ""
    elif tool == "nc":
        host = urllib.parse.urlparse(url).hostname or "www.gstatic.com"
        result = shell(
            f"printf 'GET /generate_204 HTTP/1.1\\r\\nHost: {host}\\r\\n"
            f"Connection: close\\r\\n\\r\\n' | nc -w 15 {host} 80"
        )
        body = result.stdout or ""
        first = body.splitlines()[0] if body.splitlines() else ""
        code = "204" if "204" in first else (first[:40] or "no-response")
    else:
        code = "no-http-tool"
    time.sleep(3)
    fresh = access_log_new(offset)
    accepted = bool(re.search(r"\b(accepted|tcp:)", fresh))
    log(f"درخواست از پوستهٔ ادمین ({label}): خروجی={code!r} — ردِ سرور: "
        f"{'دیده شد' if accepted else 'دیده نشد'} ({len(fresh)} بایت لاگ تازه)")
    if fresh.strip():
        log(f"  نمونهٔ لاگ سرور: `{fresh.strip().splitlines()[0][:160]}`")
    return code, accepted


def import_config(uri, name):
    component = "co.asiven.vixentvpn/co.asiven.vixentvpn.trial.ui.MainActivity"
    adb("shell", f"am start -a android.intent.action.VIEW -d '{uri}' -n {component}", timeout=120)
    return wait_for(text=name, seconds=90)


def connect_button_text():
    """The button carries one of three labels depending on the tunnel state."""
    for label in ("اتصال به سرور انتخابی", "اتصال", "قطع اتصال"):
        if find(text=label, exact=True):
            return label
    return None


def main(argv):
    global OUT, ACCESS_LOG, PROBE_URL
    if len(argv) < 4:
        print(__doc__)
        return 2
    OUT, ACCESS_LOG, PROBE_URL = argv[0], argv[1], argv[2]
    servers = []
    for item in argv[3:]:
        name, _, uri = item.partition("=")
        servers.append((name, uri))
    os.makedirs(OUT, exist_ok=True)
    failures = []
    connected_ok = False

    # ---------------------------------------------------------------- 1. import + connect
    name_a, uri_a = servers[0]
    log(f"ورود کانفیگ اول با intent: `{uri_a[:60]}…`")
    row_a = import_config(uri_a, name_a)
    shot("01-imported")
    if not row_a:
        log("**کانفیگ واردشده در فهرست پیدا نشد**")
        failures.append("import")
        row_a = None
    else:
        log(f"کانفیگ «{name_a}» در فهرست دیده شد")

    if row_a:
        tap(center(row_a.get("bounds")))
        time.sleep(2)
        shot("02-selected")
        if tap_text("اتصال", exact=True) or tap_desc("اتصال"):
            log("دکمهٔ اتصال زده شد")
        else:
            log("**دکمهٔ اتصال پیدا نشد**")
            failures.append("connect-button")
        time.sleep(4)
        if accept_vpn_dialog():
            log("دیالوگ مجوز VPN تأیید شد")
        else:
            log("دیالوگ مجوز VPN دیده نشد (احتمالاً از قبل تأیید شده بود)")
        connected = wait_for(text=f"متصل — {name_a}", seconds=120)
        connected_ok = connected is not None
        shot("03-connected")
        if connected:
            log(f"وضعیت «متصل — {name_a}» دیده شد")
        else:
            log("**برنامه به وضعیت متصل نرسید**")
            failures.append("not-connected")

        time.sleep(5)
        tun_out = (shell("ip -4 addr show tun0").stdout or "")
        log(f"رابط tun0: {'موجود' if 'inet ' in tun_out else 'موجود نیست'}")
        if connected_ok and "inet " not in tun_out:
            failures.append("no-tun")

        # ------------------------------------------------------------ 2. traffic
        code, accepted = probe_from_shell("HTTPS", PROBE_URL)
        if connected_ok:
            if code != "204":
                failures.append(f"probe-http-{code or 'none'}")
            if not accepted:
                failures.append("server-never-saw-traffic")
        code2, _ = probe_from_shell("HTTP", "http://connectivitycheck.gstatic.com/generate_204")
        if connected_ok and code2 != "204" and code != "204":
            failures.append("probe-http-plain")
        shot("04-traffic")

        # ------------------------------------------------------------ 3. stability
        log("اجرای «پینگ همه» و بررسی اینکه سرور متصل عوض نشود")
        if tap_text("پینگ همه", exact=True):
            time.sleep(25)
        shot("05-ping-all")
        status = ""
        for node in nodes(dump_xml()):
            text = node.get("text") or ""
            if text.startswith(("متصل", "انتخاب‌شده", "در حال", "خطا")):
                status = text
                break
        log(f"وضعیت بعد از پینگ همه: `{status}`")
        if connected_ok and not status.startswith("متصل"):
            log("**پس از پینگ همه، اتصال عوض شد (همان نقص اپ اصلی)**")
            failures.append("selection-changed-after-ping-all")

        # ------------------------------------------------------------ 4. switch server
        if len(servers) > 1:
            name_b, uri_b = servers[1]
            log(f"ورود کانفیگ دوم: `{uri_b[:60]}…`")
            row_b = import_config(uri_b, name_b)
            if not row_b:
                log("**کانفیگ دوم در فهرست پیدا نشد**")
                failures.append("import-second")
            else:
                shot("06-second-imported")
                label = connect_button_text()
                log(f"برچسب دکمهٔ اتصال در این حالت: `{label}`")
                if label and tap_text(label, exact=True):
                    log("درخواست تغییر سرور زده شد")
                else:
                    failures.append("switch-button")
                switched = wait_for(text=f"متصل — {name_b}", seconds=120)
                shot("07-switched")
                if switched:
                    log(f"تونل به «{name_b}» منتقل شد")
                    code3, _ = probe_from_shell("HTTPS بعد از تغییر سرور", PROBE_URL)
                    if code3 != "204":
                        failures.append(f"probe-after-switch-{code3 or 'none'}")
                    tun_b = (shell("ip -4 addr show tun0").stdout or "")
                    if "inet " not in tun_b:
                        failures.append("no-tun-after-switch")
                else:
                    log("**تونل به سرور دوم منتقل نشد**")
                    failures.append("switch-failed")

        # ------------------------------------------------------------ 5. teardown
        if tap_text("قطع اتصال", exact=True):
            time.sleep(8)
            shot("08-disconnected")
            tun_after = (shell("ip -4 addr show tun0").stdout or "")
            log(f"پس از قطع: tun0 {'هنوز موجود است' if 'inet ' in tun_after else 'حذف شد'}")
            if "inet " in tun_after:
                failures.append("tun-not-removed")
        else:
            log("**دکمهٔ قطع اتصال پیدا نشد**")
            failures.append("disconnect-button")

    # ---------------------------------------------------------------- report
    logcat = adb("logcat", "-d", "-s", "MvpnTrial:V", timeout=120).stdout or ""
    with open(os.path.join(OUT, "logcat.txt"), "w", encoding="utf-8") as handle:
        handle.write(logcat)
    with open(os.path.join(OUT, "CONNECT.md"), "w", encoding="utf-8") as handle:
        handle.write("# آزمون اتصال واقعی (CI)\n\n")
        handle.write(f"- زمان: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
        handle.write(f"- سرورهای آزمون: {', '.join('`' + n + '`' for n, _ in servers)}\n")
        handle.write(f"- آدرس آزمون: `{PROBE_URL}`\n\n")
        handle.write("## گام‌ها\n\n" + "\n".join(REPORT) + "\n\n")
        handle.write("## تصاویر\n\n")
        for name in SHOTS:
            handle.write(f"![{name}]({name}.png)\n\n")
        handle.write("## نتیجه\n\n")
        if failures:
            handle.write("**ناموفق**: " + ", ".join(failures) + "\n")
        else:
            handle.write("**موفق** — ورود کانفیگ، اتصال، عبور ترافیک از تونل، پایداری سرور "
                         "هنگام پینگ همه، تغییر سرور در حال اتصال و قطع اتصال همه درست کار کردند.\n")
    print("FAILURES:" + ",".join(failures) if failures else "ALL OK", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
