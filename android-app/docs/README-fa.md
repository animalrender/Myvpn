# MVPN Trial — کلاینت آزمایشی بر پایهٔ همان بک‌اند و همان هستهٔ APK اصلی

این پوشه یک اپ اندروید کامل و قابل‌ساخت است که **رفتار و ساختار** اپ تحلیل‌شده
(`co.asiven.vixentvpn` — «Vixen VPN» ۳٫۲٫۰) را بازتولید می‌کند، اما:

| حذف شده                            | دلیل / جایگزین                                                |
| ---------------------------------- | ------------------------------------------------------------- |
| کل منطق تبلیغ (AdMob / Fyber / …)  | اپ آزمایشی است؛ هیچ SDK تبلیغاتی و هیچ «الماس»ی وجود ندارد      |
| کل منطق حساب کاربری (Google Sign-In) | نیازی نیست؛ هویت دستگاه همان `ANDROID_ID` است                 |
| دروازهٔ `price` (خرید سرور)         | **سرورهای پولی هم نمایش داده و هم قابل اتصال‌اند**، فقط برچسب می‌خورند |
| Firebase (FCM / Analytics / Crashlytics / Remote Config) | هیچ وابستگی Firebase در `build.gradle` نیست |
| MMKV                                | `SharedPreferences` ساده (فقط برای اینکه لایهٔ بومی اضافه نشود)  |

و این‌ها **عیناً** حفظ شده‌اند:

* همان اندپوینت‌ها، همان کلیدها و همان هدرهای درخواست
  (`/api/token`, `/api/setting`, `/api/protocols`)
* همان امضای APK (کلید تست AOSP) تا هدرهای `sign` و `sha_hexadecimal` بایت‌به‌بایت مثل
  نسخهٔ اصلی محاسبه شوند
* همان هستهٔ اتصال: `libv2ray.aar` (بیلد gomobile از `xtls/xray-core`، دقیقاً همان
  خانواده‌ای که در APK اصلی به‌صورت `libgojni.so` هست) + `hev-socks5-tunnel` برای
  تبدیل TUN به SOCKS5 (همان نقشی که `libtun2socks.so` در نسخهٔ اصلی دارد)
* همان دو حالت `pref_mode`: `VPN` (کل دستگاه) و `PROXY` (فقط SOCKS/HTTP محلی روی
  پورت‌های `10808` و `10809`)
* همان قالب پیکربندی v2ray/Xray برای `vmess` / `vless` / `trojan` / `ss` / `socks` / `http`

---

## ۱. رابط کاربری — چه چیزی روی صفحه است

```
┌───────────────────────────────────────────────┐
│ MVPN Trial                          ⋮ (منو)   │
├───────────────────────────────────────────────┤
│ وضعیت: آماده / متصل / خطا                     │
│ حالت: VPN (کل دستگاه)                         │
│ [        اتصال / قطع اتصال        ]           │
├───────────────────────────────────────────────┤
│ [ دریافت و بازآوری همهٔ سرورها ]  [ پینگ همه ]│
│ ۱۲ سرور (رایگان: ۸ / پولی: ۴)        (spinner)│
├───────────────────────────────────────────────┤
│ 🇩🇪 Germany-01            vmess   رایگان  210ms│
│    مصرف: ↑ 12.4 MB · ↓ 88.1 MB                │
│    [پینگ] [جزئیات]                            │
│ 🇳🇱 NL-Premium            vless  پولی·۵💎  —  │
│    …                                          │
└───────────────────────────────────────────────┘
```

* **یک دکمه برای دریافت و بازآوری همهٔ سرورها** → `btn_fetch_all`
  (`getToken` → `getSetting` → `getProtocols`، پشت سر هم، با کش و به‌روزرسانی کامل فهرست).
* **فهرست قابل‌اسکرول** (`RecyclerView`) — همهٔ سرورها، بدون هیچ فیلتری.
* **پینگ تک‌سرور** (دکمهٔ `پینگ` روی هر ردیف) و **پینگ گروهی** (دکمهٔ `پینگ همه`،
  ۴ درخواست هم‌زمان).
