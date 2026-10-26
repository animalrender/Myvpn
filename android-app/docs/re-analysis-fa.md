# باز‌تحلیل `base.apk` و مقایسهٔ آن با نسخهٔ آزمایشی

این سند نتیجهٔ بازآزمایی APK اصلی (همان فایلی که از گوگل‌درایو دوباره دانلود شد) با ابزارهای
REA و androguard است و تفاوت‌های آن را با نسخهٔ آزمایشی (`MVPN Trial`) فهرست می‌کند.

- فایل بررسی‌شده: `base.apk` — ۳۸٫۵۵۹٫۷۶۷ بایت، شناسهٔ درایو `1V688P9EDDI7MX9nOewV2Uw4L9HjePtDo`
- ابزارها: `rea-agents 6.8.0`، `androguard 4.1.4`، `pycryptodome`
- تاریخ بازآزمایی: ۲۰۲۶-۱۰-۲۶

---

## ۱) هویت بسته

| ویژگی | `base.apk` | نسخهٔ آزمایشی |
| --- | --- | --- |
| `applicationId` | `co.asiven.vixentvpn` | `co.asiven.vixentvpn` (یکسان) |
| نسخه | `3.2.0` / `versionCode 1004220` | `3.2.0-trial` / `versionCode 1004220` (یکسان) |
| Activity شروع | `co.dev.ui.WelcomeActivity` | `…trial.ui.MainActivity` (یک صفحه، بدون معرفی) |
| `minSdk` / `targetSdk` | ۲۱ / ۳۴ | ۲۴ / ۳۵ |
| معماری‌های داخل APK | `arm64-v8a`, `armeabi-v7a` | `arm64-v8a` و `x86_64` (دو APK جدا) |
| امضا | AOSP testkey (`a40da80a…71bf5dc`) | همان کلید (هدر `sign` یکسان) |
| تعداد کلاس‌ها (dex) | ۲۱٫۰۷۹ | فقط کلاس‌های لازم برای همین صفحه |

اختلاف `minSdk` عمدی است: `minSdk 24` حداقل نسخهٔ پشتیبانی‌شدهٔ `libv2ray` و
`hev-socks5-tunnel` است و پایین‌تر بردن آن بدون تست روی اندروید ۵ تا ۶ ریسک شکست هستهٔ Xray را
دارد. `targetSdk 35` هم لازمهٔ نصب و اجرا در اندروید ۱۵ است؛ در غیر این صورت سرویس VPN
محدود می‌شود. هیچ‌کدام روی هدرهای API اثر ندارند (هدرها از `applicationId`، `versionCode` و
امضا ساخته می‌شوند).

## ۲) محافظت کد (سه لایه)

۱. **ApkDex2C 3.1.14** (محصول NP Manager): متدهای حساس به کد بومی منتقل شده‌اند. فهرست
   متدهای بومی شامل همهٔ getter/setterهای `co.dev.models.*`، دروازهٔ پرمیوم
   `Li4/c;->a(ServerConfig, Lco/dev/ui/e;)Z`، و بخش‌هایی از `com.v2ray.ang.ui.MainActivity`,
   `BaseActivity`, `libv2ray.*`, `V2RayVPNServiceSupportsSet.*` و
   `co.nevisa.commonlib.{admob,fairbid}.*` است.
۲. **رمزنگاری رشته‌ها «ScKit»** — **حل شد** (جزئیات و اثبات در بخش ۸): هر رشتهٔ متنی dex
   به‌صورت `ScKit-<hex>` ذخیره شده و با `AES/ECB/PKCS5Padding`، کلید
   `lower(MD5(passphrase))[8:24]` و همان `passphrase`ی که در کنارش آمده باز می‌شود.
   همهٔ **۴۶٫۶۹۰** نقطهٔ فراخوانی (`classes.dex` ۲۰٫۸۳۱ + `classes2.dex` ۱۹٫۶۹۳ +
   `classes3.dex` ۶٫۱۶۶) با **۰ خطا** رمزگشایی شد و ۴۴٫۳۹۶ رشتهٔ یکتا به‌دست آمد؛
   همین کار برای `libstub.so` هم انجام شد (۳۳۷ از ۳۷۸ رشته، ۲۶۶ یکتا).
