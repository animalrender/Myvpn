# REA — Electron/JavaScript demo report

Target: [`examples/electron-demo-app`](../electron-demo-app) — a 5-file Electron app that
exposes a clipboard read over IPC (`main.js` → `ipcMain.handle('clipboard:read')`,
`preload.js` → `contextBridge.exposeInMainWorld('api', …)`, `lib/clipboard.js` → `clipboard.readText()`).

Command (nothing was executed; this is static analysis of the files):

```bash
rea analyze-javascript-application examples/electron-demo-app --json
```

## What REA reported

| Fact | Value |
| --- | --- |
| Evidence id | `ev_0bc9c0360abba4ee3700b1daf7bd514ecd92bb33d21b984da2cc27a7e9744534` |
| Provider | `rea-javascript-application` (no native engine required) |
| Files parsed | 4 JavaScript files, 6 relevant files, 965 text bytes, 0 parse failures |
| Browser windows / preload entrypoints | 1 / 1 |
| `contextBridge` APIs and exposed members | 1 API, 1 member (`api.readClipboard`) |
| IPC operations | 2 (1 literal channel, 1 main-process handler, 1 renderer transmission, 1 pair) |
| Semantic graph | 116 nodes, 54 relations (module, binding, call-site, boundary, promise, …) |
| Coverage | `status: unknown`, families reported `partial` (call-flow, boundary) |

Recovered chain (labels as REA returned them):

```
boundary: api.readClipboard
  → expression: readClipboard            (preload's contextBridge member)
  → call-site: electron.ipcRenderer.invoke
  → [ipc literal channel  clipboard:read]
  → main-process handler  ipcMain.handle('clipboard:read')
  → module: lib/clipboard.js   (readClipboard → clipboard.readText / readHTML)
```

## Limits this run declared

- `unknowns[]` contains an `object-flow` / `ambiguous-target` entry for the
  `ipcRenderer` destructure: the receiver is not a retained container, so object
  identity stays partial instead of being asserted.
- `coverage.status` is `unknown`, with `call-flow` and `boundary` families marked
  `partial`; missing data is not reported as absent behavior.
- Static inspection only: nothing was launched, so runtime-only effects (what the
  renderer actually does with the clipboard text) are not established.

## Why this example matters

This is the exact "understand a feature of a shipped app, then rebuild it" loop:
REA gives the module/boundary/IPC graph plus the residual unknowns, and the agent
uses that to write and test its own implementation. No Hopper/Ghidra/IDA is
involved — JavaScript/Electron analysis is fully built in.
