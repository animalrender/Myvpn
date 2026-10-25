#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# quickstart.sh — four verified REA flows, condensed output.
#
#   bash examples/quickstart.sh              # print summaries
#   bash examples/quickstart.sh --raw        # also keep the raw JSON in examples/output/
#
# No analysis engine (Hopper/Ghidra/IDA/JADX) is needed for any of these.
# ---------------------------------------------------------------------------
set -euo pipefail

cd "$(dirname "$0")/.."
RAW=0
[[ "${1:-}" == "--raw" ]] && RAW=1
OUT=examples/output
[[ $RAW == 1 ]] && mkdir -p "$OUT"

command -v rea >/dev/null || { echo "rea not found — run: bash scripts/bootstrap-rea.sh"; exit 1; }

say() { printf '\n\033[1;35m== %s\033[0m\n' "$*"; }

say "0. version + MCP server health"
rea --version
rea mcp doctor 2>/dev/null | sed -n '1,3p;/inventory:/,/server-identity/p' | sed -n '1,8p'

say "1. static JavaScript / Electron (demo app in this repo)"
js="$(rea analyze-javascript-application examples/electron-demo-app --json 2>/dev/null)"
[[ $RAW == 1 ]] && printf '%s' "$js" > "$OUT/electron.json"
printf '%s' "$js" | python3 -c '
import json,sys
d=json.load(sys.stdin); s=d["normalized_result"]["summary"]; st=d["normalized_result"]["statistics"]
print("evidence:", d["evidence_id"][:24] + "...")
print("files parsed:", st["parsed_javascript_files"], "| findings:", st["findings"], "| parse failures:", st["parse_failures"])
print("preload entrypoints:", s["preload_entrypoints"], "| contextBridge APIs:", s["context_bridge_apis"], "| exposed members:", s["exposed_api_members"])
print("ipc:", s["ipc"])
'

say "2. offline ELF layout with the pwntools provider"
elf="$(rea inspect-binary-layout /bin/true --json 2>/dev/null)"
[[ $RAW == 1 ]] && printf '%s' "$elf" > "$OUT/true-layout.json"
printf '%s' "$elf" | python3 -c '
import json,sys
d=json.load(sys.stdin); n=d["normalized_result"]
print("provider:", d["provider"]["id"], "|", d["provider"]["version"])
print("sections:", len(n["sections"]), "| segments:", len(n.get("segments") or []), "| relocations:", len(n.get("relocations") or []))
link=n.get("linkage") or {}
print("plt imports:", [p["display_name"] for p in (link.get("plt") or [])][:6])
print("mitigations:", n["mitigations"])
'

say "3. ELF notes (build-id, ABI tag) with zero external tools"
notes="$(rea inspect-elf-notes /bin/true --json 2>/dev/null)"
[[ $RAW == 1 ]] && printf '%s' "$notes" > "$OUT/true-notes.json"
printf '%s' "$notes" | python3 -c '
import json,sys
d=json.load(sys.stdin); n=d["normalized_result"]
print("artifact:", n["artifact"]["path"], n["artifact"]["sha256"][:16] + "...")
seen=set()
for e in n["entries"]:
    if e["type_name"] in ("gnu_build_id","gnu_abi_tag") and e["type_name"] not in seen:
        seen.add(e["type_name"])
        print(e["type_name"], "->", (e["gnu"]["build_id_hex"] or e["gnu"]["abi_tag"]))
'

say "4. SQLite schema inspection"
db="$(python3 examples/make-demo-sqlite.py)"
sql="$(rea inspect-sqlite-database "$db" --json 2>/dev/null)"
[[ $RAW == 1 ]] && printf '%s' "$sql" > "$OUT/demo-db.json"
printf '%s' "$sql" | python3 -c '
import json,sys
d=json.load(sys.stdin); n=d["normalized_result"]
print("engine:", n["engine"]["name"], n["engine"]["version"], "| encoding:", n["database_encoding"])
for t in n["schema"]["tables"]:
    print("table:", t["name"], "| columns:", t["column_count"], "| root page:", t["root_page"])
'

say "5. the same server over MCP (JSON-RPC), via the repository bridge"
node tools/rea-mcp-bridge.mjs call inspect_byte_entropy '{"path":"/bin/true","block_size":4096}' 2>/dev/null \
  | python3 -c '
import json,sys
d=json.load(sys.stdin); body=json.loads(d["content"][0]["text"]); n=body["normalized_result"]
print("tool: inspect_byte_entropy | evidence:", body["evidence_id"][:24] + "...")
print("file entropy:", n["file"]["entropy"] if isinstance(n.get("file"),dict) else n.get("file_entropy"))
print("blocks:", len(n.get("blocks") or []))
'

say "done"
[[ $RAW == 1 ]] && echo "raw JSON written to $OUT/"
