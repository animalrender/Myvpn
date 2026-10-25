#!/usr/bin/env node
/**
 * REA MCP bridge — a dependency-free stdio MCP client for the REA server.
 *
 * Why this exists: an agent can only use MCP tools its host has registered.
 * REA ships an MCP server (`rea --mcp`); this bridge lets anything that has a
 * shell (CI jobs, scripts, or an agent using bash) drive the very same server
 * over MCP JSON-RPC instead of the REA CLI. Same tools, same Evidence.
 *
 * Usage:
 *   node tools/rea-mcp-bridge.mjs init                      # handshake + server info
 *   node tools/rea-mcp-bridge.mjs tools                     # list tool names
 *   node tools/rea-mcp-bridge.mjs tools --filter native     # filtered list
 *   node tools/rea-mcp-bridge.mjs prompts                   # list prompts
 *   node tools/rea-mcp-bridge.mjs schema <tool>             # input schema of one tool
 *   node tools/rea-mcp-bridge.mjs call <tool> '<json args>'  # call a tool
 *   node tools/rea-mcp-bridge.mjs prompt <name> '<json args>' # get a prompt
 *
 * Env:
 *   REA_COMMAND    launcher to spawn (default: "rea")     e.g. "/usr/local/bin/rea"
 *   REA_MCP_ARGS   extra server args (default: "--mcp")
 *   REA_TIMEOUT_MS per-request timeout (default: 600000)
 */
import { spawn } from "node:child_process";

const TIMEOUT_MS = Number(process.env.REA_TIMEOUT_MS ?? 600000);
const COMMAND = process.env.REA_COMMAND ?? "rea";
const SERVER_ARGS = (process.env.REA_MCP_ARGS ?? "--mcp").split(" ").filter(Boolean);
const PROTOCOL_VERSION = "2025-11-25";

class McpStdioClient {
  constructor({ command, args }) {
    this.nextId = 1;
    this.pending = new Map();
    this.stderr = "";
    this.child = spawn(command, args, { stdio: ["pipe", "pipe", "pipe"] });
    this.child.stdout.setEncoding("utf8");
    this.child.stderr.setEncoding("utf8");
    let buffer = "";
    this.child.stdout.on("data", (chunk) => {
      buffer += chunk;
      let newline;
      while ((newline = buffer.indexOf("\n")) !== -1) {
        const line = buffer.slice(0, newline).trim();
        buffer = buffer.slice(newline + 1);
        if (line) this.#onLine(line);
      }
    });
    this.child.stderr.on("data", (chunk) => {
      this.stderr = (this.stderr + chunk).slice(-8000);
    });
    this.child.on("error", (error) => {
      for (const { reject } of this.pending.values()) reject(error);
      this.pending.clear();
    });
    this.child.on("exit", (code, signal) => {
      const error = new Error(
        `REA MCP server exited (code=${code}, signal=${signal})\n${this.stderr}`,
      );
      for (const { reject } of this.pending.values()) reject(error);
      this.pending.clear();
    });
  }

  #onLine(line) {
    let message;
    try {
      message = JSON.parse(line);
    } catch {
      return; // non-JSON diagnostics on stdout are ignored
    }
    if (message.id === undefined || message.id === null) return; // notification
    const entry = this.pending.get(message.id);
    if (!entry) return;
    this.pending.delete(message.id);
    clearTimeout(entry.timer);
    if (message.error) {
      entry.reject(new Error(`${message.error.code}: ${message.error.message}`));
    } else {
      entry.resolve(message.result);
    }
  }

  request(method, params = {}, timeoutMs = TIMEOUT_MS) {
    const id = this.nextId++;
    const payload = JSON.stringify({ jsonrpc: "2.0", id, method, params });
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`timeout after ${timeoutMs}ms: ${method}`));
      }, timeoutMs);
      this.pending.set(id, { resolve, reject, timer });
      this.child.stdin.write(payload + "\n");
    });
  }

  notify(method, params = {}) {
    this.child.stdin.write(JSON.stringify({ jsonrpc: "2.0", method, params }) + "\n");
  }

  async initialize() {
    const result = await this.request("initialize", {
      protocolVersion: PROTOCOL_VERSION,
      capabilities: { tools: {}, prompts: {} },
      clientInfo: { name: "rea-mcp-bridge", version: "1.0.0" },
    });
    this.notify("notifications/initialized");
    return result;
  }

  close() {
    this.child.stdin.end();
    this.child.kill("SIGTERM");
  }
}

