# ساخت، توسعه و انتشار

این سند همهٔ چیزی است که برای ساختن/تغییر دادن این اپ لازم است: پیش‌نیازها، اسکریپت‌های CI،
ورک‌فلوها، نسخه‌گذاری و انتشار. برای معماری کد به [`architecture-fa.md`](architecture-fa.md)
و برای قرارداد بک‌اند به [`api-contract-fa.md`](api-contract-fa.md) مراجعه کنید.

---

## ۱) پیش‌نیازها

| ابزار | نسخه | چرا |
| --- | --- | --- |
| JDK | ۱۷ | `compileOptions`/`jvmTarget = 17` |
| Android SDK | Platform 35 + Build-Tools 35 | `compileSdk 35`، `targetSdk 35` |
| Android NDK | 26.x/27.x با `ndk-build` | ساخت `libhev-socks5-tunnel.so` |
| Gradle | ۸٫۹ (در CI نصب می‌شود) | AGP 8.7.3 / Kotlin 2.0.21 |
| Python | ۳٫۱۱+ | ابزارهای `tools/*.py` (ادب/پروب/درایور آزمون) |
| `apksigner`/`aapt2` | همراه Build-Tools | بررسی خروجی APK |

هیچ کلید امضایی داخل مخزن نیست. `android-app/signing/` و `app/libs/*.aar` و `jniLibs/` در
`.gitignore` هستند و در CI ساخته می‌شوند.

---

## ۲) ساخت محلی

```bash
cd android-app

# ۱) هستهٔ Xray (AAR از AndroidLibXrayLite، نسخهٔ پین‌شده v26.6.27)
bash tools/fetch-libv2ray.sh

# ۲) tun2socks از سورس (hev-socks5-tunnel 2.19.3) با نام پکیج/کلاس همین اپ
bash tools/build-hevtun.sh 2.19.3

# ۳) کلید امضا (AOSP testkey → signing/keystore.p12، همان گواهی اپ اصلی)
bash tools/fetch-testkey.sh

# ۴) ساخت
gradle assembleRelease                 # arm64-v8a
gradle assembleRelease -PtargetAbi=x86_64   # برای شبیه‌ساز
# خروجی: app/build/outputs/apk/release/app-release.apk
```

بررسی خروجی (همان چیزی که CI هم می‌سنجد):

```bash
APK=app/build/outputs/apk/release/app-release.apk
unzip -l "$APK" | grep -E "lib/(arm64-v8a|x86_64)/lib(gojni|hev-socks5-tunnel)\.so"
aapt2 dump badging "$APK" | head -3        # package=co.asiven.vixentvpn.trial، versionCode=1004221
apksigner verify --print-certs "$APK"      # گواهی AOSP testkey
```

> **نکتهٔ هسته:** نسخهٔ `libv2ray` عمداً `v26.6.27` است. از xray-core `v26.7.11` به بعد، ساخت
> outbound برای **VLESS/Trojan بدون TLS روی IP عمومی** رد می‌شود و ۹۸ ردیف از ۱۰۵ ردیف این
> بک‌اند از همین نوع است. اگر نسخه را بالا بردید، انتظار داشته باشید بخش بزرگی از سرورها
> با پیام `vless without TLS or other encryption is prohibited…` رد شوند — (شرح کامل در
> [`README-fa.md`](README-fa.md) بخش «چرا این نسخهٔ هسته»).

---

## ۳) ساخت و انتشار در GitHub Actions