۳. **`libstub.so`** — **نگاشت کامل بومی به‌دست آمد** (بخش ۸): جدول محافظت NetEase DCC
   (`np/dcc/protect/EntryPoint`) در `0xcf818` نشسته و پس از اعمال 「relocation」های
   `R_AARCH64_RELATIVE` خوانا می‌شود: **۱۵ کلاس / ۲۵۸ متد بومی** با نام، امضا و آدرس کد
   (مثلاً `MainActivity.importBatchConfig` در `0x4f150`). یک `ApkSignatureKillerEx` هم در بسته
   هست که بررسی امضای خودی را دور می‌زند.

**نتیجه (اصلاح‌شده):** فرض قبلی «کلید داخل کد بومی ساخته می‌شود» **رد شد**. کلید رمزگشایی
`value` **در هیچ نسخه‌ای از این APK وجود ندارد** — نه در dex، نه در `libstub.so`
(کتابخانه **هیچ** ابتدایی رمزنگاری ندارد: نه S-box ای‌ای‌اس، نه جدول MD5/SHA، نه ارجاع به
`javax/crypto`). سرویس‌دهنده `value` را با کلیدی می‌فرستد که فقط کلاینت نسل بعدی آن را دارد.
بنابراین نسخهٔ آزمایشی همهٔ ۱۰۵ سرور را **کامل** فهرست و برچسب‌گذاری می‌کند، برای هر ردیف لینک
اشتراک v2ray می‌سازد/کپی می‌کند و اتصال را با کانفیگ واقعی (لینک اشتراک، کلیپ‌بورد یا
`vless://`/`vmess://`) با همان هستهٔ Xray انجام می‌دهد.

## ۳) payload سرورها

- `GET /api/protocols` و `GET /api/v2/protocols` هر دو ۲۰۰ و ۱۰۵ ردیف می‌دهند؛
  `/api/v2/protocols` سه فیلد تازه هم دارد: `configKey`, `routeKey`, `endpointKey` —
  **هگز تصادفیِ هر پاسخ** (در دو اندازهٔ مشاهده‌شده: ۶۴ و ۳۰ کاراکتر، یعنی ۳۲ و ۱۵ بایت)،
  نه مقدار ثابت و نه هش کانفیگ.
- `value` = base64 با طول متغیر؛ اندازه‌اش همیشه مضرب ۱۶ است (نمونهٔ امروز: ۱۲۸ بایت برای
  سوئد، ۳٫۳۶۰ بایت برای بریتانیا). **هر بار که درخواست تکرار می‌شود مقدار عوض می‌شود** (بخش ۸).
- هیچ مسیری در API کانفیگ آماده نمی‌دهد: `/api/configs|config|connect|decode|proxy|endpoint/*|route/*`
  همه ۴۰۴ هستند، `/api/token` پاسخ `app token is disabled` می‌دهد، `/api/setting` برابر `data:null` است.
- `value` بدون امضای درست هم پذیرفته نمی‌شود؛ هدر `sign` = `Base64(MD5(certDER))` است
  (`6JsVjkvPmI69CeuD9TeOhw==`).

## ۴) هستهٔ شبکه

| مورد | `base.apk` | نسخهٔ آزمایشی |
| --- | --- | --- |
| هستهٔ Xray | `libgojni.so` (gomobile، Xray-core v26.10.21) | `libv2ray.aar` از AndroidLibXrayLite v26.10.21 |
| تونل TUN→SOCKS | `libtun2socks.so` + `hev` | `libhev-socks5-tunnel.so` 2.19.3 (ndk-build) |
| پورت‌های محلی | SOCKS 10808 / HTTP 10809 | همان |
| TUN | `10.10.10.2/24`, MTU 1500, DNS `1.1.1.1`/`8.8.8.8` | همان |
| `geoip.dat` / `geosite.dat` | **در بستهٔ APK نیست** | لازم نیست: قواعد مسیریابی نسخهٔ آزمایشی فقط IP خصوصی را `direct` می‌کند و به `geoip:`/`geosite:` ارجاع نمی‌دهد |
| Firebase | `vixent-5ac3f` / `834191356570` | همان پروژه و همان `google-services.json` |
| تبلیغ | AdMob + FairBid (`co.nevisa.commonlib`) | حذف‌شده |

