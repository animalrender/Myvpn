#!/usr/bin/env python3
"""End-to-end connection test for MVPN Trial — runs on an Android emulator inside CI.

Unlike `ui-drive.py` (a generic screenshot walker) this script is a *functional* test:
it imports a real VLESS server, connects the tunnel, pushes traffic through it and
asserts that the traffic really left through the Xray server. Every observation is
written to `CONNECT.md` in the output directory so the run can be reviewed from the
repository without access to the Actions log.

Layout of the test round:

  1. import      `adb shell am start -a android.intent.action.VIEW -d vless://…`
                 (the app registers those schemes, same as v2rayNG)
  2. connect     tap the imported row, tap «اتصال», accept the system VPN dialog
  3. tunnel      request a URL from the *shell* uid (its traffic is routed into the TUN),
                 then grep the Xray server access log — proof that the bytes went
                 through the tunnel and out of the server
  4. stability   run «پینگ همه» while connected and assert the selected/connected
                 server did not change (the defect seen in the original APK)
  5. teardown    tap «قطع اتصال», assert the notification/tun are gone

Usage: connect-drive.py <out-dir> <server-name> <vless-uri> <access-log> <probe-url>
"""

import os
import re
import subprocess
import sys
import time
import urllib.parse

OUT = "."
SERVER_NAME = "CI-Local"
VLESS_URI = ""
ACCESS_LOG = "/tmp/xray-access.log"
PROBE_URL = "https://www.gstatic.com/generate_204"
REPORT = []
SHOTS = []


def log(message):
    line = f"- {message}"
    print(message, flush=True)
    REPORT.append(line)


def shot(name):
    path = os.path.join(OUT, f"{name}.png")
    subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=open(path, "wb"),
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
        result = adb("exec-out", "uiautomator dump /dev/tty", timeout=120)
        text = result.stdout or ""
        match = re.search(r"<\?xml.*</hierarchy>", text, re.S)
        if match:
            return match.group(0)
        time.sleep(2)
    return ""


def nodes(xml_text):
    found = []
    for match in re.finditer(r"<node[^>]*>", xml_text):
        tag = match.group(0)
        attrs = dict(re.findall(r'([\w:-]+)="([^"]*)"', tag))
        found.append(attrs)
    return found


