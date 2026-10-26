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


def adb(*args, timeout=120):
    return subprocess.run(["adb", *args], capture_output=True, text=True, timeout=timeout)


def shell(cmd, timeout=120):
    return adb("shell", cmd, timeout=timeout)


def dump_xml(retries=6):
    for _ in range(retries):
        out = shell("uiautomator dump /sdcard/window.xml", timeout=60)
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
    """Types the first ASCII word of a server name — proves the search box filters the list."""
    skip = re.compile(r"(MVPN|VPN|^[0-9:/.]+$|^—$|^…$)")
    for node in nodes(dump_xml()):
        text = (node.get("text") or "").strip()
        token = text.split(" ")[0]
        if 3 <= len(token) <= 18 and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,17}", token) and not skip.search(token):
            shell(f'input text "{token}"')
            print(f"type: '{token}'")
            STEPS.append(f"type '{token}'")
            return True
    print("type: nothing suitable found")
    STEPS.append("type: skipped (no ASCII server name)")
    return False


def crash_check():
    pid = shell("pidof co.asiven.vixentvpn").stdout.strip()
    crash = adb("logcat", "-d", "-b", "crash").stdout or ""
    fata = [line for line in adb("logcat", "-d").stdout.splitlines() if "FATAL EXCEPTION" in line or "AndroidRuntime: " in line]
    ok = bool(pid) and not crash.strip() and not fata
    print(f"crash-check: pid={'yes' if pid else 'no'} crash_buffer={len(crash)} fatal_lines={len(fata)}")
    STEPS.append(f"crash-check: pid={'yes' if pid else 'no'}, fatal lines={len(fata)}")
    if not pid:
        FAILURES.append("app process is not running")
    if fata:
        FAILURES.append("crash in logcat: " + fata[0][:200])
    return ok


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
        elif cmd == "type-from-list":
            type_from_list(); index += 1
        elif cmd == "wait-text":
            wait_text(rest[index + 1], int(rest[index + 2])); index += 3
        elif cmd == "sleep":
            time.sleep(float(rest[index + 1])); index += 2
        elif cmd == "back":
            shell("input keyevent 4"); time.sleep(1); index += 1
        elif cmd == "swipe-up":
            shell("input swipe 540 1600 540 500 300"); time.sleep(1); index += 1
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

    summary = os.path.join(OUT, "STEPS.txt")
    with open(summary, "w", encoding="utf-8") as handle:
        handle.write("\n".join(STEPS) + "\n")
        handle.write("\nFAILURES:\n" + ("\n".join(FAILURES) if FAILURES else "none") + "\n")
    if FAILURES:
        print("::error title=ui-snapshot::" + " | ".join(FAILURES)[:900])
        return 1
    print("::notice title=ui-snapshot::all steps ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
