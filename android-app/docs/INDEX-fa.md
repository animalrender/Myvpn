# نقشهٔ مستندات (MVPN Trial)

این فایل «فهرست راهنما»ی همهٔ مستندات این مخزن است: هر سند چه چیزی را توضیح می‌دهد، برای چه
کسی نوشته شده و شاهد/خروجی‌اش کجاست. اگر دنبال یک نکتهٔ خاص هستید، از همین‌جا شروع کنید.

> وضعیت فعلی: آخرین ریلیز تأییدشده **[trial-51](https://github.com/animalrender/Myvpn/releases/tag/trial-51)**
> (`mvpn-trial-arm64-51.apk` + `mvpn-trial-x86_64-51.apk`)، آخرین آزمون سرتاسری سبز روی بک‌اند واقعی
> **run 42** (کامیت `3b3df66`) — گزارش در [`e2e-real/CONNECT-REAL.md`](e2e-real/CONNECT-REAL.md).

---

## ۱) اگر کاربر/تست‌کننده هستید

| سند | چه چیزی می‌گوید |
| --- | --- |
| [`README-fa.md`](README-fa.md) | معرفی کامل، قابلیت‌ها، قرارداد بک‌اند، ساخت، عیب‌یابی، Firebase، پرسش‌های متداول |
| [`install-fa.md`](install-fa.md) | نصب قدم‌به‌قدم روی گوشی و شبیه‌ساز، نصب کنار اپ اصلی، مجوزها، به‌روزرسانی و حذف |
| [`troubleshooting-fa.md`](troubleshooting-fa.md) | همهٔ خطاهای واقعیِ دیده‌شده + معنا + راه‌حل (بر اساس لاگ‌های همین پروژه) |
| [`security-privacy-fa.md`](security-privacy-fa.md) | چه داده‌ای رد و بدل می‌شود، مجوزها، لاگ‌ها، مجوزهای نرم‌افزاری (GPL/MPL) — فهرست کامل: [`../THIRD-PARTY-NOTICES.md`](../THIRD-PARTY-NOTICES.md) |
| [`changelog-fa.md`](changelog-fa.md) | تاریخچهٔ تغییرات از تحلیل APK تا نسخهٔ فعلی |

## ۲) اگر توسعه‌دهنده هستید

| سند | چه چیزی می‌گوید |
| --- | --- |
| [`architecture-fa.md`](architecture-fa.md) | معماری، چرا `libv2ray` و `hev-socks5-tunnel`، جریان کانفیگ، نقشهٔ کلاس‌ها |
| [`build-fa.md`](build-fa.md) | پیش‌نیازها، ساخت محلی و در CI، ورک‌فلوها و تریگرهایشان، نسخه‌گذاری |
| [`api-contract-fa.md`](api-contract-fa.md) | قرارداد کامل API: هدرها، اندپوینت‌ها، شکل پاسخ، خطاهای منطقی |
| [`value-decrypt-fa.md`](value-decrypt-fa.md) | قاعدهٔ باز کردن `value` (AES/CBC با کلید `key_<id>`) و شواهد ۱۰۵/۱۰۵ |
| [`verification-fa.md`](verification-fa.md) | همهٔ آزمون‌های خودکار، نتیجهٔ آخرین اجرا، نحوهٔ بازتولید |

## ۳) اگر می‌خواهید بدانید «چرا این‌طور شد»

| سند | چه چیزی می‌گوید |
| --- | --- |
| [`docs/apk-vixentvpn-analysis-fa.md`](../../docs/apk-vixentvpn-analysis-fa.md) | تحلیل کامل APK اصلی: مجوزها، کلاس‌ها، تبلیغات، مدل الماس، بک‌اند |
| [`re-analysis-fa.md`](re-analysis-fa.md) | بازآزمایی `base.apk` و جدول تفاوت‌ها با نسخهٔ آزمایشی |
| [`docs/rea-guide-fa.md`](../../docs/rea-guide-fa.md) | راهنمای ابزار REA که برای تحلیل APK استفاده شد |
| [`probe-rows/`](probe-rows/) | شواهد خام بک‌اند: پاسخ‌های زنده، پوشش رمزگشایی، گزارش قیمت |
| [`e2e-real/`](e2e-real/) | گزارش و تصاویر آزمون «صفر ورودی» روی بک‌اند واقعی |
| [`connect-test/`](connect-test/) | گزارش آزمون پشتهٔ تونل روی سرور محلی Xray |
| [`screenshots/`](screenshots/) | تصاویر واقعی رابط کاربری + `STEPS.txt` هر اجرا |

## ۴) پوشه‌های شاهد (خروجی خودکار CI)

| مسیر | تولیدکننده | محتوا |
| --- | --- | --- |
| `e2e-real/CONNECT-REAL.md` + PNG + `logcat*.txt` | `e2e-real.yml` | سناریوی واقعی کاربر: دریافت، پینگ، اتصال، ترافیک، تغییر سرور، قطع |
| `connect-test/CONNECT.md` + PNG + `xray-access.txt` | `connect-test.yml` | اثبات عبور بایت‌ها از تونل با لاگ سرور Xray محلی |
| `screenshots/` | `ui-snapshot.yml` | تصاویر رابط کاربری و متن هر مرحله |
| `probe-rows/` | `probe-rows.yml` / `probe-api.yml` | پاسخ خام بک‌اند، توزیع قیمت، جدول رمزگشایی |
| `native-map.json` | `tools/dcc-native-map.py` | نقشهٔ ۱۵ کلاس / ۲۵۸ متد کد بومی APK اصلی |

## ۵) قواعد این پروژه (خلاصهٔ یک‌خطی)

1. اپ **از کاربر هیچ کانفیگ/لینک/کلیدی نمی‌خواهد**؛ فهرست و `value` را خودش می‌گیرد و باز می‌کند.
2. همان بک‌اند، همان هدرها، همان امضا، همان هستهٔ Xray — بدون تبلیغ، بدون حساب، بدون قفل قیمت.
3. «متصل» فقط وقتی نمایش داده می‌شود که یک درخواست واقعی از تونل عبور کرده باشد.
4. هر تغییر باید با اجرای واقعی روی شبیه‌ساز (نه فقط اسکرین‌شات) تأیید شود.
5. نسخهٔ APK فقط از طریق `build-apks` و به‌صورت GitHub Release تحویل می‌شود.

## ۶) نگه‌داری این مستندات

- هر تغییر رفتاری در کد ⇒ یک خط در [`changelog-fa.md`](changelog-fa.md).
- هر یافتهٔ جدید از بک‌اند ⇒ خروجی خام در `probe-rows/` + به‌روزرسانی [`api-contract-fa.md`](api-contract-fa.md).
- هر آزمون سبز/سرخ ⇒ گزارش CI خودش در `e2e-real/` یا `connect-test/` کامیت می‌شود؛ شمارهٔ اجرا را در
  [`verification-fa.md`](verification-fa.md) ثبت کنید.
- شمارهٔ ریلیز در سه جا هم‌زمان به‌روز می‌شود: `README-fa.md` (پرسش متداول «نسخهٔ فعلی»)،
  [`changelog-fa.md`](changelog-fa.md) و متن PR (`pr-body-fa.md`).