* **انتخاب سرور** با لمس ردیف؛ سرور انتخاب‌شده هایلایت می‌شود و در `SharedPreferences`
  با کلید `selectedServer` می‌ماند.
* **جزئیات** هر سرور (لمس طولانی یا دکمهٔ «جزئیات»): همهٔ فیلدهای اصلی پاسخ سرور +
  JSON خام همان ردیف + دکمهٔ کپی.
* منوی سه‌نقطه: `JSON خام` (کل پاسخ `‎/api/protocols`)، `لاگ‌ها`، `تغییر حالت اتصال`.

### برچسب‌ها — «چه سروری بود، دقیقاً»

هر ردیف چهار برچسب دارد که از **فیلدهای اصلی سرور** ساخته می‌شوند و هیچ‌کدام دستکاری
نمی‌شوند:

| برچسب        | منبع در پاسخ API | نمونه |
| ------------ | ---------------- | ----- |
| نوع پروتکل   | خودِ `value` (scheme) یا `type`/`protocol` | `vmess`, `vless`, `trojan`, `ss`, `socks`, `http` |
| وضعیت قیمت   | `price`          | `رایگان` یا `پولی · ۵ الماس` |
| موقعیت       | `flag`/`country` (همان مقدار خام) | `DE`, `🇩🇪` یا هرچه سرور بدهد |
| مصرف/سهمیه   | `usage` → `upload/download/total/used/expireTime/deviceId` | `↑ 12.4 MB · ↓ 88.1 MB · سهمیه 2.0 GB` |

اگر سروری فیلد `price` نداشته باشد، برچسب «قیمت نامشخص» می‌خورد (به‌جای حدس زدن).
اگر `usage` نداشته باشد، «بدون سابقهٔ مصرف».

---

## ۲. قرارداد API (همان چیزی که APK اصلی صدا می‌زند)

مبنا: `https://managev1.xyz` (در نسخهٔ اصلی با AES/CBC از `Lk4/d` رمزگشایی می‌شود؛
اینجا ثابت `BuildConfig.API_BASE` است و با فیلد `apiUrl` پاسخ `‎/api/setting` هم
به‌روزرسانی می‌شود — همان «سوییچ دامنه از راه دور»).

| اندپوینت            | نقش                                   | نگاشت در APK اصلی |
| ------------------- | ------------------------------------- | ----------------- |
| `GET/POST /api/token`    | گرفتن توکن دستگاه (`deviceId`)    | `WelcomeActivity.getToken()` |
| `GET /api/setting`       | تنظیمات اپ (`testUrl`, `apiUrl`, …) | `WelcomeActivity.getAppSetting()` |
| `GET /api/protocols`     | **کل فهرست سرورها** (رایگان + پولی) | `WelcomeActivity.getData()` |

هدرهای هر درخواست (کلاس `ApiClient.kt`):

```
Content-Type: application/json
Accept: application/json
app_name: co.asiven.vixentvpn
version_code: 1004220
admobSeen: false            # فقط برای سازگاری سیمی؛ این اپ هیچ تبلیغی ندارد
token: <token>              # بعد از /api/token
Authorization: bearer <token>
sha_hexadecimal: <app_name>,<sha256-hex گواهی امضا>
sign: <Base64(sha256(گواهی امضا))>
```

* `sha_hexadecimal` و `sign` از **گواهی امضای همین APK** محاسبه می‌شوند
  (`Signing` در `ApiClient.kt`) — پس اگر اپ با کلید تست AOSP امضا شود (که در
  `.github/workflows/build-arm64.yml` انجام می‌شود)، مقدار این دو هدر دقیقاً برابر
  نسخهٔ اصلی است.
* هدر `firebase_token` **فرستاده نمی‌شود** (چون Firebase نداریم). اگر سرور آن را
  اجباری کرده باشد، در لاگ پاسخ ۴xx دیده می‌شود.