## ۵) رفتار «پینگ همه → مکث → اتصال به سرور دیگر»

در APK اصلی، «پینگ همه» فقط اندازه‌گیری تأخیر نیست: پس از پایان پینگ، بهترین سرور
جایگزین انتخاب فعلی می‌شود و اگر اتصال برقرار باشد هسته دوباره راه‌اندازی می‌شود؛ همین
مکث و جابه‌جایی سرور، رفتاری است که در نسخهٔ اصلی دیده می‌شود.

نسخهٔ آزمایشی **هیچ‌گاه** به‌طور خودکار سرور را عوض نمی‌کند:

- `pingAll()` فقط `pingMs`/`pingState` هر ردیف را به‌روز می‌کند و به `prefs.selectedKey` دست نمی‌زند؛
- تونل فقط با زدن دکمهٔ «اتصال» یا انتخاب صریح کاربر شروع/متوقف می‌شود؛
- این رفتار در ورک‌فلوی `connect-test` به‌صورت خودکار سنجیده می‌شود: پس از اتصال، «پینگ همه»
  اجرا می‌شود و متن وضعیت باید همان `متصل — CI-Local` بماند.

## ۶) تفاوت‌های عمدی نسخهٔ آزمایشی

| مورد | دلیل |
| --- | --- |
| حذف تبلیغ (AdMob/FairBid) و دروازهٔ پرمیوم | خواستهٔ کارفرما؛ سرورهای پولی همچنان با برچسب نمایش داده می‌شوند |
| حذف ورود/حساب کاربری و منطق سکه (`price`) | خواستهٔ کارفرما؛ مقدار `price` فقط به‌عنوان برچسب نمایش داده می‌شود |
| صفحهٔ تک‌صفحه‌ای بازطراحی‌شده (به‌جای Welcome + تبلیغ + منو) | خواستهٔ کارفرما: UI بازطراحی شود |
| دو خروجی `arm64-v8a` و `x86_64` | درخواست: نسخهٔ `x86_64` هم منتشر شود |
| بدون `ApkSignatureKillerEx` | امضای خودمان با همان AOSP testkey ساخته می‌شود، پس دور زدن بررسی امضا لازم نیست |
| بدون `libstub.so` / رشته‌های ScKit | کد محافظت‌شده لازم نیست؛ کد ما باز و قابل بازبینی است |

## ۷) آنچه با نسخهٔ اصلی یکسان است

- `applicationId`، `versionCode`، امضا و در نتیجه **همهٔ هدرهای API** (`sign`, `sha_hexadecimal`,
  `app_name`, `version_code`, `seen`)
- آدرس پایهٔ API (`https://managev1.xyz`)، مسیرهای `/api/protocols` و `/api/v2/protocols`
- فهرست ۱۰۵ سرور، نام‌ها، پرچم‌ها، `price`/`usage` و همهٔ فیلدهای ناشناختهٔ دیگر
- پشتهٔ هسته: Xray-core v26.10.21 + hev tun2socks + همان پورت‌ها و پارامترهای TUN
- Firebase (`firebase_token` و همان پروژه)
- قالب لینک اشتراک v2ray برای هر سرور (سازگار با v2rayNG/Streisand)

## ۸) کلیدها و رمزنگاری — استخراج کامل (بازآزمایی ۲۰۲۶-۱۰-۲۶)

### ۸-۱) قاعدهٔ رمزنگاری رشته‌ها (ScKit) — حل شد

| مورد | مقدار |
| --- | --- |
| الگوریتم | `AES/ECB/PKCS5Padding` (بلوک ۱۶ بایتی، `Cipher.getInstance("AES")`) |
| عبارت عبور | آرگومان دوم همان‌طور که نوشته شده، **با پیشوند** `ScKit-` |
| کلید AES | `encodePass(passphrase)` = `lower(MD5(passphrase))[8:24]` (۱۶ کاراکتر ASCII) |
| متن رمزشده | آرگومان اول بدون پیشوند `ScKit-`، به‌صورت هگز |
| تأیید | `ScKit-4c24019abf6ca137fa83af683f558bb9` + `ScKit-fa103df02f265218` → `"Serializing "` |