function parseJsonArg(raw, fallback = {}) {
  if (raw === undefined) return fallback;
  if (raw === "-") {
    return JSON.parse(requireStdin());
  }
  try {
    return JSON.parse(raw);
  } catch {
    throw new Error(`arguments must be JSON, received: ${raw.slice(0, 200)}`);
  }
}

function requireStdin() {
  throw new Error('stdin ("-") is not supported in this build; pass inline JSON instead');
}

async function main(argv) {
  const [command, ...rest] = argv;
  if (!command || command === "--help" || command === "-h") {
    console.log(
      [
        "tools/rea-mcp-bridge.mjs — stdio MCP client for the REA server",
        "",
        "  init                        handshake and print server info",
        "  tools [--filter <text>]     list tools (name + title)",
        "  prompts                     list prompts",
        "  schema <tool>               print one tool's input schema",
        "  call <tool> [json-args]     call a tool",
        "  prompt <name> [json-args]   resolve a prompt",
        "",
        'Env: REA_COMMAND (default "rea"), REA_MCP_ARGS (default "--mcp"), REA_TIMEOUT_MS',
      ].join("\n"),
    );
    return 0;
  }

  const client = new McpStdioClient({ command: COMMAND, args: SERVER_ARGS });
  try {
    const info = await client.initialize();

    if (command === "init") {
      console.log(JSON.stringify(info, null, 2));
    } else if (command === "tools") {
      const filterIndex = rest.indexOf("--filter");
      const filter = filterIndex === -1 ? null : rest[filterIndex + 1]?.toLowerCase();
      const { tools } = await client.request("tools/list");
      const rows = (tools ?? [])
        .filter((tool) => !filter || `${tool.name} ${tool.title ?? ""}`.toLowerCase().includes(filter))
        .map((tool) => ({ name: tool.name, title: tool.title ?? "" }));
      if (process.env.REA_BRIDGE_JSON) {
        console.log(JSON.stringify({ count: rows.length, tools: rows }, null, 2));
      } else {
        console.error(`# ${rows.length} tool(s)`);
        for (const row of rows) console.log(`${row.name}\t${row.title}`);
      }
    } else if (command === "prompts") {
      const { prompts } = await client.request("prompts/list");
      for (const prompt of prompts ?? []) {
        console.log(`${prompt.name}\t${prompt.title ?? ""}\t${prompt.description ?? ""}`);
      }
    } else if (command === "schema") {
      const name = rest[0];
      const { tools } = await client.request("tools/list");
      const tool = (tools ?? []).find((item) => item.name === name);
      if (!tool) throw new Error(`unknown tool: ${name}`);
      console.log(JSON.stringify(tool, null, 2));
    } else if (command === "call") {
      const [name, rawArgs] = rest;
      if (!name) throw new Error("call requires a tool name");
      const args = parseJsonArg(rawArgs);
      const result = await client.request("tools/call", { name, arguments: args });
      console.log(JSON.stringify(result, null, 2));
    } else if (command === "prompt") {
      const [name, rawArgs] = rest;
      const args = parseJsonArg(rawArgs);
      const result = await client.request("prompts/get", { name, arguments: args });
      console.log(JSON.stringify(result, null, 2));
    } else {
      throw new Error(`unknown command: ${command}`);
    }
    return 0;
  } finally {
    client.close();
  }
}

main(process.argv.slice(2))
  .then((code) => process.exit(code))
  .catch((error) => {
    console.error(`rea-mcp-bridge: ${error.message}`);
    process.exit(1);
  });