* برای اینکه یک سخت‌گیری کوچک سمت سرور کل اپ را از کار نیندازد، `ApiClient` هر
  اندپوینت را با چند حالت امتحان می‌کند: `GET` و `POST`، با/بدون `/` انتهایی، و
  `sha_hexadecimal` با حروف کوچک و بزرگ. اولین پاسخ موفق کش می‌شود.

---

## ۳. جریان کار در زمان اجرا

```
Application.onCreate
 └─ XrayCore.init()            Seq.setContext + Libv2ray.initCoreEnv(assetPath, xudpKey)

MainActivity
 ├─ بارگذاری کش (در صورت وجود) از SharedPreferences: protocolsCache
 └─ «دریافت و بازآوری همهٔ سرورها»
      ├─ /api/token    → token
      ├─ /api/setting  → testUrl / apiUrl / …
      └─ /api/protocols→ ServerParser → List<Server>  (بدون فیلتر)
            └─ ذخیره در کش + نمایش در RecyclerView

«پینگ» (تک یا همه)
 └─ ConfigBuilder.parse(server) → outbound
    └─ Libv2ray.measureOutboundDelay(pingConfig(outbound), testUrl)
       (همان تابعی که v2rayNG برای «real ping» استفاده می‌کند)

«اتصال»
 ├─ VpnService.prepare()  (فقط در حالت VPN)
 └─ VpnTunnelService
      ├─ Builder().addAddress(10.10.10.2/24).addRoute(0.0.0.0/0)
      │    .addDnsServer(1.1.1.1).addDisallowedApplication(خودمان)
      │    → ParcelFileDescriptor (fd)
      ├─ XrayCore.start(runtimeConfig(outbound), fd)
      │    └─ inbounds: socks 127.0.0.1:10808 (udp) + http 127.0.0.1:10809
      └─ HevTunnel.start(fd)
           └─ TProxyStartService(yaml, fd)   [libhev-socks5-tunnel.so]
```

در حالت `PROXY` مرحلهٔ TUN انجام نمی‌شود؛ فقط هسته بالا می‌آید و SOCKS/HTTP محلی
روی `10808`/`10809` سرویس می‌دهد (همان رفتار `V2RayProxyOnlyService` در نسخهٔ اصلی).

`addDisallowedApplication(خودمان)` حیاتی است: سوکت‌های خود هسته (به سمت سرور) نباید
داخل تونل بیفتند وگرنه حلقه می‌شود.

---

## ۴. ساخت (GitHub Actions) و خروجی

فایل: `.github/workflows/build-arm64.yml`

```
Checkout → JDK 17 → پیدا کردن SDK/NDK (تصویر رانر) 
  → tools/fetch-libv2ray.sh     (libv2ray.aar از ریلیز AndroidLibXrayLite → app/libs/)
  → tools/build-hevtun.sh       (ndk-build، APP_ABI=arm64-v8a، -DPKGNAME=co/asiven/vixentvpn/service)
                                 → app/src/main/jniLibs/arm64-v8a/libhev-socks5-tunnel.so
  → tools/fetch-testkey.sh      (کلید تست AOSP → signing/keystore.p12 + keystore.properties)
  → gradle assembleRelease      (فقط arm64-v8a)
  → بازرسی APK: وجود libgojni.so و libhev-socks5-tunnel.so، نبود هیچ رشتهٔ firebase
  → آپلود آرتیفکت + انتشار GitHub Release با تگ trial-arm64-<run>
```

* خروجی: `mvpn-trial-arm64-<run>.apk` + `.sha256`
* نسخه‌ها: `libv2ray.aar` از `AndroidLibXrayLite v26.10.21`، `hev-socks5-tunnel 2.19.3`
  (هر دو در اسکریپت‌ها قابل تغییرند: `LIBV2RAY_VERSION`, `HEV_VERSION`)
* هیچ فایل باینری سنگین یا کلیدی در گیت نیست: `app/libs/*.aar`, `jniLibs/`, `signing/`
  در `.gitignore` هستند و همه در رانر ساخته/گرفته می‌شوند.

ساخت دستی روی سیستم خودتان (با SDK/NDK نصب‌شده):

