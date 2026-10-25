# راهنمای کامل REA — نصب، اتصال و استفاده

> این سند برای پروژه‌ی [morluto/rea](https://github.com/morluto/rea) نوشته شده و وضعیت واقعی
> نصب و اتصال آن در همین ورک‌اسپیس را ثبت می‌کند. هر عدد و خروجی‌ای که در این‌جا می‌آید،
> در همین محیط اجرا و تأیید شده است.

---

## ۱. REA چیست؟

**REA = Reverse Engineer Anything.** یک سرور **MCP** (Model Context Protocol) است که ابزارهای
مهندسی معکوس را در اختیار ایجنت هوش مصنوعی یا ترمینال شما می‌گذارد. به‌جای اینکه خودتان
بین Hopper/Ghidra/IDA و ابزارهای خط فرمان سوییچ کنید، ایجنت با ۲۲۹ ابزار آماده از REA
می‌پرسد و پاسخ همراه با **Evidence** (سندِ شواهد قابل بازرسی) برمی‌گردد.

سه ویژگی که آن را از «یک اسکریپت تحلیل» جدا می‌کند:

| ویژگی | معنی عملی |
| --- | --- |
| **MCP-first** | همان ابزارها هم از CLI و هم از داخل ایجنت (Claude Code، Cursor، Codex، Gemini CLI و …) در دسترس‌اند. |
| **Evidence در خروجی** | هر نتیجه `evidence_id`، هش فایل، provider، پارامترها و فهرست `limitations` دارد؛ «نمی‌دانم» با «وجود ندارد» قاطی نمی‌شود. |
| **اجرای محلی** | فایل هدف آپلود نمی‌شود؛ تحلیل روی ماشین خودتان انجام می‌شود. |

دسته‌بندی توانایی‌ها (خلاصه‌ی README پروژه): باینری بومی (ELF/PE/Mach-O)، اپ‌های
JavaScript/Electron، اسمبلی‌های .NET، APK اندروید، فریمور، مدل‌های GGUF/safetensors،
پایگاه‌داده SQLite، فایل‌های pcap، کرش‌های ثبت‌شده، سایت‌ها و رفتار runtime.

---

## ۲. وضعیت نصب در این محیط (تأییدشده)

| مورد | وضعیت |
| --- | --- |
| نسخه‌ی REA | `6.8.0` (پکیج npm: `rea-agents`) |
| Node.js | `v26.12.1` — در مسیر `/usr/local/rea26/bin/node` (نسخه‌ی پیش‌فرض سیستم `22.22.3` بود که REA رد می‌کرد) |
| اجرایی `rea` | `/usr/local/bin/rea` |
| سرور MCP | ✅ سالم — `rea mcp doctor` → `healthy: true`، پروتکل `2025-11-25`، **۲۲۹ ابزار** و **۶ prompt** |
| Skill ایجنت | ✅ نصب در `~/.agents/skills/reverse-engineer-anything` |
| Provider فعال | `pwntools-elf` (pwntools 4.15.0 + pyelftools 0.33 + unicorn 2.1.2) برای `inspect-binary-layout` و کرش‌ها |
| موتور تحلیل بومی | ❌ Ghidra / IDA / Hopper / JADX / Kuna نصب نیستند (دلیل: دانلودشان از GitHub Releases به میزبان‌های مسدود در این سندباکس ریدایرکت می‌شود) |

یعنی: **همه‌ی ابزارهای static داخلی + JavaScript/Electron + .NET + PE/ELF/Mach-O +
SQLite + GGUF + IL2CPP + …** کار می‌کنند؛ ولی `decompile`/`analyze` روی باینری بومی
(که موتور عمیق می‌خواهد) در این سندباکس جواب نمی‌دهد. راه‌حل در بخش ۹ آمده است.

> ⚠️ نکته‌ی مهم درباره‌ی ماندگاری: `/usr/local` بیرون از اسنپ‌شات ورک‌اسپیس است.
> در یک سندباکس تازه، REA از بین می‌رود. راه‌حل: `bash scripts/bootstrap-rea.sh`
> (در بخش ۳). خودِ اسکریپت و همه‌ی فایل‌های این ریپو باقی می‌مانند.

---

## ۳. نصب/بازسازی در سشن جدید (یک دستور)

```bash
bash scripts/bootstrap-rea.sh
```

این اسکریپت idempotent است و به‌ترتیب:

1. اگر Node سازگار نیست، `node-linux-x64@26.12.1` را از **رجیستری npm** می‌گیرد و در
   `/usr/local/rea26/bin/node` می‌نشاند (بدون نیاز به GitHub).
2. `rea-agents@6.8.0` را با `npm install -g --prefix /usr/local/rea26` نصب می‌کند.
3. لانچر `/usr/local/bin/rea` را می‌سازد (همیشه با Node پین‌شده اجرا می‌شود).
4. venv پایتون + `pwntools==4.15.0` را برای provider ال‌اف می‌سازد.
5. skill ایجنت را نصب می‌کند.
6. در پایان `rea --version`، `rea mcp doctor` و یک probe واقعی `inspect-binary-layout` را اجرا می‌کند.

فقط بررسی بدون تغییر:

```bash
bash scripts/bootstrap-rea.sh --check
```

---

## ۴. «وصل شدن به من» چطور انجام شد؟

نکته‌ی فنی: در این محیط نمی‌توان وسط یک گفتگو سرور MCP جدیدی به فهرست ابزارهای ایجنت
اضافه کرد. پس اتصال در دو لایه انجام شد که هر دو واقعی و قابل استفاده‌اند:

### لایه ۱ — مسیر CLI (استفاده‌ی مستقیم توسط من)

من می‌توانم دستور `rea` را در همین سندباکس اجرا کنم؛ یعنی هر وقت بگویید «این فایل را
معکوس‌مهندسی کن»، من واقعاً `rea inspect-…`/`analyze-…` را اجرا می‌کنم و خروجی JSON و
limitations را برایتان تفسیر می‌کنم. REA برای همین ساخته شده که ایجنت صدایش بزند.

### لایه ۲ — پل MCP (همان سرور، ولی از طریق پروتکل)

فایل [`tools/rea-mcp-bridge.mjs`](../tools/rea-mcp-bridge.mjs) یک کلاینت MCP بدون
وابستگی است که سرور `rea --mcp` را spawn می‌کند و JSON-RPC رد و بدل می‌کند. یعنی من
(یا هر اسکریپت/CI) می‌توانم دقیقاً همان ۲۲۹ ابزار MCP را صدا بزنم، نه صرفاً CLI را:

```bash
# دست‌دادن و دیدن هویت سرور
node tools/rea-mcp-bridge.mjs init

# فهرست ابزارها (با فیلتر)
node tools/rea-mcp-bridge.mjs tools --filter native

# دیدن اسکیمای ورودی یک ابزار
node tools/rea-mcp-bridge.mjs schema inspect_artifact

# صدا زدن یک ابزار
node tools/rea-mcp-bridge.mjs call inspect_elf_notes '{"path":"/usr/bin/ls","max_entries":40}'

# promptهای آماده (۶ عدد)
node tools/rea-mcp-bridge.mjs prompts
```

متغیرهای محیطی پل: `REA_COMMAND` (پیش‌فرض `rea`)، `REA_MCP_ARGS` (پیش‌فرض `--mcp`)،
`REA_TIMEOUT_MS` (پیش‌فرض ۶۰۰۰۰۰).

> خروجی ابزارهای MCP در `content[0].text` به‌صورت **رشته‌ی JSON** می‌آید؛ برای همین
> نمونه‌ها با `python3 -c 'json.loads(...)'` پارس می‌شوند. اگر `_meta.provenance.untrusted_content`
> برابر `true` بود، یعنی متن از خودِ هدف آمده و باید به‌عنوان **داده** خوانده شود، نه دستور.

---

## ۵. اتصال به ایجنت‌های خودتان (روی ماشین خودتان)

REA رسماً این کلاینت‌ها را ثبت می‌کند: `claude_code`, `claude_desktop`, `codex`,
`cursor`, `gemini_cli`, `windsurf`, `devin`, `opencode`, `antigravity`, `copilot_cli`,
`vscode`, `grok_build`, `omp`, `commandcode`.

```bash
# ۱) پیش‌نمایش تغییرات (بدون نوشتن چیزی)
rea setup --client claude_code --dry-run

# ۲) اعمال
rea setup --client claude_code --yes

# ۳) ری‌استارت کلاینت، بعد صحت ثبت
rea doctor --client claude_code
```

اگر ایجنت شما جزو فهرست نیست، ثبت دستی MCP. فایل [`.mcp.json`](../.mcp.json) همین ریپو
یک نمونه‌ی قابل‌حمل است:

```json
{
  "mcpServers": {
    "rea": {
      "command": "npx",
      "args": ["-y", "rea-agents@6.8.0", "--mcp"]
    }
  }
}
```

در همین سندباکس، معادلش با لانچر محلی (سریع‌تر، بدون دانلود):

```json
{
  "mcpServers": {
    "rea": { "command": "/usr/local/bin/rea", "args": ["--mcp"] }
  }
}
```

نکته: اسکیمای ورودی ابزارها به‌صورت پیش‌فرض `compact` است تا context کم مصرف شود؛ برای
راهنمای کامل فیلدها `REA_MCP_INPUT_SCHEMA_PROFILE=full` را در ثبت MCP بگذارید.

---

## ۶. استفاده — الگوی کاری درست

REA مثل «grep روی باینری» نیست؛ قراردادش این است:

```
inspect / analyze   →  چه چیزی هست؟ (فهرست، ساختار، هش)
search / xrefs      →  کجا استفاده شده؟
function / decompile→  آن بخش چه کاری می‌کند؟ (نیازمند موتور بومی)
trace               →  یک قابلیت را از UI تا کد دنبال کن
Evidence            →  ادعا + محدودیت‌ها را نگه دار و export کن
```

### ۶.۱ دستورهای پرکاربرد CLI

```bash
rea --version                 # نسخه
rea doctor                    # آمادگی کلی محیط
rea mcp doctor                # سالم بودن سرور MCP و فهرست ۲۲۹ ابزار
rea capabilities              # کدام عملیات/provider روی این میزبان «در دسترس» است
rea providers                 # providerهای پیکربندی‌شده

rea inspect-artifact FILE --json                 # شناسایی کلی یک فایل ناشناس
rea inspect-binary-layout FILE --json            # سکشن/سگمنت/سیمبل/relocation + mitigations
rea inspect-elf-notes FILE --json                # build-id، ABI-tag
rea inspect-go-binary FILE --json                # نسخه‌ی کامپایلر و ماژول‌های Go
rea inspect-rust-binary FILE --json              # crateها از cargo-auditable
rea inspect-pe-imports FILE --json               # واردات PE و ایمپورت‌هش
rea inspect-managed-artifact FILE --json         # هویت .NET بدون اجرا
rea inspect-model-artifact FILE --json           # متادیتای GGUF / safetensors
rea inspect-sqlite-database FILE --json          # اسکیمای SQLite
rea analyze-javascript-application DIR --json    # Electron/JS: ماژول، IPC، boundary
rea inspect-byte-entropy FILE --json             # آنتروپی برای پیدا کردن داده‌ی فشرده/رمز

rea analyze / decompile / function / search / xrefs / trace   # نیازمند موتور بومی
```

همه‌ی دستورها `--json` دارند؛ برای خروجی کوچک‌تر:
`--filter-output foo,bar.baz` یا `--token-limit 2000` یا `--format md`.

### ۶.۲ استفاده از داخل چت با من

کافی است هدف و سؤال را بدهید. مثال‌هایی که در همین محیط قابل انجام است:

- «این APK/برنامه‌ی الکترون را نگاه کن و بگو قابلیت X را چطور پیاده کرده و چه شواهدی داری؟»
- «ساختار این فایل ناشناس را بگو: نوع، معماری، ایمپورت‌ها، آنتروپی، آیا فشرده/پک‌شده است؟»
- «این دیتابیس SQLite را تحلیل کن؛ جدول‌ها و ستون‌ها را دربیاور.»
- «کوچک‌ترین نمونه‌ی بازسازی این قابلیت را برای پروژه‌ی خودم بنویس و با شواهد مقایسه کن.»
- «بین نسخه‌ی ۱ و ۲ این اپ چه تفاوتی هست؟» (`compare-application-versions`)

مثال واقعی از همین ورک‌اسپیس:

```text
با REA اپ examples/electron-demo-app را تحلیل کن:
پل clipboard از renderer تا main را دنبال کن، شواهد را نشان بده،
و بگو چه چیزهایی هنوز نامعلوم مانده‌اند.
```

### ۶.۳ promptهای آماده‌ی MCP

`investigate_feature`، `compare_application_versions`، `verify_reconstruction`،
`trace_crash`، `audit_residual_unknowns`، `prepare_bounded_process_capture`.
این‌ها «دستور کار»های استانداردی هستند که REA به ایجنت می‌دهد تا نتیجه‌گیری‌اش
از شواهد جلو نزند:

```bash
node tools/rea-mcp-bridge.mjs prompt investigate_feature '{"target":"/path/to/app"}'
```

### ۶.۴ محیط RL (AgentEnv)

REA می‌تواند از یک HAR یا جلسه‌ی ضبط‌شده، یک محیط قابل‌اجرا برای ایجنت بسازد:

```bash
rea environment-build ./session.har ./my-env --name my-env --json
agent-env run ./my-env     # نیازمند AgentEnv + Docker
```

---

## ۷. نمونه‌های اجراشده در همین محیط (خروجی واقعی)

اجرای همه با یک دستور: `bash examples/quickstart.sh` (و `--raw` برای نگه‌داشتن JSON خام).

### ۷.۱ Electron/JavaScript — بدون هیچ موتور بومی

هدف: `examples/electron-demo-app` (۵ فایل، clipboard روی IPC).

```
evidence: ev_0bc9c0360abba4ee3700b1daf7bd514ec…
files parsed: 4 | findings: 21 | parse failures: 0
preload entrypoints: 1 | contextBridge APIs: 1 | exposed members: 1
ipc: operations=2, literal_channels=1, main_handlers=1, paired_renderer_transmissions=1
semantic graph: 116 nodes / 54 relations
```

زنجیره‌ای که REA بازسازی کرد: `boundary api.readClipboard` → `readClipboard` در preload →
`ipcRenderer.invoke` → کانال `clipboard:read` → هندلر main → ماژول `lib/clipboard.js` →
`clipboard.readText/readHTML`. گزارش کامل: [`examples/reports/electron-static-analysis.md`](../examples/reports/electron-static-analysis.md).

### ۷.۲ ELF layout با provider pwntools

```bash
rea inspect-binary-layout /bin/true --json
```

```
provider: pwntools-elf | pwntools@4.15.0;pyelftools@0.33;unicorn@2.1.2
sections: 31 | segments: 13 | relocations: 66
plt imports: free, abort, __errno_location, strncmp, _exit, __fpending …
mitigations: PIE=true, NX=true, executable-stack=false, canary=true, RELRO=Partial
```

### ۷.۳ ELF notes (بدون ابزار بیرونی)

```
gnu_build_id -> c89156ebdabf859f4ee70cb0c303004dccf1ae51
gnu_abi_tag  -> linux 3.2.0
```

### ۷.۴ SQLite

```
engine: SQLite 3.54.0 | encoding: UTF-8
table: users  | columns: 3 | root page: 2
table: orders | columns: 3 | root page: 3
```

### ۷.۵ همان سرور از مسیر MCP (نه CLI)

```
tool: inspect_byte_entropy | evidence: ev_85da9f0927fcde436bacf…
file entropy: 5.0249   blocks: 9
```

---

## ۸. Evidence چیست و چرا جدی است؟

هر خروجی یک شیء Evidence با این فیلدهاست: `evidence_id`, `subject` (نام + sha256 +
مسیر), `provider` (id/version), `parameters`, `normalized_result`, `limitations`,
`confidence` (`observed` / `inferred`), `authority`.

- `limitations` می‌گوید این تحلیل **چه چیزی را اثبات نمی‌کند** (مثلاً «نبودِ سیمبل
  ثابت نمی‌کند تابع محافظت‌نشده است»).
- `coverage.status = unknown` یعنی «داده ناقص است»، نه «رفتار وجود ندارد».
- ذخیره و مقایسه:

```bash
rea evidence-export ./raw.json ./canonical.json     # اعتبارسنجی + خروجی کانونیکال
rea compare a.json b.json                           # مقایسه‌ی دو بسته‌ی شواهد
```

اگر می‌خواهید نتیجه‌ای قابل ارجاع بماند، همیشه JSON را نگه دارید؛ خروجی انسانی خلاصه است.

---

## ۹. چه چیزی الان کار می‌کند و چه چیزی نه

| هدف | در این سندباکس | پیش‌نیاز روی ماشین خودتان |
| --- | --- | --- |
| JS/Electron (تحلیل static) | ✅ | فقط Node + npm |
| ELF/PE/Mach-O static (ساختار، ایمپورت، نُت، آنتروپی) | ✅ | هیچ |
| Go / Rust / .NET / IL2CPP / GGUF / Godot PCK / BEAM / WASM* | ✅ (WASM نیاز به WABT) | هیچ |
| SQLite | ✅ | Node 24.15+ یا 26+ |
| ELF layout با pwntools | ✅ | `pip install pwntools==4.15.0` + `REA_PWNTOOLS_PYTHON` |
| **decompile / analyze / function / trace روی باینری بومی** | ❌ | Hopper، Ghidra یا IDA |
| APK اندروید (jadx) | ❌ | JDK + `jadx-headless-mcp`، `REA_JADX_MCP_JAR` |
| وب‌سایت / اسکرین‌شات | ❌ (کروم نصب نیست) | یک مرورگر Chrome-family |
| ADB / دستگاه اندروید | ❌ | `adb` |
| pcap / TShark | ❌ | `tshark` + `capinfos` |
| فریمور | ❌ | `binwalk` یا `unblob` |

### فعال کردن تحلیل بومی (روی ماشین خودتان، ۲ دقیقه)

```bash
# Ghidra 12.1.x را از releases دانلود و اکسترکت کنید، بعد:
export GHIDRA_INSTALL_DIR=/absolute/path/to/ghidra_12.1.4_PUBLIC
export JAVA_HOME=/path/to/jdk-21-or-newer      # Ghidra خودش JDK می‌خواهد
rea doctor --provider ghidra
rea analyze /path/to/binary --json
```

اگر Hopper دارید: `export HOPPER_LAUNCHER_PATH=...`؛ اگر IDA: `REA_IDA_MCP_CONFIG`.
برای باینری‌های بزرگ، مهلت شروع را بالا ببرید:
`REA_GHIDRA_STARTUP_TIMEOUT_MS=600000`.

> در این سندباکس این کار ممکن نشد چون دانلود assetهای GitHub Releases به میزبان‌های
> مسدود ریدایرکت می‌شود. خودِ REA هم (به‌درستی) هیچ موتور تحلیلی را خودش دانلود نمی‌کند.

---

## ۱۰. عیب‌یابی

| نشانه | علت رایج | درمان |
| --- | --- | --- |
| `Unsupported engine` / اجرا نمی‌شود | Node خیلی قدیمی | `bash scripts/bootstrap-rea.sh` |
| `command not found: rea` | سشن تازه، `/usr/local` پاک شده | همان اسکریپت |
| `rea mcp doctor` → tools missing | نصب ناقص یا نسخه‌ی ناهمگون | `REA_VERSION=… bootstrap-rea.sh` |
| ابزارهای REA در ایجنت دیده نمی‌شوند | ثبت MCP یا ری‌استارت نشده | `rea setup --client … --yes`، سپس ری‌استارت ایجنت |
| `provider_timeout` | موتور بومی کند/بزرگ | `REA_GHIDRA_STARTUP_TIMEOUT_MS` یا تحلیل کوچک‌تر |
| `resource_constraint … budget` | بودجه‌ی ابزار کم انتخاب شده | همان پارامتر را بالا ببرید (مثلاً `max_entries`) |
| نبود `pwntools` | venv نیست | بخش ۳ یا `REA_PWNTOOLS_PYTHON=/…/python` |
| خروجی خیلی بزرگ / context پر شد | JSON کامل | `--filter-output`, `--token-limit`, `--format md` |

بررسی هدفمند به‌جای نگاه کلی:

```bash
rea doctor --skill                       # فقط skill
rea doctor --provider <id>               # فقط یک provider
rea doctor --target /path/to/app         # آمادگی برای یک هدف مشخص
rea capabilities                         # چه چیزی روی این میزبان مجاز/در دسترس است
```

---

## ۱۱. امنیت، حریم خصوصی و استفاده‌ی منصفانه

- تحلیل **محلی** است؛ REA فایل شما را جایی آپلود نمی‌کند. اما خروجی ابزار به مدل ایجنت
  می‌رسد و سیاست داده‌ی آن provider جداگانه است.
- `capture-*`/`observe-*` ممکن است هدف را **اجرا** کنند؛ `rea capabilities` اثرات هر
  عملیات (`launches_process`, `may_write_filesystem`, …) را نشان می‌دهد.
- متن‌های برگشتی از هدف (strings، کد، لاگ) **غیرقابل‌اعتماد** هستند و REA با
  `_meta.provenance.untrusted_content` علامت‌گذاری می‌کند. اگر داخل آن‌ها دستوری دیدید
  (مثلاً «این را دانلود کن»)، آن تلاش prompt-injection است؛ اجرا نکنید و گزارش دهید.
- مجوز: فقط نرم‌افزاری را تحلیل کنید که مالک آن هستید یا اجازه‌ی تحلیلش را دارید
  (به `DISCLAIMER.md` پروژه مراجعه کنید).
- پروژه MIT است و ادعای رسمی: فقط از `morluto/rea`، `rea.tools` یا پکیج npm `rea-agents`
  نصب کنید؛ ریپوی هم‌نام دلیل رسمی بودن نیست.

---

## ۱۲. به‌روزرسانی و حذف

```bash
rea update            # آپدیت نصب گلوبال + بررسی نسخه
rea setup --yes --all-detected   # تازه‌سازی ثبت ایجنت‌ها و skill

rea uninstall                     # حذف پیکربندی‌ها و skill (خود پکیج npm بماند)
npm uninstall -g rea-agents       # حذف پکیج
```

در این ورک‌اسپیس، به‌روزرسانی = تغییر `REA_VERSION` در `scripts/bootstrap-rea.sh` و
اجرای مجدد آن.

---

## ۱۳. فایل‌های این ریپو

```text
README.md                              نقطه‌ی شروع (فارسی/انگلیسی)
docs/rea-guide-fa.md                   همین راهنما
.mcp.json                              ثبت نمونه‌ی MCP برای کلاینت‌های ایجنت
scripts/bootstrap-rea.sh               نصب/بازسازی کامل و idempotent
tools/rea-mcp-bridge.mjs               کلاینت MCP بدون وابستگی (init/tools/call/prompt)
examples/quickstart.sh                 ۵ جریان تأییدشده با خروجی خلاصه
examples/electron-demo-app/            اپ نمونه‌ی Electron برای تحلیل
examples/make-demo-sqlite.py           ساخت دیتابیس نمونه
examples/reports/electron-static-analysis.md   گزارش واقعی تحلیل اپ نمونه
```

---

## ۱۴. گام‌های بعدی پیشنهادی

1. **روی ماشین خودتان** Node 24/26 + `npm i -g rea-agents` و `rea setup` را اجرا کنید و
   یک موتور بومی (Ghidra) را وصل کنید تا `decompile`/`trace` هم فعال شود.
2. یک هدف واقعی انتخاب کنید (یک اپ Electron که دوستش دارید، یک باینری محلی) و با
   پرامپت «قابلیت X را با شواهد توضیح بده» شروع کنید.
3. برای کارهای تکراری، خروجی JSON را نگه دارید و با `rea compare` نسخه‌ها را مقایسه کنید.
4. اگر می‌خواهید من همین حالا یک هدف واقعی را تحلیل کنم، فقط مسیر/فایل را در سندباکس
   بگذارید (یا از `registry.npmjs.org` یک پکیج مشخص بدهید تا بیاورم) و بگویید دنبال چه
   قابلیتی هستید.
