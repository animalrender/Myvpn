#!/usr/bin/env python3
"""Drives the MVPN Trial app on a running emulator and captures screenshots.

Used by .github/workflows/ui-snapshot.yml. Reads nothing from the repository, talks only to
`adb`, and matches UI elements by their visible text or content description (so it keeps
working when the layout moves). Every step writes a PNG into the output directory and the
console gets a one line result per step.

Usage:
    python3 tools/ui-drive.py OUT_DIR shot 01-home tap-text "پینگ" sleep 4 shot 02 ...
"""

import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET

OUT = "."
STEPS = []
FAILURES = []
ACTIVITY = "co.asiven.vixentvpn.trial/co.asiven.vixentvpn.trial.ui.MainActivity"
PACKAGE = "co.asiven.vixentvpn.trial"


def adb(*args, timeout=120):
    return subprocess.run(["adb", *args], capture_output=True, text=True, timeout=timeout)


def shell(cmd, timeout=120):
    return adb("shell", cmd, timeout=timeout)


def dump_xml(retries=6):
    for _ in range(retries):
        shell("rm -f /sdcard/window.xml", timeout=30)
        out = shell("uiautomator dump --compressed /sdcard/window.xml", timeout=60)
        if "dumped to" in (out.stdout or "") + (out.stderr or ""):
            raw = adb("exec-out", "cat /sdcard/window.xml", timeout=60)
            text = raw.stdout or ""
            if text.lstrip().startswith("<?xml"):
                return text
        time.sleep(2)
    return ""


def nodes(xml_text):
    if not xml_text:
        return []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    return list(root.iter("node"))


def center(bounds):
    match = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds or "")
    if not match:
        return None
    x1, y1, x2, y2 = (int(v) for v in match.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2


def in_foreground():
    """True when our activity owns the focused window."""
    out = shell("dumpsys window", timeout=60).stdout or ""
    for line in out.splitlines():
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            if PACKAGE in line:
                return True
    return False


def ensure_foreground(reason=""):
    """Brings the app back if the emulator dropped it (screen off, stray HOME, relaunch).

    A screenshot run is worthless if the app is not on screen, so every step starts with this
    check instead of assuming the previous step left the app in front.
    """
    shell("input keyevent KEYCODE_WAKEUP", timeout=30)
    shell("wm dismiss-keyguard", timeout=30)
    if in_foreground():
        return True
    shell(f"am start -W -n {ACTIVITY}", timeout=90)
    time.sleep(3)
    ok = in_foreground()
    print(f"ensure-foreground{' (' + reason + ')' if reason else ''}: {'ok' if ok else 'RELAUNCHED'}")
    STEPS.append(f"ensure-foreground{' (' + reason + ')' if reason else ''}: {'ok' if ok else 'RELAUNCHED'}")
    return ok


def tap_text(target, exact=False):
    for node in nodes(dump_xml()):
        text = node.get("text", "")
        if not text:
            continue
        hit = text == target if exact else (target in text)
        if hit:
            point = center(node.get("bounds"))
            if point:
                shell(f"input tap {point[0]} {point[1]}")
                return True
    return False


def tap_desc(target):
    for node in nodes(dump_xml()):
        if target in (node.get("content-desc") or ""):
            point = center(node.get("bounds"))
            if point:
                shell(f"input tap {point[0]} {point[1]}")
                return True
    return False


def screen_size():
    """Reads the real resolution instead of assuming 1080x1920 (the AVD may be 320x640)."""
    out = shell("wm size", timeout=45).stdout or ""
    match = re.search(r"(\d+)x(\d+)", out)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 1080, 1920


def swipe(up=True):
    width, height = screen_size()
    x = width // 2
    if up:
        start, end = int(height * 0.80), int(height * 0.30)
    else:
        start, end = int(height * 0.30), int(height * 0.80)
    shell(f"input swipe {x} {start} {x} {end} 350")
    time.sleep(1)


def tap_class(class_name):
    """Taps the first node whose class ends with `class_name` (e.g. EditText)."""
    for node in nodes(dump_xml()):
        if (node.get("class") or "").endswith(class_name):
            point = center(node.get("bounds"))
            if point:
                shell(f"input tap {point[0]} {point[1]}")
                return True
    return False


def shot(name):
    path = os.path.join(OUT, name + ".png")
    with open(path, "wb") as handle:
        result = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True, timeout=120)
        handle.write(result.stdout)
    size = os.path.getsize(path)
    print(f"shot {name}: {size} bytes")
    STEPS.append(f"shot {name} ({size} bytes)")
    if size < 5000:
        FAILURES.append(f"{name}: screenshot looks empty ({size} bytes)")


def wait_text(target, seconds=90):
    deadline = time.time() + seconds
    while time.time() < deadline:
        if any(target in (n.get("text") or "") for n in nodes(dump_xml())):
            print(f"wait-text '{target}': found")
            STEPS.append(f"wait-text '{target}': found")
            return True
        time.sleep(3)
    print(f"wait-text '{target}': timeout")
    STEPS.append(f"wait-text '{target}': TIMEOUT")
    FAILURES.append(f"text '{target}' never appeared within {seconds}s")
    return False