| ورک‌فلو | تریگر | چه می‌کند |
| --- | --- | --- |
| [`build-apks.yml`](../../.github/workflows/build-apks.yml) | push روی تغییرات `android-app/app/**`، `tools/**`، فایل‌های Gradle، یا `workflow_dispatch` | ماتریس `arm64-v8a` + `x86_64`، ساخت با کلید AOSP، بررسی وجود هر دو `.so` و نبود ABI اضافی، بررسی `package`/`versionCode`، ساخت `.sha256`، و انتشار **یک** ریلیز با تگ `trial-<run_number>` |
| [`e2e-real.yml`](../../.github/workflows/e2e-real.yml) | push روی برنچ + `workflow_dispatch` | آزمون «صفر ورودی» روی بک‌اند واقعی: دریافت فهرست، پینگ همه، اتصال، عبور ترافیک، تغییر سرور، قطع. گزارش را در `docs/e2e-real/` کامیت می‌کند |
| [`connect-test.yml`](../../.github/workflows/connect-test.yml) | push + `workflow_dispatch` | سرور Xray محلی روی runner، اتصال اپ، اثبات عبور بایت‌ها با لاگ سرور، پایداری سرور در «پینگ همه»، تغییر سرور |
| [`ui-snapshot.yml`](../../.github/workflows/ui-snapshot.yml) | push + `workflow_dispatch` | رانندگی رابط کاربری روی شبیه‌ساز و ثبت ۱۱ تصویر در `docs/screenshots/` |
| [`probe-api.yml`](../../.github/workflows/probe-api.yml) | تغییر `tools/probe-*.py` + `workflow_dispatch` | پروب‌های قرارداد بک‌اند (هدرها، اندپوینت‌ها، توزیع `price`) و انتشار نتیجه به‌صورت annotation |
| [`probe-rows.yml`](../../.github/workflows/probe-rows.yml) | تغییر `tools/probe-rows.py` | گرفتن نمونهٔ خام ردیف‌ها برای تحلیل آفلاین |
| [`probe-legacy.yml`](../../.github/workflows/probe-legacy.yml) | تغییر `tools/probe-legacy.py` | آزمون `version_code` نسخه‌های قدیمی |

نکات عملی:

- ورک‌فلوهای `e2e-real`، `connect-test`، `ui-snapshot` گزارش خودشان را **داخل مخزن کامیت**
  می‌کنند؛ آن کامیت با `[skip ci]` زده می‌شود تا اجرای تازه‌ای راه نیفتد و اجرای در حال
  انجام را کنسل نکند.
- برای اجرای دستی یک آزمون، یک کامیت خالی با کلیدواژه بزنید:

```bash
git commit --allow-empty -m "chore: tunnel check [net]"   # connect-test
git commit --allow-empty -m "chore: ui check [ui]"        # ui-snapshot
git commit --allow-empty -m "chore: e2e [real]"           # e2e-real
```

- خواندن لاگ کامل اجرا از بیرون ممکن نیست؛ نتیجهٔ هر اجرا در annotationها و در فایل‌های
  کامیت‌شده (`STATUS.md`، `CONNECT-REAL.md`) است.

---

## ۴) نسخه‌گذاری

| مقدار | جا | مقدار فعلی |
| --- | --- | --- |
| `applicationId` | `app/build.gradle.kts` | `co.asiven.vixentvpn.trial` (نصب کنار اپ اصلی) |
| `versionName` | همان | `3.2.0-trial` |
| `versionCode` | همان | `1004221` |
| `HEADER_APP_NAME` (بک‌اند) | همان | `co.asiven.vixentvpn` — **نباید** با پکیج عوض شود |
| `HEADER_VERSION_CODE` (بک‌اند) | همان | `1004220` — همان نسخهٔ اپ اصلی |
| `API_BASE` | همان | `https://managev1.xyz` |
| `TEST_URL` | همان | `https://www.gstatic.com/generate_204` |

`HEADER_*` عمداً از `applicationId` جدا هستند: بک‌اند بر اساس `app_name` + امضای APK به درخواست
جواب می‌دهد، پس تغییر پکیج برای «نصب کنار اپ اصلی» نباید هویت درخواست را عوض کند.
هدرها از `BuildConfig` خوانده می‌شوند (`ApiClient`)، نه از `context.packageName`.

برای بالا بردن نسخه:

