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

## MVPN Trial — کلاینت آزمایشی اندروید

پوشهٔ [`android-app/`](android-app/) یک اپ اندروید کامل است که همان بک‌اند، همان هدرها،
همان امضا و همان هستهٔ Xray/hev اپ تحلیل‌شده را بازتولید می‌کند، اما **بدون تبلیغ، بدون
حساب کاربری و بدون قفل قیمت**.

**آخرین ریلیز: [trial-51](https://github.com/animalrender/Myvpn/releases/tag/trial-51)** —
`mvpn-trial-arm64-51.apk` (گوشی، `arm64-v8a`) و `mvpn-trial-x86_64-51.apk` (شبیه‌ساز/کروم‌بوک)
به‌همراه فایل‌های `.sha256`. با `applicationId = co.asiven.vixentvpn.trial` **کنار اپ اصلی**
نصب می‌شود.

```bash
gh release download trial-51
sha256sum -c mvpn-trial-arm64-51.apk.sha256
adb install -r mvpn-trial-arm64-51.apk
```

### قابلیت‌ها (خلاصه)

- **صفر ورودی از کاربر**: فهرست ۱۰۵ سرور خودکار از بک‌اند، باز کردن `value` روی خود دستگاه
  (`AES/CBC` با کلید `key_<id>`)، پینگ همه، انتخاب خودکار سریع‌ترین و اتصال با یک لمس.
- **همهٔ سرورها، رایگان و پولی، بدون قفل**؛ هر ردیف با برچسب نوع/پروتکل، قیمت، مصرف، پرچم و `id`.
- **کپی همهٔ لینک‌های v2ray** در سه گروه: همه / پینگ‌داده‌ها / بی‌پینگ‌ها (آمادهٔ Import در v2rayNG).
- **مرتب‌سازی** بر اساس الفبا، پینگ، قیمت یا شناسه — صعودی و نزولی.
- **«متصل» فقط با ترافیک واقعی**: اگر سروری پاسخ ندهد، تونل بسته و پیام صریح داده می‌شود.
- **دو حالت اتصال**: `VPN` (TUN سراسری) و `PROXY` (SOCKS 10808 / HTTP 10809).

### مستندات

| سند | محتوا |
| --- | --- |
| [`android-app/docs/INDEX-fa.md`](android-app/docs/INDEX-fa.md) | نقشهٔ همهٔ مستندات و شاهدهای آزمون |
| [`android-app/docs/README-fa.md`](android-app/docs/README-fa.md) | معرفی کامل، قابلیت‌ها، قرارداد بک‌اند، پرسش‌های متداول |
| [`android-app/docs/install-fa.md`](android-app/docs/install-fa.md) | نصب، مجوزها، به‌روزرسانی، چک‌لیست تست |
| [`android-app/docs/troubleshooting-fa.md`](android-app/docs/troubleshooting-fa.md) | خطاهای واقعی و راه‌حلشان |
| [`android-app/docs/security-privacy-fa.md`](android-app/docs/security-privacy-fa.md) | داده‌های ارسالی، مجوزها، مدل اعتماد، مجوزهای نرم‌افزاری |
| [`android-app/docs/build-fa.md`](android-app/docs/build-fa.md) | ساخت محلی و CI، نسخه‌گذاری، انتشار |
| [`android-app/docs/verification-fa.md`](android-app/docs/verification-fa.md) | شواهد آزمون‌ها و نحوهٔ بازتولید |
| [`android-app/docs/changelog-fa.md`](android-app/docs/changelog-fa.md) | تاریخچهٔ تغییرات |
| [`android-app/docs/architecture-fa.md`](android-app/docs/architecture-fa.md) | معماری و نقشهٔ کد |
| [`android-app/docs/api-contract-fa.md`](android-app/docs/api-contract-fa.md) | قرارداد کامل API و هدرها |
| [`android-app/docs/value-decrypt-fa.md`](android-app/docs/value-decrypt-fa.md) | قاعدهٔ باز کردن `value` (۱۰۵/۱۰۵) |
| [`docs/apk-vixentvpn-analysis-fa.md`](docs/apk-vixentvpn-analysis-fa.md) | تحلیل کامل APK اصلی |

### مجوزها

اجزای شخص ثالث (Xray/libv2ray، hev-socks5-tunnel، AndroidX، Firebase) در
[`android-app/THIRD-PARTY-NOTICES.md`](android-app/THIRD-PARTY-NOTICES.md) با نسخه، مجوز و منبع
فهرست شده‌اند. `libv2ray` و `hev-socks5-tunnel` هر دو GPL-3.0 هستند؛ برای توزیع عمومی APK این
شرایط باید رعایت شود.

### تأیید خودکار

| ورک‌فلو | چه چیزی را ثابت می‌کند |
| --- | --- |
| `build-apks` | ساخت هر دو معماری با امضای AOSP، بررسی `.so`ها، `package`/`versionCode`، انتشار ریلیز |
| `e2e-real` | سناریوی کامل روی بک‌اند واقعی: دریافت → پینگ → اتصال → ترافیک → تغییر سرور → قطع |
| `connect-test` | عبور واقعی بایت‌ها از تونل با ردِ لاگ سرور Xray محلی |
| `ui-snapshot` | اجرای رابط کاربری روی شبیه‌ساز و ثبت تصاویر |

گزارش آخرین اجرای سبز: [`android-app/docs/e2e-real/CONNECT-REAL.md`](android-app/docs/e2e-real/CONNECT-REAL.md).

**وضعیت در این محیط:** REA `6.8.0` روی Node `26.12.1` · MCP سالم (`2025-11-25`, 229 tools, 6 prompts) ·
provider فعال `pwntools-elf` · بدون Ghidra/IDA/Hopper/JADX (تحلیل بومی عمیق در این سندباکس غیرفعال است —
دلیل و راه‌حل در بخش ۹ راهنما).

> `/usr/local` بیرون از اسنپ‌شات است؛ در سشن تازه یک‌بار `scripts/bootstrap-rea.sh` را اجرا کنید.