def type_from_list():
    """Types the longest ASCII word visible on screen — for this backend that is a country name
    ("Finland"), which proves the search box really filters the list. Chrome words that are part of
    the app itself are ignored."""
    skip = {"MVPN", "Trial", "VPN", "JSON", "Android", "enc", "v2ray"}
    candidates = []
    for node in nodes(dump_xml()):
        for token in re.split(r"[\s\u200c/·]+", (node.get("text") or "").strip()):
            if 3 <= len(token) <= 20 and re.fullmatch(r"[A-Za-z][A-Za-z0-9._-]{2,19}", token) and token not in skip:
                candidates.append(token)
    if not candidates:
        print("type: nothing suitable found")
        STEPS.append("type: skipped (no ASCII server name on screen)")
        return False
    token = max(candidates, key=len)
    shell(f'input text "{token}"')
    print(f"type: '{token}'")
    STEPS.append(f"type '{token}'")
    return True


def crash_check():
    pid = shell("pidof co.asiven.vixentvpn.trial").stdout.strip()
    crash = adb("logcat", "-d", "-b", "crash").stdout or ""
    # Only a fatal exception raised by our own package counts; AndroidRuntime lines from other
    # processes (and "VM exiting" noise) are not a crash of this app.
    fata = [
        line for line in adb("logcat", "-d").stdout.splitlines()
        if "FATAL EXCEPTION" in line or ("co.asiven.vixentvpn.trial" in line and "Process:" in line and "died" in line)
    ]
    ok = bool(pid) and not crash.strip() and not fata
    print(f"crash-check: pid={'yes' if pid else 'no'} crash_buffer={len(crash)} fatal_lines={len(fata)} foreground={in_foreground()}")
    STEPS.append(f"crash-check: pid={'yes' if pid else 'no'}, fatal lines={len(fata)}")
    if not pid:
        FAILURES.append("app process is not running")
    if fata:
        FAILURES.append("crash in logcat: " + fata[0][:200])
    return ok


def write_status():
    """Writes STEPS.txt after every action so a half-finished run still reports what it did."""
    if OUT == ".":
        return
    try:
        with open(os.path.join(OUT, "STEPS.txt"), "w", encoding="utf-8") as handle:
            handle.write("\n".join(STEPS) + "\n")
            handle.write("\nFAILURES:\n" + ("\n".join(FAILURES) if FAILURES else "none") + "\n")
    except OSError:
        pass


def main(argv):
    global OUT
    if len(argv) < 2:
        print(__doc__)
        return 2
    OUT = argv[0]
    os.makedirs(OUT, exist_ok=True)
    rest = argv[1:]
    index = 0
    while index < len(rest):
        cmd = rest[index]
        ensure_foreground(cmd)
        if cmd == "shot":
            shot(rest[index + 1]); index += 2
        elif cmd == "tap-text":
            ok = tap_text(rest[index + 1])
            print(f"tap-text '{rest[index + 1]}': {'ok' if ok else 'NOT FOUND'}")
            STEPS.append(f"tap-text '{rest[index + 1]}': {'ok' if ok else 'NOT FOUND'}")
            if not ok:
                FAILURES.append(f"text '{rest[index + 1]}' not found")
            index += 2
        elif cmd == "tap-text-exact":
            ok = tap_text(rest[index + 1], exact=True)
            print(f"tap-text-exact '{rest[index + 1]}': {'ok' if ok else 'NOT FOUND'}")
            STEPS.append(f"tap-text-exact '{rest[index + 1]}': {'ok' if ok else 'NOT FOUND'}")
            if not ok:
                FAILURES.append(f"text '{rest[index + 1]}' not found")
            index += 2
        elif cmd == "tap-desc":
            ok = tap_desc(rest[index + 1])
            print(f"tap-desc '{rest[index + 1]}': {'ok' if ok else 'NOT FOUND'}")
            STEPS.append(f"tap-desc '{rest[index + 1]}': {'ok' if ok else 'NOT FOUND'}")
            if not ok:
                FAILURES.append(f"content-desc '{rest[index + 1]}' not found")
            index += 2
        elif cmd == "tap-class":
            ok = tap_class(rest[index + 1])
            print(f"tap-class '{rest[index + 1]}': {'ok' if ok else 'NOT FOUND'}")
            STEPS.append(f"tap-class '{rest[index + 1]}': {'ok' if ok else 'NOT FOUND'}")
            if not ok:
                FAILURES.append(f"no view of class {rest[index + 1]}")
            index += 2
        elif cmd == "type-from-list":
            type_from_list(); index += 1
        elif cmd == "wait-text":
            wait_text(rest[index + 1], int(rest[index + 2])); index += 3
        elif cmd == "sleep":
            time.sleep(float(rest[index + 1])); index += 2
        elif cmd == "back":
            shell("input keyevent 4"); time.sleep(1); index += 1
        elif cmd == "swipe-up":
            swipe(True); index += 1
        elif cmd == "swipe-down":
            swipe(False); index += 1
        elif cmd == "crash-check":
            crash_check(); index += 1
        elif cmd == "dump":
            path = os.path.join(OUT, rest[index + 1] + ".xml")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(dump_xml())
            index += 2
        else:
            print(f"unknown step: {cmd}")
            FAILURES.append(f"unknown step {cmd}")
            index += 1
        write_status()

    write_status()
    if FAILURES:
        print("::error title=ui-snapshot::" + " | ".join(FAILURES)[:900])
        return 1
    print("::notice title=ui-snapshot::all steps ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
