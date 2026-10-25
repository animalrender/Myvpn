# MVPN Trial — کلاینت آزمایشی اندروید (مستندات فارسی)

این پوشه یک اپ اندروید کامل و مستقل است که **همان رفتار/ساختار اپ تحلیل‌شده** (`co.asiven.vixentvpn`)
را بازتولید می‌کند، اما:

| حذف شده | توضیح |
| --- | --- |
| منطق تبلیغات | Admob / FairBid / native ad / interstitial / reward — هیچ‌کدام وجود ندارند |
| منطق کاربر و حساب | ورود، ثبت‌نام، دستگاه‌های متصل، «زمان اتصال» و پاداش‌های وابسته |
| دروازهٔ `price` | سرورهای پولی **پنهان یا قفل نمی‌شوند**؛ همهٔ ۱۰۵ سرور نمایش داده می‌شوند |
| خرید سکه/الماس | هیچ مسیر پرداخت یا مصرف سکه وجود ندارد |

| حفظ شده | توضیح |
| --- | --- |
| همان دامنه و اندپوینت‌ها | `https://managev1.xyz` + `/api/token`، `/api/setting`، `/api/protocols`، `/api/protocols/<operator>`، `/api/v2/protocols`، `/api/configs` |
| همان هدرها و امضا | `app_name`، `version_code`، `seen`، `token`، `sign`، `sha_hexadecimal`، `Authorization` |
| همان شناسهٔ اپ | `applicationId = co.asiven.vixentvpn`، `versionCode = 1004220`، `versionName = 3.2.0-trial` |
| همان هستهٔ تونل | `libv2ray.aar` (gomobile build از `xtls/xray-core`) + `hev-socks5-tunnel` (tun2socks) |
| همان حالت‌های اتصال | `VPN` (کل دستگاه، TUN) و `PROXY` (SOCKS/HTTP محلی) |