```bash
# در app/build.gradle.kts
versionCode = 1004222
versionName = "3.2.0-trial.2"
```

سپس push کنید؛ `build-apks` خودش APK و ریلیز تازه می‌سازد.

---

## ۵) نقشهٔ ابزارها

| ابزار | کار |
| --- | --- |
| `tools/fetch-libv2ray.sh` | دانلود و بررسی `libv2ray.aar` (شامل کنترل `classes.jar` و وجود JNI) |
| `tools/build-hevtun.sh` | clone و ساخت `hev-socks5-tunnel` با `-DPKGNAME=co/asiven/vixentvpn/service -DCLSNAME=TProxyService` |
| `tools/fetch-testkey.sh` | ساخت `keystore.p12` از AOSP testkey + `keystore.properties` |
| `tools/connect-real.py` | درایور آزمون صفر-ورودی: `pm clear`، دریافت، مرتب‌سازی، کپی همه، پینگ، اتصال، ترافیک، تغییر سرور، قطع |
| `tools/connect-drive.py` | درایور آزمون تونل روی سرور محلی Xray (ورک‌فلوی `connect-test`) |
| `tools/ui-drive.py` | رانندگی رابط کاربری + اسکرین‌شات (ورک‌فلوی `ui-snapshot`) |
| `tools/probe-*.py` | پروب‌های بک‌اند (قرارداد، ردیف‌ها، قیمت، نسخه‌های قدیمی، رمزگشایی) |
| `tools/apk-keys.py` | رمزگشایی رشته‌های ScKit و پیدا کردن کلید آدرس API از APK اصلی |
| `tools/dcc-native-map.py` | استخراج نقشهٔ کلاس/متد کد بومی (`ApkDex2C`) |

---

## ۶) افزودن یا تغییر رفتار

- **پروتکل/کانفیگ جدید**: `core/ConfigBuilder.kt` (تابع `parse`) و مجموعهٔ `SUPPORTED`.
  اگر پروتکل با هستهٔ پین‌شده اجرا نمی‌شود، باید پیام خطای صریح برگردد، نه «متصل» دروغین.
- **تغییر متن یا چیدمان**: رشته‌ها در `res/values/strings.xml` (فارسی) و چیدمان‌ها در `res/layout/`.
  بعد از تغییر UI ورک‌فلوی `ui-snapshot` را اجرا کنید تا تصاویر تازه کامیت شوند.
- **تغییر منطق اتصال**: بعد از هر تغییر، **هر دو** آزمون `connect-test` (پشتهٔ تونل) و
  `e2e-real` (بک‌اند واقعی) باید سبز شوند. «متصل» بدون عبور ترافیک یک باگ است.
- **تغییر در هدرها/اندپوینت‌ها**: ابتدا پروب (`probe-api`) را اجرا کنید، نتیجه را در
  `api-contract-fa.md` ثبت کنید و بعد کد را تغییر دهید.

---

## ۷) عیب‌یابی ساخت

| خطا | علت | راه‌حل |
| --- | --- | --- |
| `Could not find libv2ray.aar` | `fetch-libv2ray.sh` اجرا نشده | اسکریپت را اجرا کنید؛ در CI خودکار است |
| `hev-socks5-tunnel شروع نشد` روی دستگاه | `.so` ساخته/بسته‌بندی نشده یا ABI اشتباه | `unzip -l` روی APK؛ `-PtargetAbi` درست را بدهید |
| `INSTALL_FAILED_NO_MATCHING_ABIS` | APK `arm64` روی شبیه‌ساز | فایل `x86_64` را نصب کنید |
| `e: Unresolved reference: BuildConfig` | `buildFeatures.buildConfig` خاموش | در `build.gradle.kts` روشن است؛ بازش نکنید |
| خطای امضا در بک‌اند (`Application sign is missing`) | APK با کلید دیگری امضا شده | با `fetch-testkey.sh` بسازید تا گواهی AOSP testkey شود |