```bash
cd android-app
bash tools/fetch-libv2ray.sh
NDK_HOME=$ANDROID_NDK_HOME bash tools/build-hevtun.sh
bash tools/fetch-testkey.sh
gradle assembleRelease        # یا ./gradlew اگر wrapper اضافه کنید
```

---

## ۵. نصب و استفاده

```bash
adb install -r mvpn-trial-arm64-<run>.apk
```

> ⚠️ `applicationId` عمداً همان `co.asiven.vixentvpn` است (برای اینکه هدر `app_name`
> و امضا با نسخهٔ اصلی یکی باشد). بنابراین اگر نسخهٔ اصلی نصب است، اول آن را حذف کنید
> (`adb uninstall co.asiven.vixentvpn`)؛ در غیر این صورت نصب با خطای
> `INSTALL_FAILED_UPDATE_INCOMPATIBLE` شکست می‌خورد.

۱. اپ را باز کنید؛ در اولین اجرا خودش «دریافت همهٔ سرورها» را می‌زند.
۲. یک ردیف را لمس کنید (انتخاب) — یا با «جزئیات» همهٔ فیلدهایش را ببینید.
۳. «پینگ» تک‌سرور یا «پینگ همه».
۴. «اتصال»؛ دفعهٔ اول اندروید اجازهٔ VPN می‌پرسد.
۵. برای حالت فقط‌پروکسی: منو → «تغییر حالت اتصال»، بعد اتصال؛ سپس
   `socks5 127.0.0.1:10808` یا `http 127.0.0.1:10809` (از همان گوشی).

---

## ۶. عیب‌یابی

| نشانه | کار |
| ----- | --- |
| «فهرست سرورها دریافت نشد» | منو → «لاگ‌ها»؛ کد و متن پاسخ در آنجاست. `sign`/`sha_hexadecimal`/`token` هم لاگ می‌شوند |
| پاسخ ۴۰۱/۴۰۳ | یعنی بک‌اند امضا/توکن را نپذیرفته؛ مطمئن شوید APK با کلید تست AOSP امضا شده (`signing/SIGNING_INFO.txt` باید `testkey (AOSP…)` باشد) |
| «سرور هیچ مقدار اتصالی ندارد» | فیلد `value` سرور خالی/ناشناخته است؛ JSON خام همان سرور را از پنجرهٔ «جزئیات» کپی کنید |
| «hev-socks5-tunnel شروع نشد» | یعنی `libhev-socks5-tunnel.so` نیامده یا `PKGNAME` با `co/asiven/vixentvpn/service` نساخته شده |
| اتصال برقرار می‌شود ولی اینترنت نیست | سرور پولی ممکن است سمت سرور قفل باشد (کلاینت اصلی هم بدون خرید عبور نمی‌داد)؛ یا حالت PROXY را امتحان کنید |
| لاگ کامل | `adb logcat -s MvpnTrial` یا فایل `files/mvpn-trial.log` داخل اپ |

---

## ۷. نقشهٔ کد

```
android-app/
├─ app/src/main/java/co/asiven/vixentvpn/
│  ├─ service/
│  │  ├─ TProxyService.java     ← JNI خام hev (نام کلاس بخشی از ABI است؛ جابه‌جا نکنید)
│  │  ├─ HevTunnel.kt           ← نوشتن YAML + start/stop/stat
│  │  └─ VpnTunnelService.kt    ← VpnService، TUN، ترتیب راه‌اندازی، نوتیفیکیشن، برادکست وضعیت
│  └─ trial/
│     ├─ TrialApp.kt
│     ├─ data/ApiClient.kt      ← اندپوینت‌ها + هدرها + sign/sha_hexadecimal + fallbacks
│     ├─ data/Models.kt         ← Server / Usage / AppSetting / ServerParser (تحمل تفاوت نام کلیدها)
│     ├─ data/Prefs.kt          ← کلیدهای هم‌نام با MMKV اصلی: token, apiUrl, testUrl, pref_mode
│     ├─ core/ConfigBuilder.kt  ← vmess/vless/trojan/ss/socks/http → outbound + کانفیگ کامل
│     ├─ core/XrayCore.kt       ← initCoreEnv / startLoop / stopLoop / measureOutboundDelay
│     ├─ ui/MainActivity.kt     ← یک دکمه دریافت همه، پینگ تک/گروهی، انتخاب، اتصال
│     ├─ ui/ServerAdapter.kt    ← ردیف‌ها و برچسب‌ها
│     └─ util/AppLog.kt         ← لاگ درون‌برنامه‌ای + فایل
├─ app/src/main/res/…           ← تم تیره، رشته‌های فارسی، آیکون
├─ tools/fetch-libv2ray.sh
├─ tools/build-hevtun.sh
├─ tools/fetch-testkey.sh
└─ tools/gen_icon.py            ← تولید آیکون (بدون وابستگی بیرونی)
```

