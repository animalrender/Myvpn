## MVPN Trial — نسخهٔ آزمایشی با همان بک‌اند، همان هدرها، همان امضا و همان هستهٔ APK اصلی

این PR یک اپ اندروید کامل در `android-app/` به‌همراه ورک‌فلوی ساخت/انتشار APK اضافه می‌کند:
همان رفتار و ساختار اپ تحلیل‌شده (`co.asiven.vixentvpn` 3.2.0 / `1004220`)، اما **بدون تبلیغ،
بدون حساب کاربری و بدون قفل قیمت**.

**نکتهٔ کلیدی:** اپ **از کاربر هیچ کانفیگ/لینک/کلیدی نمی‌خواهد**. فهرست سرورها را خودش از
بک‌اند می‌گیرد، مقدار رمزشدهٔ `value` هر ردیف را در خود دستگاه باز می‌کند
(`AES/CBC`، کلید = `key_<id>`) و با همان هستهٔ Xray وصل می‌شود — دقیقاً مثل نسخهٔ اصلی.

### 📦 خروجی آمادهٔ تست

* ریلیز: **[trial-34](https://github.com/animalrender/Myvpn/releases/tag/trial-34)** — **دو APK**:
  * `mvpn-trial-arm64-34.apk` — گوشی/تبلت (`arm64-v8a`)
  * `mvpn-trial-x86_64-34.apk` — شبیه‌ساز/کروم‌بوک (`x86_64`)
  * هر دو با فایل `.sha256`
* امضا: AOSP testkey با `SHA-256 = a40da80a59d170caa950cf15c18c454d47a39b26989d8b640ecd745ba71bf5dc`
  — **همان گواهی نسخهٔ اصلی**، تا هدرهای `sign` و `sha_hexadecimal` بایت‌به‌بایت درست باشند.
* نصب: `adb install -r mvpn-trial-arm64-34.apk`
  **کنار نسخهٔ اصلی** نصب می‌شود — `applicationId` این نسخه `co.asiven.vixentvpn.trial` است،
  پس لازم نیست اپ اصلی را حذف کنید (هدر `app_name` برای بک‌اند همان `co.asiven.vixentvpn` می‌ماند).

```bash
gh release download trial-34
sha256sum -c mvpn-trial-arm64-9.apk.sha256
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
| **کپی همهٔ لینک‌ها با یک لمس** در سه گروه: همه / فقط پینگ‌داده‌ها / فقط بی‌پینگ‌ها (هر خط یک لینک، آمادهٔ «Import config from clipboard») | ✅ | منوی سه‌نقطه → «کپی همهٔ لینک‌های v2ray» |
| **مرتب‌سازی فهرست**: الفبا، پینگ، قیمت، شناسه — هر کدام صعودی/نزولی (ردیف‌های بدون پینگ همیشه آخر) | ✅ | دکمهٔ مرتب‌سازی کنار نوار خلاصه |
| **نصب کنار اپ اصلی** (`applicationId = co.asiven.vixentvpn.trial`) با همان امضا و همان هدر `app_name` | ✅ | `app/build.gradle.kts` + `BuildConfig.HEADER_APP_NAME` |
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

### 🔓 رمز `value` حل شد — اپ خودش وصل می‌شود

در این بک‌اند فیلد `value` هر ردیف base64 از یک blob رمزشده است. قاعده‌اش کشف و روی دادهٔ زنده
تأیید شد:

| مؤلفه | مقدار |
| --- | --- |
| الگوریتم | `AES/CBC/PKCS5Padding` |
| کلید | `"key_<id>"` (همان `id` ردیف، حتی منفی مثل `key_-16068`) + بایت `0x00` تا ۱۶ بایت |
| IV | برابر کلید |
| خروجی | لینک `vless`/`vmess`/`trojan`/`ss` یا JSON کامل Xray |

* پیاده‌سازی: `app/src/main/java/co/asiven/vixentvpn/trial/core/PayloadCipher.kt`
* اجرای واقعی در CI روی پاسخ زنده: **۱۰۵ از ۱۰۵ ردیف** باز شد
  (۹۸ `vless`، ۱ `trojan`، ۶ JSON) — شاهد: `android-app/docs/probe-rows/decrypt-coverage.txt`
* کشف از کد عمومی پنل مدیریت همین خانوادهٔ سرویس (`vefghmhassan/vpn-pannel` →
  `internal/utils/tools.go` → `DecryptValue`) و سپس آزمون روی دادهٔ واقعی؛ مسیرهایی که به
  بن‌بست رسیدند (کلید در APK نیست، هیچ اندپوینتی متن‌باز برنمی‌گرداند، `version_code` بی‌اثر است)
  در `android-app/docs/value-decrypt-fa.md` مستند شده‌اند.
* ابطال یک فرض قبلی: `value` در هر درخواست عوض **نمی‌شود**؛ فقط ترتیب ردیف‌ها جابه‌جا می‌شود.

نتیجه:

* فهرست کامل ۱۰۵ سرور + برچسب‌ها + پینگ + انتخاب + اتصال، همه بدون دخالت کاربر؛
* بعد از «پینگ همه»، سریع‌ترین سروری که پاسخ داده **خودکار انتخاب** می‌شود؛
* ردیفی که پروتکلش را هستهٔ Xray اجرا نمی‌کند (مثلاً `hysteria`) با پیام صریح رد می‌شود،
  نه با وانمود کردن به اتصال؛
* مسیرهای اختیاری (کلیپ‌بورد، لینک `sub`، کپی لینک v2ray هر ردیف) هم سر جای خودشان هستند.

### 🔌 اتصال واقعی، واقعاً آزمایش شد (نه فقط اسکرین‌شات)

ورک‌فلوی `connect-test` یک **سرور واقعی Xray** روی runner بالا می‌آورد (VLESS/TCP روی
`10086` و VMess/WS روی `10087`)، اپ را روی شبیه‌ساز نصب می‌کند، کانفیگ را با intent وارد
می‌کند (`vless://…`)، «اتصال» را می‌زند، مجوز VPN را تأیید می‌کند و بعد **ترافیک را از داخل
TUN به بیرون می‌فرستد و ردِ آن را در لاگ access سرور Xray** می‌بیند. نتیجهٔ اجرای
[`40275697024`](https://github.com/animalrender/Myvpn/actions/runs/40275697024) — همهٔ گام‌ها ✅:

| گام | نتیجه |
| --- | --- |
| ورود کانفیگ با intent (`vless://`) | ✅ ردیف «CI-Local-A» اضافه شد |
| اتصال + مجوز VPN + وضعیت «متصل — CI-Local-A (VPN)» | ✅ |
| ساخت `tun0` | ✅ |
| عبور ترافیک (HTTPS و HTTP) | ✅ `204` + `accepted tcp:www.gstatic.com:443` در لاگ سرور |
| «پینگ همه» در حال اتصال | ✅ سرور عوض نشد (نقص اپ اصلی تکرار نشد) |
| تغییر سرور در حال اتصال → VMess/WS | ✅ «متصل — CI-Local-B» و ترافیک ادامه‌دار |
| «قطع اتصال» | ✅ `tun0` حذف شد |

گزارش کامل: [`android-app/docs/connect-test/CONNECT.md`](connect-test/CONNECT.md) + ۸ تصویر + لاگ‌ها.

این آزمون دو نقص واقعی را پیدا کرد که در همین PR اصلاح شده‌اند:

1. **اتصال هرگز شروع نمی‌شد**: `VpnTunnelService` کانفیگ را از `Server.rawJson` می‌خواند،
   ولی برای ردیف‌های واردشده این فیلد همان لینک `vless://` است نه JSON ← سرویس با پیام
   «سروری برای اتصال ارسال نشده است» بلافاصله بسته می‌شد. حالا کانفیگ خام + نام سرور جدا
   پاس داده می‌شود.
2. **از دست رفتن وضعیت اتصال** وقتی اپ با یک لینک تازه باز می‌شد (نمونهٔ دوم Activity):
   دکمه دوباره «اتصال» می‌شد و قطع/وصل می‌کرد. وضعیت تونل اکنون در `Prefs` آینه می‌شود و
   دکمه هنگام انتخاب سرور دیگر به «اتصال به سرور انتخابی» تغییر می‌کند (تغییر سرور با یک لمس).

### 🧭 آزمون «صفر ورودی کاربر» روی بک‌اند واقعی (`e2e-real`)

ورک‌فلوی `e2e-real` دقیقاً همان کاری را می‌کند که کاربر می‌کند — و هیچ چیز اضافه‌ای به اپ نمی‌دهد:

| گام | سنجه |
| --- | --- |
| `pm clear` + باز کردن اپ | دادهٔ قبلی پاک شده؛ پس هر چیزی که می‌آید تازه از بک‌اند است |
| دریافت فهرست | ۱۰۵ ردیف بدون هیچ ورودی |
| «پینگ همه» | تعداد ردیف‌های پاسخ‌داده و سریع‌ترین ردیف |
| اتصال | `متصل — <نام سرور>` + وجود `tun0` |
| عبور ترافیک | `204` از داخل تونل و **تغییر IP خروج** نسبت به قبل از اتصال |
| تغییر سرور | اتصال به ردیف دوم و تکرار سنجهٔ ترافیک |
| قطع اتصال | حذف `tun0` |

نتیجهٔ اجرا، همراه با تصاویر و لاگ‌کت، در `android-app/docs/e2e-real/CONNECT-REAL.md` کامیت می‌شود.

### 🤖 تأییدهای خودکار CI روی همین APK

* وجود `lib/<abi>/libgojni.so` (هستهٔ Xray) و `lib/<abi>/libhev-socks5-tunnel.so` (tun2socks) برای
  **هر دو معماری** و رد شدن هر ABI اضافی در APK
* `apksigner verify --print-certs` ⇒ گواهی AOSP testkey مطابق نسخهٔ اصلی
* `aapt2 dump badging` ⇒ `package=co.asiven.vixentvpn`، `versionCode=1004220`،
  `native-code=arm64-v8a` یا `x86_64`
* اجرای پروب‌های واقعی API (ورک‌فلوی `probe-api`) و انتشار همهٔ نتایج به‌صورت annotation

### 🖼️ رابط کاربری، واقعاً دیده و آزمایش شده

ورک‌فلوی `ui-snapshot` نسخهٔ `x86_64` را با همان کلید امضا می‌سازد، شبیه‌ساز Android 14
(۱۰۸۰×۲۲۸۰، KVM) را بالا می‌آورد، اپ را نصب و با `tools/ui-drive.py` کنترل می‌کند و از هر مرحله
اسکرین‌شات می‌گیرد. اجرای آخر (run 12) **بدون هیچ خطا** تمام شد (`FAILURES: none`،
`crash-check: pid=yes, fatal lines=0`) و ۱۱ تصویر در [`android-app/docs/screenshots`](
screenshots/) کامیت شد:

`01-home` · `02-list-loaded` · `03-single-ping` · `04-ping-all` · `05-server-sheet` ·
`06-filter-paid` · `07-search` · `08-menu` · `09-scrolled` · `10-scrolled-more`

آنچه در همین اجرا داخل شبیه‌ساز تأیید شد: ورود اپ، دریافت **۱۰۵ سرور** از `/api/protocols`
(۲۰۰، ۷۷–۱۰۴ کیلوبایت)، رندر برچسب‌ها، باز شدن bottom sheet، فیلتر و جست‌وجو
(تایپ «Finland»)، منوی «بیشتر» و اسکرول. خطاها و اصلاح‌های همین مسیر هم ثبت شده‌اند:
اندازهٔ صفحهٔ شبیه‌ساز، از دست رفتن foreground، تپ روی متن بنر به‌جای چیپ، و نمایش «—» برای
برچسب‌های خالی.

نکتهٔ عمدی: در این بک‌اند همهٔ ۱۰۵ سرور `price = 0` هستند، پس فیلتر «پولی» عمداً **خالی** است و
همین را هم پیام «با این فیلتر سروری پیدا نشد» می‌گوید.

### 🔍 بازآزمایی `base.apk` (۲۰۲۶-۱۰-۲۶)

APK اصلی دوباره از گوگل‌درایو دانلود و با REA/androguard بازآزمایی شد. گزارش کامل:
[`android-app/docs/re-analysis-fa.md`](re-analysis-fa.md). خلاصه:

* سه لایه محافظت: **ApkDex2C 3.1.14**، رمزنگاری رشته‌ها با **ScKit** (۵۷٬۶۸۶ رشته از ۱۲۰٬۰۷۲)،
  و **`libstub.so`** که فقط `JNI_OnLoad` را export می‌کند (ثبت پویا) + `ApkSignatureKillerEx`.
* `value` سرورها: base64 با آنتروپی ۷٫۹۳ — **۶۵۶٬۷۵۰ ترکیب کلید** (رشته‌های dex، هدرها،
  `configKey/routeKey/endpointKey`، معماهای بسته) روی AES-ECB/CBC آزمایش شد و خروجی معناداری
  نداد.
* `geoip.dat`/`geosite.dat` در APK اصلی هم وجود ندارد و نسخهٔ آزمایشی به آن‌ها ارجاع نمی‌دهد.
* «پینگ همه → مکث → پریدن به سرور دیگر» در اپ اصلی از انتخاب خودکار «بهترین سرور» می‌آید؛ در
  نسخهٔ آزمایشی چنین منطقی وجود ندارد و در CI هم سنجیده می‌شود.

### 🔑 استخراج کلیدها و بازکردن هر سه لایهٔ محافظت (۲۰۲۶-۱۰-۲۶)

* **قاعدهٔ رمزنگاری رشته‌ها (ScKit) حل شد:** `AES/ECB/PKCS5`، کلید = `lower(MD5(passphrase))[8:24]`
  و `passphrase` همان رشتهٔ `ScKit-<hex>` **با پیشوند**. هر ۴۶٬۶۹۰ نقطهٔ فراخوانی در سه dex و
  ۳۳۷ رشته در `libstub.so` با ۰ خطا رمزگشایی شد.
* **کلید آدرس API:** روتین `Lz/d;->v` = `AES/CBC/PKCS5` با **کلید و IV = نام بسته**
  (`co.asiven.vixentvpn`)؛ نتیجه: `https://managev1.xyz`.
* **نقشهٔ کامل کد بومی:** جدول محافظت `ApkDex2C`/`np/dcc/protect/EntryPoint` در `0xcf818`
  خوانده شد ⇒ **۱۵ کلاس / ۲۵۸ متد** با نام، امضا و آدرس (`android-app/docs/native-map.json`).
* **کلید `value` داخل بسته نیست — چون کلید ثابت نیست:** متد بومی
  `MainActivity.importBatchConfig` مقدار `value` را دست‌نخورده به `AngConfigManager` می‌دهد و
  `Protocol.getValue` فقط یک خواندن فیلد است؛ یعنی خود APK هم رمزگشایی را جای دیگری (سمت پنل)
  انجام می‌دهد. کلید از `id` ردیف ساخته می‌شود و همین در `PayloadCipher` پیاده شد ⇒
  **۱۰۵/۱۰۵ ردیف باز می‌شوند**. جزئیات: `value-decrypt-fa.md` و `re-analysis-fa.md` بخش ۸.
* ابزار بازتولید: `tools/apk-keys.py`، `tools/dcc-native-map.py`، `tools/probe-rows.py`
  (+ ورک‌فلوی `probe-rows.yml`) و شواهد خام در `android-app/docs/probe-rows/`.

### 📚 مستندات فارسی داخل پروژه

* `android-app/docs/README-fa.md` — معرفی، نصب، قابلیت‌ها، وضعیت رمزنگاری `value`، وضعیت Firebase، عیب‌یابی
* `android-app/docs/value-decrypt-fa.md` — قاعدهٔ باز کردن `value` + شواهد ۱۰۵/۱۰۵
* `android-app/docs/api-contract-fa.md` — قرارداد کامل API و هدرها
* `android-app/docs/architecture-fa.md` — معماری، TUN/hev، کانفیگ Xray، بازسازی لینک اشتراک
* `android-app/docs/re-analysis-fa.md` — بازآزمایی `base.apk` و جدول تفاوت‌ها با نسخهٔ آزمایشی
* `android-app/docs/connect-test/CONNECT.md` — گزارش آزمون اتصال واقعی (تولیدشده در CI)
* `android-app/docs/e2e-real/CONNECT-REAL.md` — گزارش آزمون بدون ورودی کاربر روی بک‌اند واقعی
* `docs/apk-vixentvpn-analysis-fa.md` — تحلیل کامل APK اصلی

### 🧪 پیشنهاد تست برای شما

1. نصب APK از ریلیز `trial-9` (روی شبیه‌ساز: فایل `x86_64`).
2. زدن «دریافت و بازآوری همهٔ سرورها» ← باید ۱۰۵ سرور با برچسب‌ها بیاید.
3. «پینگ همه» و «لینک v2ray» یک ردیف را امتحان کنید.
4. «پینگ همه» ← سریع‌ترین سرور خودکار انتخاب می‌شود؛ «اتصال» را بزنید و مجوز VPN را تأیید کنید.
   برای عوض کردن سرور در حال اتصال، سرور دیگر را انتخاب کنید؛ دکمه به «اتصال به سرور انتخابی»
   تغییر می‌کند. (مسیرهای دستی هم هستند اگر خواستید: لمس یک لینک `vless://`/`vmess://` در
   مرورگر، یا «افزودن کانفیگ از کلیپ‌بورد».)
5. اگر جایی خطا دید: منوی «لاگ‌ها» و «JSON خام» خروجی دقیق می‌دهد (بدون نیاز به `adb logcat`).
