#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# bootstrap-rea.sh — rebuild the REA installation used in this workspace.
#
# Why this file exists: REA lives under /usr/local/rea26, and /usr/local is
# OUTSIDE the workspace snapshot. A fresh sandbox starts blank, so run this
# script once at the beginning of a new session to get a working `rea` again.
#
# It is idempotent: every step checks first and skips what already exists.
#
#   bash scripts/bootstrap-rea.sh            # full setup + verification
#   bash scripts/bootstrap-rea.sh --check    # verify only, change nothing
#
# What gets installed
#   1. Node.js 26.12.1 runtime   -> /usr/local/rea26/bin/node   (REA needs >=22.23.4/24.22.1/26.12.1)
#   2. rea-agents (npm, pinned)  -> /usr/local/rea26/lib/node_modules/rea-agents
#   3. launcher                  -> /usr/local/bin/rea
#   4. python venv + pwntools    -> /usr/local/rea26/venv-pwntools (enables inspect-binary-layout, inspect-recorded-crash)
#   5. REA agent skill           -> ~/.agents/skills/reverse-engineer-anything (inside the snapshot, survives)
# ---------------------------------------------------------------------------
set -euo pipefail

REA_HOME="${REA_HOME:-/usr/local/rea26}"
REA_VERSION="${REA_VERSION:-6.8.0}"
NODE_VERSION="${NODE_VERSION:-26.12.1}"
PWNTools_SPEC="${PWNTools_SPEC:-pwntools==4.15.0}"
CHECK_ONLY=0
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=1

log() { printf '\033[1;36m[rea-bootstrap]\033[0m %s\n' "$*"; }
die() { printf '\033[1;31m[rea-bootstrap] error:\033[0m %s\n' "$*" >&2; exit 1; }

# --- 1. Node.js runtime -----------------------------------------------------
need_node=1
if [[ -x "$REA_HOME/bin/node" ]]; then
  have="$("$REA_HOME/bin/node" -v | sed 's/^v//')"
  major="${have%%.*}"
  if (( major >= 26 )) || (( major == 24 )) || (( major == 22 )); then
    case "$have" in
      22.23.*|22.2[4-9].*|24.2[2-9].*|24.[3-9]*|26.1[2-9].*|2[7-9].*|3*) need_node=0 ;;
    esac
  fi
fi

if (( need_node )); then
  if (( CHECK_ONLY )); then
    die "Node.js runtime missing or too old in $REA_HOME (REA needs ^22.23.4 || ^24.22.1 || >=26.12.1)"
  fi
  log "installing Node.js $NODE_VERSION into $REA_HOME"
  workdir="$(mktemp -d)"
  (
    cd "$workdir"
    # Pull the official prebuilt runtime from the npm registry (no GitHub needed).
    npm pack "node-linux-x64@${NODE_VERSION}" >/dev/null
    tar xzf node-linux-x64-*.tgz package/bin/node
    mkdir -p "$REA_HOME/bin"
    install -m 0755 package/bin/node "$REA_HOME/bin/node"
  )
  rm -rf "$workdir"
else
  log "Node.js runtime already present: $("$REA_HOME/bin/node" -v)"
fi

# npm/npx shims that always use the pinned runtime
if (( ! CHECK_ONLY )); then
  NPM_CLI="$(npm root -g 2>/dev/null | xargs -r dirname)/npm/bin/npm-cli.js"
  [[ -f "$NPM_CLI" ]] || NPM_CLI="/usr/local/lib/node_modules/npm/bin/npm-cli.js"
  cat > "$REA_HOME/bin/npm" <<EOF
#!/bin/sh
exec "$REA_HOME/bin/node" "$NPM_CLI" "\$@"
EOF
  cat > "$REA_HOME/bin/npx" <<EOF
#!/bin/sh
exec "$REA_HOME/bin/node" "${NPM_CLI%npm-cli.js}npx-cli.js" "\$@"
EOF
  chmod +x "$REA_HOME/bin/npm" "$REA_HOME/bin/npx"
fi

# --- 2. rea-agents package --------------------------------------------------
if [[ -f "$REA_HOME/lib/node_modules/rea-agents/package.json" ]]; then
  installed="$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$REA_HOME/lib/node_modules/rea-agents/package.json" | head -1)"
else
  installed=""
fi

if [[ "$installed" != "$REA_VERSION" ]]; then
  if (( CHECK_ONLY )); then
    die "rea-agents@$REA_VERSION not installed (found: ${installed:-none})"
  fi
  log "installing rea-agents@$REA_VERSION"
  PATH="$REA_HOME/bin:$PATH" "$REA_HOME/bin/npm" install --global --prefix "$REA_HOME" \
    "rea-agents@$REA_VERSION" >/dev/null
else
  log "rea-agents@$installed already installed"
fi

# --- 3. launcher ------------------------------------------------------------
if (( ! CHECK_ONLY )); then
  cat > /usr/local/bin/rea <<EOF
#!/bin/sh
# REA launcher (pinned Node.js runtime + optional providers).
# Recreated by Myvpn/scripts/bootstrap-rea.sh.
REA_HOME=$REA_HOME
if [ -x "\$REA_HOME/venv-pwntools/bin/python" ]; then
  export REA_PWNTOOLS_PYTHON="\$REA_HOME/venv-pwntools/bin/python"
fi
PATH="\$REA_HOME/bin:\$PATH"; export PATH
exec "\$REA_HOME/bin/node" "\$REA_HOME/lib/node_modules/rea-agents/scripts/rea.mjs" "\$@"
EOF
  chmod +x /usr/local/bin/rea
fi

# --- 4. pwntools provider (optional, ELF layout / crash records) ------------
if [[ -x "$REA_HOME/venv-pwntools/bin/python" ]] && \
   "$REA_HOME/venv-pwntools/bin/python" -c 'import pwn' >/dev/null 2>&1; then
  log "pwntools provider already present"
elif (( CHECK_ONLY )); then
  log "warning: pwntools provider missing (optional)"
else
  log "creating python venv with $PWNTools_SPEC"
  python3 -m venv "$REA_HOME/venv-pwntools" >/dev/null 2>&1 || true
  TERM=xterm "$REA_HOME/venv-pwntools/bin/pip" install -q --upgrade pip >/dev/null 2>&1 || true
  TERM=xterm "$REA_HOME/venv-pwntools/bin/pip" install -q "$PWNTools_SPEC" >/dev/null 2>&1 \
    || log "warning: pwntools install failed; ELF-layout tools stay unavailable"
fi

# --- 5. agent skill ---------------------------------------------------------
if (( ! CHECK_ONLY )); then
  log "installing REA agent skill (~/.agents/skills)"
  rea setup --yes --all-detected >/dev/null 2>&1 || log "warning: skill install reported an issue"
fi

# --- verification -----------------------------------------------------------
log "verifying"
rea --version
rea mcp doctor 2>/dev/null | sed -n '1,6p'
log "doctor (scoped: skill installed)"
rea doctor --skill 2>/dev/null | sed -n '1,3p' || true
log "note: audit-wide 'rea doctor' stays unhealthy until a native engine
      (Ghidra/Hopper/IDA/JADX) is configured — see docs/rea-guide-fa.md section 9"
if [[ -x "$REA_HOME/venv-pwntools/bin/python" ]]; then
  rea inspect-binary-layout /bin/true --json 2>/dev/null \
    | python3 -c 'import json,sys; d=json.load(sys.stdin); print("pwntools provider:", d["provider"]["id"])' \
    || log "warning: binary-layout probe failed"
fi
log "done"
