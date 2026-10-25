# Myvpn · REA toolkit

نصب، اتصال و راهنمای استفاده‌ی [REA — Reverse Engineer Anything](https://github.com/morluto/rea)
در این ورک‌اسپیس. / A working REA setup plus a dependency-free MCP bridge, ready to use.

**شروع سریع / Quick start**

```bash
bash scripts/bootstrap-rea.sh     # نصب/بازسازی REA در سشن تازه (idempotent)
bash examples/quickstart.sh       # ۵ جریان تأییدشده با خروجی خلاصه
rea mcp doctor                    # سالم بودن سرور MCP (۲۲۹ ابزار)
node tools/rea-mcp-bridge.mjs tools   # فهرست ابزارهای MCP
```

**راهنمای کامل (فارسی):** [`docs/rea-guide-fa.md`](docs/rea-guide-fa.md)

| مسیر | توضیح |
| --- | --- |
| `docs/rea-guide-fa.md` | راهنمای کامل: نصب، اتصال به ایجنت، استفاده، Evidence، محدودیت‌ها، عیب‌یابی |
| `scripts/bootstrap-rea.sh` | نصب Node 26 + `rea-agents@6.8.0` + pwntools + skill، با بررسی پایانی |
| `tools/rea-mcp-bridge.mjs` | کلاینت MCP بدون وابستگی (JSON-RPC روی stdio) برای صدا زدن ۲۲۹ ابزار REA |
| `.mcp.json` | ثبت نمونه‌ی سرور MCP برای Claude Code / Cursor / VS Code و … |
| `examples/quickstart.sh` | جریان‌های تأییدشده: JS/Electron، ELF layout، ELF notes، SQLite، MCP |
| `examples/reports/` | گزارش واقعی تحلیل اپ نمونه‌ی Electron |

**وضعیت در این محیط:** REA `6.8.0` روی Node `26.12.1` · MCP سالم (`2025-11-25`, 229 tools, 6 prompts) ·
provider فعال `pwntools-elf` · بدون Ghidra/IDA/Hopper/JADX (تحلیل بومی عمیق در این سندباکس غیرفعال است —
دلیل و راه‌حل در بخش ۹ راهنما).

> `/usr/local` بیرون از اسنپ‌شات است؛ در سشن تازه یک‌بار `scripts/bootstrap-rea.sh` را اجرا کنید.