---

## ۸. محدودیت‌ها و ریسک‌های شناخته‌شده (صادقانه)

۱. **بک‌اند ممکن است امضا را سخت‌گیرانه چک کند.** راه‌حل ما امضای اپ با کلید تست
   AOSP است تا هدرها یکسان شوند؛ ولی اگر سرور فیلد دیگری (مثل `firebase_token`) یا
   اثر انگشت دیگری هم بخواهد، ممکن است رد شود. در آن حالت لاگ/JSON خام دقیقاً نشان
   می‌دهد چه چیزی برگشته است.
۲. **شکل دقیق JSON سرورها از روی APK قابل استخراج نبود** (کلاس‌های `Protocol` توسط
   Dex2C به کد بومی منتقل شده‌اند). به همین دلیل `ServerParser` نسبت به نام کلیدها
   تحمل‌پذیر نوشته شده (`price/coin/cost`, `value/config/link/url/...`,
   `flag/country/cc/…`) و JSON خام هر سرور در «جزئیات» قابل مشاهده است. اگر فیلدی
   متفاوت بود، فقط همان یک تابع باید تطبیق داده شود.
۳. **سرورهای پولی**: این نسخه دروازهٔ قیمت را حذف کرده و اجازهٔ تلاش برای اتصال
   می‌دهد، اما اگر خود سرور نشست را رد کند، کلاینت کاری نمی‌تواند بکند.
۴. **بدون Firebase** یعنی هیچ پیام سرور مبنی بر «آپدیت جدید» یا «تغییر دامنه» از طریق
   push دریافت نمی‌شود؛ اما `apiUrl` از پاسخ `setting` خوانده و ذخیره می‌شود.
۵. **فقط arm64-v8a** ساخته می‌شود (طبق درخواست). روی گوشی ۳۲ بیتی نصب نمی‌شود.
۶. **مجوز و لایسنس**: کد این پوشه اصیل است، اما `libv2ray.aar` (بر پایهٔ
   AndroidLibXrayLite/v2rayNG) و `hev-socks5-tunnel` پروژه‌های GPL-3.0 هستند و
   `xray-core` تحت MPL-2.0 است. این بیلد برای تست شخصی است؛ اگر قصد توزیع عمومی
   دارید، شرایط GPL (انتشار سورس) را رعایت کنید.

---

## ۹. تفاوت‌های عمدی با نسخهٔ اصلی

| موضوع | نسخهٔ اصلی | MVPN Trial |
| ----- | ---------- | ---------- |
| ثبت‌نام/حساب | Google Sign-In اختیاری | ندارد |
| تبلیغ | AdMob + FairBid + … | ندارد |
| خرید سرور | `i4.c.a()` با الماس | ندارد؛ همهٔ سرورها آزادند |
| سقف زمان اتصال | `connectionTimeLimit`/`connectedUntil` | ندارد |
| Firebase | FCM/Crashlytics/Analytics/RemoteConfig | ندارد |
| ذخیره‌سازی | MMKV (بومی) | SharedPreferences |
| انتخاب سرور | `MainActivity` + RecyclerView v2rayNG | همان الگو، ساده‌شده |
| هسته | `libgojni.so` + `libtun2socks.so` | `libgojni.so` از libv2ray.aar + `libhev-socks5-tunnel.so` |