> نکتهٔ مهم: اگر `ScKit-` از عبارت عبور حذف شود، خروجی بی‌معنا می‌شود؛ پیشوند **بخشی از کلید** است.

بازتولید:

```bash
pip install pycryptodome androguard
python3 android-app/tools/apk-keys.py --apk-dir /tmp/apk --dump /tmp/sckit.tsv
# classes.dex: 20831 call sites, 20831 decrypted, 0 not ScKit
# classes2.dex: 19693 … / classes3.dex: 6166 …
# total call sites: 46690, unique plaintexts: 44396
```

### ۸-۲) قاعدهٔ رمزنگاری «آدرس/کانفیگ» (`Lz/d;->v`) — حل شد

| مورد | مقدار |
| --- | --- |
| الگوریتم | `AES/CBC/PKCS5Padding`، ورودی `Base64.decode(src, 1)` |
| کلید **و** IV | ۱۶ بایت اول آرگومان دوم (با صفر پر می‌شود) |
| تنها فراخوان در کد فروشنده | `Lk4/d;->f(String)` که **نام بسته** را می‌فرستد |
| نتیجه | `co.asiven.vixentvpn` + `tyBT242ubuxXa/YbRfrkGQVlNflSzufT6Q7TJTa5t0M=` → `https://managev1.xyz` |

یعنی «کلید مخفی» آدرس API چیزی جز **نام بستهٔ خود اپ** نیست؛ همان روتین با امضای
`Ll3/a;->m(String, String)` یک نسخهٔ دیگر هم دارد. با این کلید، آدرس پایه بدون هیچ حدسی
بازسازی می‌شود و همین آدرس در نسخهٔ آزمایشی استفاده شده است.

### ۸-۳) نقشهٔ کامل متدهای بومی (`libstub.so`) — برای اولین بار

بستهٔ محافظ `ApkDex2C 3.1.14` متدها را `native` می‌کند و پیاده‌سازی‌ها را با جدولی که به
`np/dcc/protect/EntryPoint` داده می‌شود ثبت می‌کند. جدول در `0xcf818` است و فقط باید
«relocation»های `R_AARCH64_RELATIVE` روی `.data.rel.ro` اعمال شود تا خوانا شود:

```
{b"stub", "(I)V", <trampoline>}
{class_name, methods*, count}        ← رکورد ۲۴ بایتی
methods[i] = {name, signature, code} ← رکورد ۲۴ بایتی
```

خروجی کامل: `android-app/docs/native-map.json` (**۱۵ کلاس / ۲۵۸ متد**).

```bash
python3 android-app/tools/dcc-native-map.py /tmp/apk/lib/arm64-v8a/libstub.so --json > native-map.json
python3 android-app/tools/dcc-native-map.py …/libstub.so --class com/v2ray/ang/ui/MainActivity
```

کلاس‌های بومی: `co/dev/models/Social` (۱۴)، `co/nevisa/commonlib/admob/c` (۹)،
`co/nevisa/commonlib/fairbid/c` (۵)، `com/CustomDialogClass` (+۲ لامبدا)، `com/WebService` (۳)،
`com/v2ray/ang/service/V2RayServiceManager` (۲۲)، `com/v2ray/ang/ui/BaseActivity` (۱۳)،
`com/v2ray/ang/ui/MainActivity` (**۱۴۹**)، `com/v2ray/ang/ui/MainActivity$initConnectionTimer$1` (۲)،
`com/v2ray/ang/ui/j`، `h/n0` (۱۷)، `h/o` (۵)، `nd/h` (۱۵).

### ۸-۴) اثبات اینکه `value` با این APK رمزگشایی نمی‌شود

۱. **مسیر داده در کد بومی**: `MainActivity.importBatchConfig(String,String,Protocol,Z)`
   (آدرس `0x4f150`) دقیقاً همان منطق کاتلین را بازنویسی می‌کند: `value` **بدون تغییر** به
   `AngConfigManager.importBatchConfig(name, value, isSub, protocol)` و سپس به
   `appendCustomConfigServer(name, value, protocol)` می‌رود.