> نکته: در این نسخه `firebase_token` ارسال نمی‌شود. دلیلش در بخش
> [«وضعیت Firebase»](#وضعیت-firebase) آمده است.

---

## ۱) نصب و اجرای سریع

1. از صفحهٔ [Releases](https://github.com/animalrender/Myvpn/releases) آخرین فایل
   `mvpn-trial-arm64-*.apk` را دانلود کنید (به همراه فایل `.sha256`).
2. روی گوشی اندروید ۷ (API 24) به بالا و **arm64-v8a** نصب کنید:
   ```bash
   adb install -r mvpn-trial-arm64-XX.apk
   ```
3. اپ را باز کنید. بار اول خودکار فهرست سرورها را می‌گیرد؛ هر وقت خواستید دکمهٔ
   **«دریافت و بازآوری همهٔ سرورها»** را بزنید.
4. یک سرور را با لمس انتخاب کنید ← **اتصال**. اولین بار اندروید اجازهٔ VPN می‌خواهد.

خروجی گرفتن بدون نصب (تأیید صحت دانلود):

```bash
sha256sum -c mvpn-trial-arm64-XX.apk.sha256
apksigner verify --print-certs mvpn-trial-arm64-XX.apk    # گواهی: AOSP testkey
```

---

## ۲) قابلیت‌ها

- **یک دکمه برای دریافت و بازآوری همهٔ سرورها** (فعال + تنظیمات + توکن، به‌ترتیب همان اپ).
- **لیست اسکرول‌شو** از همهٔ سرورها؛ هر ردیف برچسب‌های اصلی سرور را نشان می‌دهد:
  - پرچم/کشور (`name` + ایموجی پرچم داخل `name` یا فیلد `flag`)
  - **نوع/پروتکل** استخراج‌شده از مقدار اتصال (`vmess`/`vless`/`trojan`/`ss`/`socks`/`http`/`json`)
  - **قیمت اصلی** (`price`) با تفکیک «رایگان» و «پولی · n الماس»
  - **مصرف/سهمیه** (`usage`) و `id`/`serverId`
  - همهٔ کلیدهای ناشناختهٔ پاسخ هم در «جزئیات» و «JSON خام» قابل مشاهده‌اند
- **پینگ تک‌تک سرورها** (دکمهٔ `پینگ` روی هر ردیف) و **پینگ همه** (۴ درخواست هم‌زمان).
  پینگ با `Libv2ray.measureOutboundDelay(config, testUrl)` انجام می‌شود؛ یعنی همان سنجش
  تأخیری که هستهٔ Xray برای اپ اصلی انجام می‌دهد، نه ICMP ساده.
- **انتخاب سرور/موقعیت** با لمس ردیف؛ انتخاب در حافظه ذخیره می‌شود.
- **کپی لینک v2ray هر سرور** (دکمهٔ «لینک v2ray») تا همان سرور را در v2rayNG/nekobox هم
  اضافه کنید. خروجی: `vmess://`/`vless://`/`trojan://`/`ss://` بازسازی‌شده از کانفیگ.
- **افزودن کانفیگ از کلیپ‌بورد** (منوی سه‌نقطه) برای وقتی که کانفیگ را از منبع دیگری دارید.
- **دو حالت اتصال**: `VPN` (TUN + hev) و `PROXY` (فقط SOCKS 10808 / HTTP 10809 روی localhost).
- **گزارش داخلی**: «JSON خام» آخرین پاسخ بک‌اند و «لاگ‌ها» (درخواست‌ها + هسته) برای عیب‌یابی.
- رابط کاربری تیره و RTL، بدون تبلیغ و بدون هیچ صفحهٔ اضافه.

---

## ۳) قرارداد بک‌اند (همان اپ)

جزئیات کامل در [`api-contract-fa.md`](api-contract-fa.md). خلاصه:

- Base URL: `https://managev1.xyz` (در اپ اصلی داخل MMKV کلید `apiUrl` و به‌صورت
  AES/CBC/PKCS5 رمزشده نگه‌داری می‌شود؛ مقدار ثابت در `BuildConfig.API_BASE` است).
- هدرها:

| هدر | مقدار |
| --- | --- |
| `Content-Type` | `application/json` |
| `app_name` | `co.asiven.vixentvpn` (نام پکیج) |
| `version_code` | `1004220` |
| `seen` | `0` (`admobSeen`) |
| `token` | توکن دستگاه؛ اگر خالی باشد ارسال نمی‌شود |
| `sign` | `Base64(MD5(DER گواهی امضا))` |
| `sha_hexadecimal` | `hex(SHA-256(SHA-256(DER گواهی)))` |
| `Authorization` | `bearer <token>` (در صورت وجود) |

پاسخ‌ها همیشه پوشش `{"statusCode":…,"status":…,"data":…}` دارند و **کد ۲۰۰ HTTP کافی نیست**؛
اپ بدنه‌هایی مثل `{"statusCode":400,"status":false,"data":"Proxy Mode : Application sign is missing."}`
را خطا حساب می‌کند (این همان خطای «Internal server error» نسخهٔ قبلی بود).

---

## ۴) ساخت با GitHub Actions

تنها مسیر ساخت، ورک‌فلوی [`.github/workflows/build-arm64.yml`](../../.github/workflows/build-arm64.yml) است:

```bash
gh workflow run build-arm64.yml
gh run watch
gh release list                     # تگ: trial-arm64-<شمارهٔ اجرا>
```

ورک‌فلو در همان runner:

1. `tools/fetch-libv2ray.sh` — دانلود `libv2ray.aar` از [AndroidLibXrayLite](https://github.com/2dust/AndroidLibXrayLite)
   (آخرین ریلیز `v26.10.21`) و قرار دادن آن در `app/libs/`.
2. `tools/build-hevtun.sh` — clone کردن [hev-socks5-tunnel](https://github.com/heiher/hev-socks5-tunnel)
   تگ `2.19.3` و ساخت کتابخانهٔ JNI با نام پکیج `co/.asiven/.vixentvpn/.service` و کلاس
   `TProxyService` (پسوند `.so` در `app/src/main/jniLibs/arm64-v8a/`).
3. `tools/fetch-testkey.sh` — ساخت `signing/keystore.p12` از AOSP testkey تا **گواهی امضای APK
   همان گواهی اپ اصلی باشد** (هدرهای `sign`/`sha_hexadecimal` باید تطبیق داشته باشند).
4. `gradle assembleRelease` ← بررسی وجود هر دو `.so` در APK، چاپ `aapt2 badging`،
   `apksigner verify --print-certs` و ساخت `.sha256`.
5. انتشار Release با نام `trial-arm64-<run_number>`.

ساخت دستی روی ماشین خودتان (نیاز به JDK 17، Android SDK 35، NDK):

```bash
cd android-app
bash tools/fetch-libv2ray.sh
bash tools/build-hevtun.sh 2.19.3
bash tools/fetch-testkey.sh
gradle assembleRelease   # خروجی: app/build/outputs/apk/release/
```

---

## ۵) نقشهٔ کد

| مسیر | نقش |
| --- | --- |
| `app/src/main/java/co/asiven/vixentvpn/trial/TrialApp.kt` | `Application`: لاگ + آماده‌سازی هسته |
| `.../trial/data/ApiClient.kt` | ساخت هدرها، `sign`/`sha_hexadecimal`، فراخوانی اندپوینت‌ها، تشخیص خطای منطقی |
| `.../trial/data/Models.kt` | مدل سرور/مصرف/تنظیمات + پارسر انعطاف‌پذیر پاسخ بک‌اند |
| `.../trial/data/Prefs.kt` | حافظهٔ محلی (توکن، `apiUrl`، `testUrl`، حالت، کش سرورها، انتخاب) |
| `.../trial/core/ConfigBuilder.kt` | تبدیل `value` به outbound اکستری + ساخت کانفیگ اجرا/پینگ + بازسازی لینک اشتراک |
| `.../trial/core/XrayCore.kt` | پوستهٔ `libv2ray.aar`: `initCoreEnv`، `startLoop/stopLoop`، `measureOutboundDelay` |
| `.../service/VpnTunnelService.kt` | سرویس Foreground + ساخت TUN + اتصال به hev + اعلان وضعیت |
| `.../service/TProxyService.java` | اعلان متدهای native همان ABI که `hev-jni.c` انتظار دارد |
| `.../service/HevTunnel.kt` | نوشتن `tunnel.ini` (YAML) و راه‌اندازی/توقف hev |
| `.../trial/ui/MainActivity.kt` | صفحهٔ اصلی: دریافت، پینگ، انتخاب، اتصال، کپی لینک، کلیپ‌بورد |
| `.../trial/ui/ServerAdapter.kt` | لیست اسکرول‌شو با برچسب‌ها و وضعیت پینگ |
| `app/src/main/res/...` | تم تیرهٔ Material3، چیدمان‌ها، رشته‌های فارسی |
| `tools/probe-*.py` | پروب‌های واقعی بک‌اند (برای تأیید قرارداد API؛ در CI اجرا می‌شوند) |

جریان اتصال (خلاصه):

```
انتخاب سرور → ConfigBuilder.parse(value) → outbound Xray
            → ConfigBuilder.runtimeConfig(outbound)   (SOCKS/HTTP 10808/10809 + direct/block)
mode == VPN   → VpnService(TUN 10.10.10.2/24, MTU 1500) → HevTunnel(tunFd)
              → XrayCore.start(config, tunFd = TUN)
mode == PROXY → HevTunnel(fd = 0) → locale SOCKS/HTTP → XrayCore.start(config, 0)
```

---

## ۶) وضعیت رمزنگاری `value` در بک‌اند

این موضوع مهم است و شفاف مستند می‌شود. پروب‌های `tools/probe-*.py` (که داخل GitHub Actions و با
اینترنت واقعی اجرا شده‌اند) نشان می‌دهند:

- `/api/protocols` و `/api/v2/protocols` با هدرهای صحیح **۲۰۰** می‌دهند و ۱۰۵ آیتم برمی‌گردانند
  (نام، `id`، `serverId`، `price`، `usage`)، اما فیلد `value` در پاسخ **base64 از دادهٔ رمزشده** است
  (طول‌ها مضرب ۱۶، آنتروپی بالا). `/api/v2/protocols` سه کلید اضافه هم می‌دهد:
  `configKey`، `routeKey`، `endpointKey` (هر کدام ۶۴ کاراکتر هگز).
- `/api/configs` (هم GET و هم POST، با هر ترکیب `deviceId`/`serverId`/`protocolId`) در بک‌اند فعلی
  **۴۰۴** است؛ `POST /api/protocols` با هر بدنه‌ای پاسخ `the protocol id is incorrect!` می‌دهد.
- `/api/token` می‌گوید `The app token is disabled` (پس توکن لازم نیست).
- رمزگشایی `value` با همهٔ کلیدهای قابل استخراج از خود APK (رشته‌های dex، `libstub.so`، گواهی امضا،
  `app_name`/`version_code`/`deviceId`، `configKey`/`routeKey`/`endpointKey`) و همهٔ حالت‌های متعارف
  AES (ECB/CBC/CTR/CFB/OFB/GCM) و ChaCha20/Salsa20 آزمایش شد و نتیجه نداد؛ یعنی کلید/الگوریتم
  رمزگشایی در کد native محافظت‌شدهٔ اپ اصلی (Dex2C، `libstub.so`، `EntryPoint.stub`) نگه‌داری می‌شود و
  از سمت کلاینت بدون آن باینری قابل بازتولید نیست.

نتیجهٔ عملی برای این نسخهٔ آزمایشی:

- فهرست کامل سرورها + همهٔ برچسب‌ها + پینگ + انتخاب + کپی لینک **کار می‌کند** (به‌محض اینکه مقدار
  `value` متن‌باز/لینک باشد، اتصال هم بدون تغییر کد برقرار می‌شود).
- اگر بک‌اند مقدار رمزشده برگرداند، اپ خطا را پنهان نمی‌کند: در «جزئیات سرور» دلیل دقیق
  («سرور هیچ مقدار اتصالی ندارد» / «پروتکل پشتیبانی‌نشده») و در «لاگ‌ها» وضعیت کامل دیده می‌شود.
- مسیر جایگزین تعبیه‌شده: **«افزودن کانفیگ از کلیپ‌بورد»** — هر لینک/JSON معتبر v2ray را می‌توانید
  وارد کنید و با همان هستهٔ Xray/hev وصل، پینگ و کپی کنید.

---

## ۷) وضعیت Firebase

در اپ اصلی، Firebase (Messaging + Remote Config) سه کار می‌کند: نوشتن `firebase_token` در MMKV،
دریافت پیام‌های به‌روزرسانی، و کش تنظیمات از راه دور. برای افزودن آن به این نسخه لازم است:

1. فایل `google-services.json` پروژهٔ Firebase همان اپ (که در مخزن اپ نیست و باید از کنسول گرفته شود)،
2. پلاگین `com.google.gms.google-services` و وابستگی `firebase-messaging`،
3. یک `FirebaseMessagingService` برای ذخیرهٔ توکن و ارسال آن در هدر `token`.

تا زمانی که `google-services.json` در دسترس نیست، اپ عمداً بدون Firebase ساخته می‌شود تا
**بیلد شکسته نشود**؛ ساختار کد طوری است که افزودن این سه مورد هیچ تغییری در بقیهٔ منطق لازم نداشته باشد
(محل اتصال: `ApiClient.fetchToken()` و `Prefs.token`).

---

## ۸) عیب‌یابی

| نشانه | معنا و راه‌حل |
| --- | --- |
| «فهرست سرورها دریافت نشد» | منوی «لاگ‌ها» را ببینید؛ اگر `statusCode:400` با متن sign missing بود یعنی امضای APK با امضای اپ اصلی یکی نیست (باید با `fetch-testkey.sh` ساخته شود). |
| «سرور هیچ مقدار اتصالی ندارد» | مقدار `value` خالی یا رمزشده است (بخش ۶). |
| پینگ همه `—` می‌ماند | سرورها مقدار اتصال معتبر ندارند، یا شبکه بسته است؛ تک‌تک پینگ بزنید و لاگ هسته را ببینید. |
| اتصال برقرار می‌شود ولی اینترنت نیست | حالت را روی `PROXY` بگذارید و با `socks5://127.0.0.1:10808` تست کنید (برای بررسی این‌که مشکل از TUN/hev است یا از سرور). |
| «hev-socks5-tunnel شروع نشد» | یعنی `.so` در APK نیست یا نام پکیج/کلاس JNI نمی‌خواند؛ ورک‌فلو این را با `unzip -l` بررسی می‌کند. |

---

## ۹) مجوزها و وابستگی‌ها

- کد این پوشه (اپ آزمایشی) اختصاصی همین مخزن است.
- `libv2ray.aar` از [AndroidLibXrayLite](https://github.com/2dust/AndroidLibXrayLite) (GPL-3.0) و
  هستهٔ [Xray-core](https://github.com/XTLS/Xray-core) (MPL-2.0).
- [hev-socks5-tunnel](https://github.com/heiher/hev-socks5-tunnel) (GPL-3.0) به‌صورت سورس در CI
  ساخته می‌شود و در مخزن کامیت نمی‌شود.
- برای استفادهٔ شخصی/آزمایشی؛ توزیع عمومی APK با این وابستگی‌ها مستلزم رعایت GPL است.

مستندات مرتبط:

- [قرارداد کامل API](api-contract-fa.md)
- [معماری و جزئیات پیاده‌سازی](architecture-fa.md)
- [تحلیل APK اصلی](../../docs/apk-vixentvpn-analysis-fa.md)
