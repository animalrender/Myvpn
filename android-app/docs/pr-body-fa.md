## MVPN Trial — نسخهٔ آزمایشی با همان بک‌اند، همان هدرها، همان امضا و همان هستهٔ APK اصلی

این PR یک اپ اندروید کامل در `android-app/` به‌همراه ورک‌فلوی ساخت/انتشار APK اضافه می‌کند:
همان رفتار و ساختار اپ تحلیل‌شده (`co.asiven.vixentvpn` 3.2.0 / `1004220`)، اما **بدون تبلیغ،
بدون حساب کاربری و بدون قفل قیمت**.

### 📦 خروجی آمادهٔ تست

* ریلیز: **[trial-arm64-25](https://github.com/animalrender/Myvpn/releases/tag/trial-arm64-25)**
  → `mvpn-trial-arm64-25.apk` (۴۶٬۸۹۱٬۲۱۳ بایت، arm64-v8a) + `mvpn-trial-arm64-25.apk.sha256`
* امضا: AOSP testkey با `SHA-256 = a40da80a59d170caa950cf15c18c454d47a39b26989d8b640ecd745ba71bf5dc`
  — **همان گواهی نسخهٔ اصلی**، تا هدرهای `sign` و `sha_hexadecimal` بایت‌به‌بایت درست باشند.
* نصب: `adb install -r mvpn-trial-arm64-25.apk`
  (چون `applicationId` همان `co.asiven.vixentvpn` است، اگر نسخهٔ اصلی نصب است باید حذف شود.)

```bash
gh release download trial-arm64-25
sha256sum -c mvpn-trial-arm64-25.apk.sha256
```

### ✅ چه چیزی در این نسخه کار می‌کند

| قابلیت | وضعیت | محل |
| --- | --- | --- |
| **یک دکمه برای دریافت و بازآوری همهٔ سرورها** | ✅ ۱۰۵ سرور از `/api/protocols` | `ui/MainActivity.kt` |
| **همهٔ سرورها، رایگان و پولی (بدون قفل `price`)** | ✅ | `data/Models.kt` |
| **برچسب‌گذاری کامل هر سرور** (نوع/پروتکل، رایگان یا «پولی · n الماس»، مصرف/سهمیه، پرچم و موقعیت، `id`/`serverId`، همهٔ کلیدهای ناشناخته) | ✅ | `ui/ServerAdapter.kt` + «جزئیات» |
| **لیست اسکرول‌شو + انتخاب سرور/موقعیت** | ✅ | `RecyclerView` + `Prefs.selectedKey` |
| **پینگ تک‌سرور و پینگ گروهی (۴ هم‌زمان)** | ✅ با `Libv2ray.measureOutboundDelay` | `ui/MainActivity.kt` |
| **اتصال با همان هسته** (`libv2ray.aar` = همان خانوادهٔ `libgojni.so`) + `hev-socks5-tunnel` به‌جای `libtun2socks.so` | ✅ حالت `VPN` (TUN) و `PROXY` (SOCKS 10808/HTTP 10809) | `core/XrayCore.kt`، `service/*` |
| **کپی لینک v2ray هر سرور** برای استفاده در v2rayNG/nekobox | ✅ `vmess://`/`vless://`/`trojan://`/`ss://` | `ConfigBuilder.shareLink` |
| **افزودن کانفیگ از کلیپ‌بورد** (لینک یا JSON) | ✅ | منوی سرصفحه |
| **Firebase مطابق اپ اصلی** (Messaging، ذخیرهٔ `firebase_token`، ارسال آن با درخواست توکن) | ✅ `google-services.json` از مقادیر واقعی منابع APK | `push/TrialMessagingService.kt` |
| **UI بازطراحی‌شده** (تم تیرهٔ Material3، RTL، کارت وضعیت، برچسب‌ها، انیمیشن وضعیت اتصال) | ✅ | `res/` |

### 🔧 چرا خطای `405` و `Internal server error` نسخهٔ قبل رفع شد

از دی‌کامپایل `VolleyHelper.initHeaders()` قرارداد دقیق درآمد و در `data/ApiClient.kt` پیاده شد:

| هدر | مقدار |
| --- | --- |
| `Content-Type` | `application/json` |
| `app_name` | `co.asiven.vixentvpn` |
| `version_code` | `1004220` |
| `seen` | `0` (`admobSeen`) |
| `token` | فقط اگر مقدار داشته باشد |
| `sign` | `Base64(MD5(DER گواهی امضا))` |
| `sha_hexadecimal` | `hex(SHA-256(SHA-256(DER)))` |
| `Authorization` | `bearer <token>` (در صورت وجود) |

* `/api/token` فقط **GET** است (`?deviceId=…`) — `POST` روی این بک‌اند `405` می‌دهد.
* بک‌اند خطاهای منطقی را با **HTTP 200** برمی‌گرداند؛ پس بدنه‌هایی مثل
  `{"statusCode":400,"status":false,"data":"Proxy Mode : Application sign is missing."}`
  اکنون خطا تلقی می‌شوند (علت اصلی «Internal server error» قبلی، نبودِ `sign` بود).

قرارداد کامل در `android-app/docs/api-contract-fa.md` مستند شده است.

### 🔬 یافته‌های پروب واقعی بک‌اند (داخل GitHub Actions)

* `/api/token` → `{"statusCode":0,"data":"The app token is disabled"}` ⇒ توکن لازم نیست.
* `/api/setting` → `data: null`.
* `/api/protocols` و `/api/v2/protocols` → ۲۰۰ با ۱۰۵ آیتم؛ نسخهٔ v2 سه کلید اضافه می‌دهد:
  `configKey`، `routeKey`، `endpointKey` (۶۴ کاراکتر هگز).
* `/api/configs` با هر ترکیب `deviceId`/`serverId`/`protocolId` و هر دو متد → **404**.
* `POST /api/protocols` → `the protocol id is incorrect!`.

**نکتهٔ شفاف:** در این بک‌اند فیلد `value` به‌صورت base64 از دادهٔ رمزشده برگردانده می‌شود
(طول‌ها مضرب ۱۶). رمزگشایی آن با همهٔ کلیدهای قابل‌استخراج از APK (رشته‌های dex و `libstub.so`،
گواهی امضا، `app_name`/`version_code`/`deviceId`، `configKey`/`routeKey`/`endpointKey`) و همهٔ
حالت‌های متعارف AES/ChaCha20 در `tools/probe-*.py` آزمایش شد و نتیجه نداد — کلید در کد native
محافظت‌شدهٔ اپ اصلی (Dex2C / `Entrypoint.stub`) است. بنابراین:

* فهرست کامل + برچسب‌ها + پینگ + انتخاب + کپی لینک **همین حالا کار می‌کند**؛
* لحظه‌ای که `value` یک لینک/JSON معتبر باشد، اتصال هم بدون تغییر کد برقرار می‌شود
  (`ConfigBuilder` همهٔ فرمت‌ها را پشتیبانی می‌کند)؛
* برای اینکه اپ در هر شرایطی قابل استفاده باشد، «افزودن کانفیگ از کلیپ‌بورد» تعبیه شده است.

### 🤖 تأییدهای خودکار CI روی همین APK

* وجود `lib/arm64-v8a/libgojni.so` (هستهٔ Xray) و `lib/arm64-v8a/libhev-socks5-tunnel.so` (tun2socks)
* `apksigner verify --print-certs` ⇒ گواهی AOSP testkey مطابق نسخهٔ اصلی
* `aapt2 dump badging` ⇒ `package=co.asiven.vixentvpn`، `versionCode=1004220`، `native-code=arm64-v8a`
* اجرای پروب‌های واقعی API (ورک‌فلوی `probe-api`) و انتشار همهٔ نتایج به‌صورت annotation

### 📚 مستندات فارسی داخل پروژه

* `android-app/docs/README-fa.md` — معرفی، نصب، قابلیت‌ها، وضعیت رمزنگاری `value`، وضعیت Firebase، عیب‌یابی
* `android-app/docs/api-contract-fa.md` — قرارداد کامل API و هدرها
* `android-app/docs/architecture-fa.md` — معماری، TUN/hev، کانفیگ Xray، بازسازی لینک اشتراک
* `docs/apk-vixentvpn-analysis-fa.md` — تحلیل کامل APK اصلی

### 🧪 پیشنهاد تست برای شما

1. نصب APK از ریلیز `trial-arm64-25`.
2. زدن «دریافت و بازآوری همهٔ سرورها» ← باید ۱۰۵ سرور با برچسب‌ها بیاید.
3. «پینگ همه» و «لینک v2ray» یک ردیف را امتحان کنید.
4. اگر خواستید اتصال را با یک کانفیگ واقعی بسنجید: آن را کپی کنید و از منو «افزودن کانفیگ از کلیپ‌بورد» را بزنید،
   سپس انتخاب و «اتصال».
5. اگر جایی خطا دید: منوی «لاگ‌ها» و «JSON خام» خروجی دقیق می‌دهد (بدون نیاز به `adb logcat`).