۲. **شرط پذیرش**: `appendCustomConfigServer` با رشته‌های رمزگشایی‌شدهٔ ScKit بررسی می‌کند که
   مقدار شامل `inbounds` / `outbounds` / `routing` باشد (یعنی JSON خام کانفیگ)؛ مقدار رمزشده
   هرگز از این دروازه رد نمی‌شود.
۳. **بدون رمزنگاری در کد بومی**: در `libstub.so` هیچ S-box ای‌ای‌اس، هیچ جدول MD5/SHA و هیچ
   ارجاعی به `javax/crypto`/`java/security`/`Base64` وجود ندارد.
۴. **بدون مسیر دیگر در dex**: تنها نقاط `Cipher.getInstance` در کل بسته عبارت‌اند از
   ScKit (دو متد `decode`/`encode`)، `Lz/d;->v`/`Ll3/a;->m` (آدرس/کانفیگ، بخش ۸-۲) و
   کلاس‌های داخلی Firebase؛ هیچ‌کدام به `value` دست نمی‌زنند. مسیر `value` فقط از
   `Config`/`Protocol` (POJO خالص) می‌گذرد.
۵. **رفتار زندهٔ سرور**: `value` **در هر درخواست تغییر می‌کند** و `configKey`/`routeKey`/`endpointKey`
   هم هر بار تصادفی و با طول متغیر برمی‌گردند؛ پس کلید جلسه سمت سرور ساخته می‌شود و کلاینت باید
   نسل بعدی باشد. آزمون ۹ حالت هدر (بدون امضا، امضای غلط، `seen=1`، بدون `app_name`،
   نسخهٔ قدیمی، هدرهای telemetry، `Accept-Encoding: identity`) هیچ‌کدام `value` را به لینک/JSON
   تبدیل نکرد؛ فقط حالت «بدون امضا» فهرست را **خالی** می‌کند (۱۰۵ ردیف → ۰).
   شواهد خام: `android-app/docs/probe-rows/variants.json` + `v1.json` + `v2.json`.
۶. **آزمون کلیدها**: بیش از ۱٫۶۰۰ تلاش *قطعی* (نه حدس) روی نمونه‌های واقعی انجام شد:
   AES-CBC/ECB/CFB/OFB/CTR/GCM و ChaCha20، با کلیدهای داخل APK (نام بسته، کلیدهای ScKit) و
   کلیدهای همان پاسخ (`configKey`/`routeKey`/`endpointKey` در دو شکل هگز و ASCII) و ترکیب‌های
   XOR/SHA-256، همراه با بازکردن gzip/deflate — **صفر نتیجه**.

### ۸-۵) نتیجه‌گیری

- کلیدهای موجود در `base.apk` **کامل استخراج شدند**: کلید رشته‌ها (`ScKit-…` + قاعدهٔ
  MD5[8:24])، کلید آدرس API (نام بسته، AES-CBC با key=IV) و کلید امضا
  (`Base64(MD5(certDER))` → `6JsVjkvPmI69CeuD9TeOhw==`).
- کلید رمزگشایی فیلد `value` **در این بسته نیست**؛ نه در dex و نه در کد بومی. بنابراین
  **نسخهٔ اصلی هم با همین فید نمی‌تواند متصل شود** — که با رفتار مشاهده‌شده
  («پینگ همه → هیچ‌کدام وصل نمی‌شود → مکث») و با پیام خود فروشنده («این نسخه از کار افتاده»)
  هم‌خوان است؛ ضمناً فایل اشتراک داخلی اپ
  (`raw.githubusercontent.com/1401vpnclick/Vixen-VPN-2.9.3/…/3.2.0 .txt`) فقط یک نقطه («.») است.
- کاری که نسخهٔ آزمایشی انجام می‌دهد، سقف امکان‌پذیر با این APK است: نمایش کامل ۱۰۵ سرور با
  برچسب‌ها، ساخت/کپی لینک اشتراک هر ردیف، و اتصال واقعی با کانفیگ معتبر (که در CI با
  سرور واقعی Xray و عبور ترافیک از تونل اثبات شده است).
