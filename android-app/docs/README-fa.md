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

> Firebase طبق اپ اصلی اضافه شده است: `google-services.json` پروژهٔ همان اپ در
> `android-app/app/google-services.json` قرار دارد، توکن FCM گرفته و ذخیره می‌شود و به‌عنوان
> `firebase_token` در درخواست `/api/token` فرستاده می‌شود (بخش
> [«وضعیت Firebase»](#۷-وضعیت-firebase)).

---

## ۱) نصب و اجرای سریع

1. از صفحهٔ [Releases](https://github.com/animalrender/Myvpn/releases) آخرین نسخه
   (`trial-<شمارهٔ اجرا>`، همیشه بالاترین شماره در بالای صفحه) را دانلود کنید. هر انتشار
   **دو APK** دارد (به همراه فایل‌های `.sha256`):

   | فایل | معماری | برای |
   | --- | --- | --- |
   | `mvpn-trial-arm64-*.apk` | `arm64-v8a` | گوشی/تبلت اندرویدی |
   | `mvpn-trial-x86_64-*.apk` | `x86_64` | شبیه‌ساز اندروید (AVD)، کروم‌بوک |

   ```bash
   gh release list                                   # فهرست نسخه‌ها
   gh release download trial-<N>                      # دانلود هر دو APK + sha256
   ```
2. روی گوشی اندروید ۷ (API 24) به بالا و **arm64-v8a** نصب کنید (روی شبیه‌ساز، فایل
   `x86_64` را نصب کنید):
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

- **بدون هیچ ورودی از کاربر**: فهرست از بک‌اند می‌آید، `value` هر ردیف در خود دستگاه باز
  می‌شود (`AES/CBC` با کلید `key_<id>`) و اتصال با همان هستهٔ Xray برقرار می‌شود — دقیقاً مثل اپ
  اصلی، نه با گرفتن لینک/کانفیگ از کاربر.
- **یک دکمه برای دریافت و بازآوری همهٔ سرورها** (توکن + تنظیمات + فهرست، با همان ترتیب و همان
  هدرهای اپ اصلی).
- **رابط کاربری بازطراحی‌شده** (Material 3، تیره، RTL):
  - کارت بالای صفحه: نقطهٔ وضعیت، حالت اتصال (`VPN`/`پروکسی`)، نام سرور انتخاب‌شده با برچسب‌های
    نوع/قیمت/موقعیت/پینگ و **یک دکمهٔ اتصال/قطع**.
  - نوار جست‌وجو (نام، کشور، نوع، `id`) و **چیپ‌های فیلتر**: همه / رایگان / پولی / قابل‌اتصال.
  - ردیف‌های کارتی با برچسب نوع، قیمت، موقعیت، مصرف و پینگ رنگی (سبز/زرد/قرمز).
  - **Bottom sheet** برای هر سرور: اتصال، پینگ، کپی لینک v2ray، کپی JSON، جزئیات کامل.
- **لیست اسکرول‌شو** از همهٔ سرورها (رایگان **و** پولی، بدون هیچ قفلی)؛ هر ردیف برچسب‌های اصلی
  سرور را نشان می‌دهد:
  - پرچم/کشور (`name` + ایموجی پرچم داخل `name` یا فیلد `flag`)
  - **نوع/پروتکل** استخراج‌شده از کانفیگ باز‌شده، همراه با ترابری: `vless · ws`، `vless · reality`، `trojan · grpc` …
  - **قیمت اصلی** (`price`) با تفکیک «رایگان» و «پولی · n الماس»
  - **مصرف/سهمیه** (`usage`) و `id`/`serverId`
  - همهٔ کلیدهای ناشناختهٔ پاسخ هم در «جزئیات» و «JSON خام» قابل مشاهده‌اند
- **پینگ تک‌تک سرورها** (دکمهٔ `پینگ` روی هر ردیف) و **پینگ همه** (۴ درخواست هم‌زمان). بعد از
  «پینگ همه»، سریع‌ترین سروری که واقعاً پاسخ داده **خودکار انتخاب** می‌شود تا یک لمس برای اتصال
  کافی باشد.
  پینگ با `Libv2ray.measureOutboundDelay(config, testUrl)` انجام می‌شود؛ یعنی همان سنجش
  تأخیری که هستهٔ Xray برای اپ اصلی انجام می‌دهد، نه ICMP ساده.
- **انتخاب سرور/موقعیت** با لمس ردیف؛ انتخاب در حافظه ذخیره می‌شود.
- **کپی لینک v2ray هر سرور** (دکمهٔ «کپی لینک v2ray») تا همان سرور را در v2rayNG/nekobox هم
  اضافه کنید. خروجی: `vmess://`/`vless://`/`trojan://`/`ss://` بازسازی‌شده از کانفیگ.
- **افزودن اشتراک (لینک `sub`)** و **افزودن کانفیگ از کلیپ‌بورد** از منوی سه‌نقطه — مسیر
  کلاینت‌محور که مستقل از پاسخ بک‌اند کار می‌کند (پشتیبانی از base64 اشتراک و لینک‌های
  `vmess/vless/trojan/ss/socks/hysteria/hy2`).
- **پذیرش لینک اشتراک از سیستم** (مثل v2rayNG): لمس یک لینک `vless://`/`vmess://`/`trojan://`/
  `ss://` در مرورگر یا پیام‌رسان، یا «اشتراک‌گذاری» متن کانفیگ به این اپ، آن را مستقیم اضافه
  می‌کند. لینک `http(s)` هم به‌عنوان آدرس اشتراک دریافت می‌شود.
- **تغییر سرور بدون قطع دستی**: وقتی تونل بالاست و سرور دیگری انتخاب می‌کنید، دکمه به
  «اتصال به سرور انتخابی» تغییر می‌کند و همان یک لمس تونل را روی سرور تازه بالا می‌آورد
  (بدون نیاز به قطع و وصل دستی).
- **بدون جابه‌جایی خودکار سرور**: «پینگ همه» فقط تأخیرها را به‌روز می‌کند و سرور انتخاب‌شده یا
  اتصال فعلی را تغییر نمی‌دهد (رفتار ناخواستهٔ اپ اصلی اینجا وجود ندارد و در ورک‌فلوی
  `connect-test` هر بار سنجیده می‌شود).
- **تست API و هدرها** در منو: یک گزارش زنده از وضعیت هر اندپوینت، هدرهای امضا و توکن — برای
  عیب‌یابی همان خطای «Internal server error».
- **دو حالت اتصال**: `VPN` (TUN + hev) و `PROXY` (فقط SOCKS 10808 / HTTP 10809 روی localhost).
- **گزارش داخلی**: «JSON خام» آخرین پاسخ بک‌اند و «لاگ‌ها» (درخواست‌ها + هسته) برای عیب‌یابی.
- **بدون تبلیغ، بدون حساب، بدون دروازهٔ قیمت.**

### تصاویر واقعی از اجرای اپ

اسکرین‌شات‌ها با شبیه‌ساز اندروید (API 34، ۱۰۸۰×۲۲۸۰) در GitHub Actions گرفته می‌شوند
(ورک‌فلوی `ui-snapshot`) و در پوشهٔ [`screenshots/`](screenshots/) کامیت می‌شوند:

| فایل | چه چیزی را نشان می‌دهد |
| --- | --- |
| [`01-home`](screenshots/01-home.png) | صفحهٔ اصلی، کارت اتصال، دکمهٔ دریافت سرورها، جست‌وجو و فیلترها |
| [`02-list-loaded`](screenshots/02-list-loaded.png) | فهرست ۱۰۵ سرور با برچسب نوع/قیمت/مصرف |
| [`03-single-ping`](screenshots/03-single-ping.png) | پینگ تک‌سرور |
| [`04-ping-all`](screenshots/04-ping-all.png) | پینگ گروهی و شمارندهٔ پیشرفت |
| [`05-server-sheet`](screenshots/05-server-sheet.png) | Bottom sheet سرور: اتصال، پینگ، کپی لینک v2ray، کپی JSON، جزئیات |
| [`06-filter-paid`](screenshots/06-filter-paid.png) | فیلتر «پولی» |
| [`07-search`](screenshots/07-search.png) | جست‌وجوی «Finland» در فهرست |
| [`08-menu`](screenshots/08-menu.png) | منوی «بیشتر»: JSON خام، لاگ‌ها، افزودن کانفیگ/اشتراک، تست API |
| [`09-scrolled`](screenshots/09-scrolled.png) | اسکرول فهرست |

گزارش هر اجرا (`STEPS.txt`، لاگ اپ و لاگ شبیه‌ساز) هم در همان پوشه است.

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

تنها مسیر ساخت، ورک‌فلوی [`.github/workflows/build-apks.yml`](../../.github/workflows/build-apks.yml) است
(ماتریس دو معماری، یک انتشار برای هر دو):

```bash
gh workflow run build-apks.yml
gh run watch
gh release list                     # تگ: trial-<شمارهٔ اجرا>
```

ورک‌فلو در همان runner:

1. `tools/fetch-libv2ray.sh` — دانلود `libv2ray.aar` از [AndroidLibXrayLite](https://github.com/2dust/AndroidLibXrayLite)
   (آخرین ریلیز `v26.10.21`) و قرار دادن آن در `app/libs/`.
2. `tools/build-hevtun.sh` — clone کردن [hev-socks5-tunnel](https://github.com/heiher/hev-socks5-tunnel)
   تگ `2.19.3` و ساخت کتابخانهٔ JNI با نام پکیج `co/.asiven/.vixentvpn/.service` و کلاس
   `TProxyService` (پسوند `.so` در `app/src/main/jniLibs/arm64-v8a/`).
3. `tools/fetch-testkey.sh` — ساخت `signing/keystore.p12` از AOSP testkey تا **گواهی امضای APK
   همان گواهی اپ اصلی باشد** (هدرهای `sign`/`sha_hexadecimal` باید تطبیق داشته باشند).
4. `gradle assembleRelease -PtargetAbi=<abi>` ← بررسی وجود هر دو `.so` در APK، رد کردن هر
   معماری اضافی، چاپ `aapt2 badging`، `apksigner verify --print-certs` و ساخت `.sha256`.
5. جاب `release` هر دو APK را برمی‌دارد و یک Release با تگ `trial-<run_number>` می‌سازد.

### بررسی رابط کاربری روی شبیه‌ساز (`ui-snapshot`)

ورک‌فلوی [`.github/workflows/ui-snapshot.yml`](../../.github/workflows/ui-snapshot.yml) نسخهٔ
`x86_64` را با همان کلید امضا می‌سازد، شبیه‌ساز اندروید (API 34) را بالا می‌آورد، اپ را با
`tools/ui-drive.py` اجرا و کنترل می‌کند (لمس بر اساس متن/توضیح عناصر، تایپ در جست‌وجو، فیلترها،
bottom sheet، منو)، از هر مرحله اسکرین‌شات می‌گیرد و PNGها را در
`android-app/docs/screenshots/` کامیت می‌کند. تریگر:

```bash
git commit --allow-empty -m "chore: ui check [ui]"
git push origin arena/b9372ae1-myvpn
```

خروجی هر مرحله در `screenshots/STEPS.txt` و در annotationهای همان job (`ui-snapshot`) هم هست.

### آزمون واقعی اتصال (`connect-test`)

ورک‌فلوی [`.github/workflows/connect-test.yml`](../../.github/workflows/connect-test.yml) فقط
رابط کاربری را نمی‌بیند؛ **تونل را واقعاً بالا می‌آورد**:

1. یک سرور واقعی **Xray** (VLESS/TCP) روی همان runner بالا می‌آید (پورت `10086`).
2. شبیه‌ساز API 34 با APK `x86_64` نصب می‌شود.
3. کانفیگ با intent وارد اپ می‌شود:
   `adb shell am start -a android.intent.action.VIEW -d "vless://…@10.0.2.2:10086…" -n co.asiven.vixentvpn/…MainActivity`
   (اپ مثل v2rayNG لینک‌های `vless://`/`vmess://`/`trojan://`/`ss://` را می‌پذیرد).
4. ردیف اضافه‌شده انتخاب و «اتصال» زده می‌شود، دیالوگ مجوز VPN تأیید می‌شود.
5. ترافیک از پوستهٔ ادمین داخل TUN فرستاده می‌شود (`curl`/`nc`) و بعد **لاگ access سرور Xray**
   بررسی می‌شود؛ اگر درخواست در لاگ سرور باشد، یعنی بایت‌ها واقعاً از تونل گذشته‌اند.
6. در حال اتصال «پینگ همه» اجرا می‌شود و بررسی می‌شود سرور متصل **عوض نشود**
   (همان نقص «پینگ همه → مکث → پرش به سرور دیگر» در اپ اصلی).
7. در پایان «قطع اتصال» زده می‌شود و حذف شدن `tun0` بررسی می‌شود.

آخرین نتیجهٔ تأییدشده (اجرای `40275697024`):

| گام | نتیجه |
| --- | --- |
| ورود کانفیگ با intent | ✅ ردیف «CI-Local-A» در فهرست |
| اتصال + مجوز VPN | ✅ وضعیت «متصل — CI-Local-A (VPN)» |
| `tun0` | ✅ ساخته شد |
| عبور ترافیک واقعی | ✅ `204` و **ردِ درخواست در لاگ سرور Xray** |
| پینگ همه در حال اتصال | ✅ سرور همچنان «CI-Local-A»، بدون پرش |
| تغییر سرور در حال اتصال | ✅ تونل به «CI-Local-B» (VMess/WS) منتقل شد و ترافیک ادامه یافت |
| قطع اتصال | ✅ `tun0` حذف شد |

این اجرا دو نقص واقعی را پیدا و اصلاح کرد: سرویس تونل کانفیگ را از فیلد اشتباه می‌خواند
(اتصال هرگز شروع نمی‌شد) و نمونهٔ تازهٔ Activity وضعیت «در حال اتصال» را از دست می‌داد
(دکمه دوباره «اتصال» می‌شد و قطع/وصل می‌کرد).

خروجی در `android-app/docs/connect-test/` (`CONNECT.md` + PNG + لاگ‌ها) کامیت می‌شود. تریگر:

```bash
git commit --allow-empty -m "chore: tunnel check [net]"
git push origin arena/b9372ae1-myvpn
```

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
| `.../trial/core/PayloadCipher.kt` | باز کردن `value` (AES-128-CBC، کلید `key_<id>`، IV = کلید) + تشخیص خوانا بودن |
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
دریافت سرورها → ServerParser → PayloadCipher.unwrap(value) → لینک/JSON واقعی
انتخاب سرور → ConfigBuilder.parse(value) → outbound Xray
            → ConfigBuilder.runtimeConfig(outbound)   (SOCKS/HTTP 10808/10809 + direct/block)
mode == VPN   → VpnService(TUN 10.10.10.2/24, MTU 1500) → HevTunnel(tunFd)
              → XrayCore.start(config, tunFd = TUN)
mode == PROXY → HevTunnel(fd = 0) → locale SOCKS/HTTP → XrayCore.start(config, 0)
```

---

## ۶) `value` رمزنگاری‌شده — حل شد، هیچ ورودی از کاربر لازم نیست

فیلد `value` هر ردیف از `/api/protocols` base64 از یک blob رمزشده است. قاعده‌اش **کشف و تأیید شد**:

```
key = ("key_<id ردیف>" + صفر تا ۱۶ بایت)      IV = key      AES/CBC/PKCS5Padding
```

`id` می‌تواند منفی باشد (`key_-16068`). خروجی، لینک اشتراک (`vless`/`trojan`/…) یا JSON کامل Xray است.
پیاده‌سازی: `app/src/main/java/co/asiven/vixentvpn/trial/core/PayloadCipher.kt`.

- **پوشش ۱۰۰٪** روی پاسخ زنده: ۱۰۵ ردیف → ۹۸ `vless`، ۱ `trojan`، ۶ JSON (`vless+xhttp+reality`،
  `vless+tcp`، `hysteria`). شاهد: `docs/probe-rows/decrypt-coverage.txt`.
- کشف از کد عمومی پنل مدیریت همین خانوادهٔ سرویس (`vefghmhassan/vpn-pannel` →
  `internal/utils/tools.go` → `DecryptValue`) و سپس آزمون روی دادهٔ واقعی.
- آن ادعای قبلی که «`value` در هر درخواست عوض می‌شود» غلط بود؛ blob هر ردیف ثابت است و فقط ترتیب
  ردیف‌ها جابه‌جا می‌شود.

**نتیجه برای کاربر:** برنامه را باز می‌کنید؛ فهرست ۱۰۵ سرور خودش می‌آید، «پینگ همه» می‌زنید،
سریع‌ترین سرور خودکار انتخاب می‌شود و «اتصال» را می‌زنید. **از شما هیچ کانفیگ، لینک یا کلیدی
خواسته نمی‌شود.**

مسیرهای اختیاری هم سر جای خودشان هستند (نه لازم، نه پیش‌فرض): «افزودن کانفیگ از کلیپ‌بورد»،
«افزودن اشتراک»، و کپی لینک v2ray هر ردیف برای استفاده در v2rayNG/nekobox.

مستند کامل: [`value-decrypt-fa.md`](value-decrypt-fa.md).

---

## ۷) وضعیت Firebase

Firebase **طبق اپ اصلی** اضافه شده است:

| مورد | مقدار / محل |
| --- | --- |
| فایل تنظیمات | `android-app/app/google-services.json` (همان پروژهٔ اپ اصلی: `vixent-5ac3f`) |
| پلاگین Gradle | `com.google.gms.google-services` |
| وابستگی | `com.google.firebase:firebase-messaging:24.0.2` |
| سرویس | `trial/push/TrialMessagingService.kt` (ثبت توکن، دریافت پیام) |
| محل استفاده | توکن FCM در `Prefs.firebaseToken` ذخیره و در `/api/token?deviceId=…&firebase_token=…` ارسال می‌شود |

اگر Firebase روی دستگاه در دسترس نباشد (مثلاً بدون سرویس‌های گوگل)، خطا فقط لاگ می‌شود و بقیهٔ
اپ مثل قبل کار می‌کند؛ هیچ مسیر حیاتی به آن وابسته نیست. تبلیغات/حساب/قیمت همچنان حذف‌شده‌اند.

---

## ۸) عیب‌یابی

| نشانه | معنا و راه‌حل |
| --- | --- |
| «فهرست سرورها دریافت نشد» | منوی «لاگ‌ها» را ببینید؛ اگر `statusCode:400` با متن sign missing بود یعنی امضای APK با امضای اپ اصلی یکی نیست (باید با `fetch-testkey.sh` ساخته شود). |
| «سرور هیچ مقدار اتصالی ندارد» یا برچسب «مقدار رمزی» | مقدار `value` رمزشده است (بخش ۶)؛ بنر بالای فهرست دقیقاً همین را توضیح می‌دهد و دکمهٔ «افزودن کانفیگ / اشتراک» را نشان می‌دهد. |
| «همهٔ سرورها مقدار رمزی دارند و چیزی وصل نمی‌شود» | محدودیت سمت بک‌اند است، نه اپ: کانفیگ فقط داخل کد native اپ اصلی رمزگشایی می‌شود. با «افزودن اشتراک» یا «افزودن کانفیگ از کلیپ‌بورد» همان هسته، پینگ، اتصال و کپی لینک کامل کار می‌کند. |
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

---

## ۱۰) بازآزمایی APK اصلی (۲۰۲۶-۱۰-۲۶)

`base.apk` دوباره از گوگل‌درایو دانلود و با REA/androguard بازآزمایی شد؛ جدول کامل تفاوت‌ها و
یافته‌ها در [`re-analysis-fa.md`](re-analysis-fa.md) است. مهم‌ترین‌ها:

* هر سه لایه محافظت **باز شد**: قاعدهٔ رمزنگاری رشته‌ها (ScKit، `AES/ECB` + `MD5(passphrase)[8:24]`)
  با رمزگشایی کامل ۴۶٬۶۹۰ نقطهٔ فراخوانی (۰ خطا)، کلید آدرس API (`AES/CBC` با کلید و IV =
  نام بسته → `https://managev1.xyz`)، و نقشهٔ کامل کد بومی (۱۵ کلاس / ۲۵۸ متد) از جدول
  `np/dcc/protect/EntryPoint`.
* کلید `value` در این بسته **نیست** (نه در dex، نه در کد بومی) و `value` در هر درخواست عوض
  می‌شود. **به‌روزرسانی ۲۰۲۶-۱۰-۲۶:** خود قاعده بعداً کشف شد (کلید از `id` ردیف ساخته می‌شود،
  نه کلید ثابت داخل APK) و ۱۰۵/۱۰۵ ردیف با آن باز می‌شوند — بخش ۶ و
  [`value-decrypt-fa.md`](value-decrypt-fa.md).
* `geoip.dat`/`geosite.dat` در APK اصلی هم نیست و این نسخه به آن‌ها نیاز ندارد.
* «پینگ همه → مکث → پریدن به سرور دیگر» از منطق انتخاب خودکار سرور در اپ اصلی می‌آید؛ این نسخه
  چنین رفتاری ندارد و در `connect-test` هر بار سنجیده می‌شود.

## ۱۱) آزمون اتصال واقعی

دو آزمون مستقل، هر دو روی شبیه‌ساز واقعی در CI:

1. **`e2e-real` — سناریوی واقعی کاربر، بدون هیچ ورودی.** دادهٔ برنامه پاک می‌شود، اپ باز می‌شود،
   فهرست را خودش از بک‌اند می‌گیرد، `value` را خودش باز می‌کند، «پینگ همه» را می‌زند، سریع‌ترین
   سرور را می‌گیرد، وصل می‌شود، HTTPS را از تونل عبور می‌دهد، IP خروجی را با قبل از اتصال مقایسه
   می‌کند، سرور را عوض می‌کند و در پایان قطع می‌کند.
   گزارش: [`e2e-real/CONNECT-REAL.md`](e2e-real/CONNECT-REAL.md).
2. **`connect-test` — آزمون پشتهٔ تونل روی سرور محلی Xray.** کانفیگ تزریقی، اتصال، عبور ترافیک
   (با ردِ لاگ سرور Xray)، پایداری سرور در «پینگ همه»، تغییر سرور در حال اتصال و قطع اتصال.
   گزارش: [`connect-test/CONNECT.md`](connect-test/CONNECT.md).

هر دو ورق‌فلوی بالا تصاویر لحظه‌ای و لاگ‌کت را هم کنار گزارش کامیت می‌کنند.

## ۱۲) ابزارهای استخراج کلید و بازکردن لایه‌های محافظت

هر یافتهٔ بخش ۱۰ بازتولیدپذیر است:

| ابزار | کار | خروجی نمونه |
| --- | --- | --- |
| `tools/apk-keys.py --apk-dir <unpacked-apk>` | رمزگشایی کامل رشته‌های ScKit + کلید آدرس API | ۴۶٬۶۹۰ نقطهٔ فراخوانی، ۴۴٬۳۹۶ رشتهٔ یکتا، `https://managev1.xyz` |
| `tools/dcc-native-map.py <libstub.so> --json` | خواندن جدول محافظت ApkDex2C و نقشهٔ متدهای بومی | `docs/native-map.json` — ۱۵ کلاس / ۲۵۸ متد |
| `tools/probe-rows.py` | آزمون زندهٔ ۹ حالت هدر روی `/api/protocols` و `/api/v2/protocols` | `docs/probe-rows/{variants,v1,v2}.json` |
| `.github/workflows/probe-rows.yml` | اجرای پروب بالا در CI (تنها جایی که دسترسی به `managev1.xyz` هست) | کامیت خودکار شواهد |

```bash
# روی ماشین خودتان، با APK بازشده:
unzip -o base.apk -d /tmp/apk
pip install pycryptodome androguard
python3 android-app/tools/apk-keys.py --apk-dir /tmp/apk
python3 android-app/tools/dcc-native-map.py /tmp/apk/lib/arm64-v8a/libstub.so --json
```