def center(bounds):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
    if not match:
        return None
    x1, y1, x2, y2 = (int(v) for v in match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2


def tap(point):
    shell(f"input tap {point[0]} {point[1]}")


def find(text=None, desc=None, res_id=None, exact=False):
    for node in nodes(dump_xml()):
        if res_id and node.get("resource-id", "").endswith(res_id):
            return node
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
    if not node:
        return False
    point = center(node.get("bounds"))
    if not point:
        return False
    tap(point)
    return True


def tap_desc(desc):
    node = find(desc=desc)
    if not node:
        return False
    point = center(node.get("bounds"))
    if not point:
        return False
    tap(point)
    return True


def accept_vpn_dialog():
    """The system VPN consent dialog lives in com.android.vpndialogs, not in our app."""
    for _ in range(25):
        xml = dump_xml()
        for node in nodes(xml):
            rid = node.get("resource-id", "")
            text = (node.get("text") or "").strip()
            if rid.endswith("button1") or text in ("OK", "Allow", "تأیید", "باشه"):
                point = center(node.get("bounds"))
                if point:
                    tap(point)
                    return True
        time.sleep(2)
    return False


def logcat_tail(tag="MvpnTrial", lines=400):
    result = adb("logcat", "-d", "-s", f"{tag}:V", timeout=120)
    return "\n".join((result.stdout or "").splitlines()[-lines:])


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
    """`curl` is present on the recent emulator images; `nc` from toybox is the fallback."""
    global _TOOL
    if _TOOL:
        return _TOOL
    for candidate in ("curl", "nc"):
        out = shell(f"command -v {candidate}").stdout or ""
        out = out.strip()
        if out and "not found" not in out:
            _TOOL = candidate
            return _TOOL
    _TOOL = "none"
    return _TOOL


def probe_from_shell(label, url=PROBE_URL):
    """Traffic generated by the `shell` uid is routed into the TUN, so it must appear in the
    Xray server access log if the tunnel really works."""
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
        body = (result.stdout or "")
        first = body.splitlines()[0] if body.splitlines() else ""
        code = "204" if "204" in first else (first[:40] or "no-response")
    else:
        code = "no-http-tool"
    log(f"ابزار آزمون ترافیک داخل دستگاه: {tool}")
    time.sleep(3)
    fresh = access_log_new(offset)
    accepted = bool(re.search(r"\b(accepted|tcp:)", fresh))
    log(f"curl از پوستهٔ ادمین ({label}): خروجی={code!r} — ردِ سرور: "
        f"{'دیده شد' if accepted else 'دیده نشد'} ({len(fresh)} بایت لاگ تازه)")
    if fresh.strip():
        first = fresh.strip().splitlines()[0][:160]
        log(f"  نمونهٔ لاگ سرور: `{first}`")
    return code, accepted, fresh


def main(argv):
    global OUT, SERVER_NAME, VLESS_URI, ACCESS_LOG, PROBE_URL
    if len(argv) < 3:
        print(__doc__)
        return 2
    OUT = argv[0]
    SERVER_NAME = argv[1]
    VLESS_URI = argv[2]
    if len(argv) > 3:
        ACCESS_LOG = argv[3]
    if len(argv) > 4:
        PROBE_URL = argv[4]
    os.makedirs(OUT, exist_ok=True)
    failures = []

    # ---------------------------------------------------------------- 1. import
    log(f"ورود کانفیگ با intent: `{VLESS_URI[:60]}…`")
    component = "co.asiven.vixentvpn/co.asiven.vixentvpn.trial.ui.MainActivity"
    adb("shell", f"am start -a android.intent.action.VIEW -d '{VLESS_URI}' -n {component}",
        timeout=120)
    imported = wait_for(text=SERVER_NAME, seconds=90)
    shot("01-imported")
    if imported:
        log("کانفیگ در فهرست دیده شد")
    else:
        log("**کانفیگ واردشده در فهرست پیدا نشد**")
        failures.append("import")

    # ---------------------------------------------------------------- 2. connect
    if imported:
        point = center(imported.get("bounds"))
        tap(point)
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
            log("**دیالوگ مجوز VPN دیده نشد (احتمالاً از قبل تأیید شده بود)**")
        connected = wait_for(text="متصل", seconds=90)
        shot("03-connected")
        if connected:
            log("وضعیت «متصل» در برنامه دیده شد")
        else:
            log("**برنامه به وضعیت متصل نرسید**")
            failures.append("not-connected")

        time.sleep(6)
        tun = shell("ip -4 addr show tun0")
        tun_out = (tun.stdout or "").strip()
        log(f"رابط tun0 در دستگاه: {'موجود' if 'inet ' in tun_out else 'موجود نیست'}")
        if "inet " not in tun_out:
            failures.append("no-tun")

        # ------------------------------------------------------------ 3. tunnel
        code, accepted, _ = probe_from_shell("HTTPS")
        if code != "204":
            failures.append(f"probe-http-{code or 'none'}")
        if not accepted:
            failures.append("server-never-saw-traffic")
        code2, accepted2, _ = probe_from_shell("HTTP", "http://connectivitycheck.gstatic.com/generate_204")
        if code2 != "204" and code != "204":
            failures.append("probe-http-plain")

        # a second, independent probe through a different host
        probe_from_shell("IPv4", "http://1.1.1.1/")
        shot("04-traffic")

        # ------------------------------------------------------------ 4. stability
        log("اجرای «پینگ همه» روی اتصال برقرار")
        if tap_text("پینگ همه", exact=True):
            time.sleep(25)
        shot("05-ping-all")
        still = find(text=SERVER_NAME)
        status_node = None
        for node in nodes(dump_xml()):
            if (node.get("text") or "").startswith(("متصل", "انتخاب‌شده", "در حال")):
                status_node = node
                break
        status_text = (status_node or {}).get("text", "")
        log(f"وضعیت بعد از پینگ همه: `{status_text}`")
        if status_text.startswith("انتخاب‌شده") or not status_text:
            log("**پس از پینگ همه، اتصال/انتخاب عوض شد (همان نقص اپ اصلی)**")
            failures.append("selection-changed-after-ping-all")
        if still is None:
            log("**ردیف سرور متصل بعد از پینگ همه ناپدید شد**")
            failures.append("row-vanished")

        # ------------------------------------------------------------ 5. teardown
        if tap_text("قطع اتصال", exact=True):
            time.sleep(6)
            shot("06-disconnected")
            off = find(text="قطع", exact=False)
            tun_after = shell("ip -4 addr show tun0").stdout or ""
            log(f"پس از قطع: tun0 {'هنوز موجود است' if 'inet ' in tun_after else 'حذف شد'}")
            if "inet " in tun_after:
                failures.append("tun-not-removed")
        else:
            log("**دکمهٔ قطع اتصال پیدا نشد**")
            failures.append("disconnect-button")

    # ---------------------------------------------------------------- report
    with open(os.path.join(OUT, "logcat.txt"), "w", encoding="utf-8") as handle:
        handle.write(logcat_tail())
    with open(os.path.join(OUT, "CONNECT.md"), "w", encoding="utf-8") as handle:
        handle.write("# آزمون اتصال واقعی (CI)\n\n")
        handle.write(f"- زمان: {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n")
        handle.write(f"- سرور آزمون: `{SERVER_NAME}`\n")
        handle.write(f"- کانفیگ: `{VLESS_URI[:70]}…`\n")
        handle.write(f"- آدرس آزمون: `{PROBE_URL}`\n\n")
        handle.write("## گام‌ها\n\n" + "\n".join(REPORT) + "\n\n")
        handle.write("## تصاویر\n\n")
        for name in SHOTS:
            handle.write(f"![{name}]({name}.png)\n\n")
        handle.write("## نتیجه\n\n")
        if failures:
            handle.write("**ناموفق**: " + ", ".join(failures) + "\n")
        else:
            handle.write("**موفق** — ورود کانفیگ، اتصال، عبور ترافیک از تونل، "
                         "پایداری انتخاب سرور و قطع اتصال همه درست کار کردند.\n")
    print("FAILURES:" + ",".join(failures) if failures else "ALL OK", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
