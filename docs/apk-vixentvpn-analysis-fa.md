# تحلیل کامل APK — «Vixen VPN» (`co.asiven.vixentvpn`)

> تحلیل ایستا (بدون اجرای برنامه) با REA + androguard + readelf روی فایل `base.apk`
> (۳۸٬۵۵۹٬۷۶۷ بایت، SHA-256: `d88660885b63c1c7bac59889f9a174b021a179781d183a43181199e6b001abb6`).
> هر ادعا در این سند به یک شاهد مشخص (کلاس، رشته، فایل، یا خروجی ابزار) وصل است و در
> بخش «محدودیت‌ها» نوشته شده چه چیزی قابل اثبات نبود.

---

## ۰. خلاصه‌ی اجرایی در ۱۰ خط

1. این فایل یک **کلاینت VPN مبتنی بر Xray-core** است که از پروژه‌ی متن‌باز **v2rayNG** فورک شده
   (`com.v2ray.ang.*`، `AngApplication`, `V2RayVpnService`).
2. نام تجاری‌اش **Vixen VPN** با پکیج `co.asiven.vixentvpn`، نسخه **3.2.0** (versionCode `1004220`).
3. هسته‌ی پروکسی: `libgojni.so` ساخته‌شده از **Xray-core** (`xtls/xray-core`, کامیت ۲۰۲۴‑۱۲‑۱۸)
   با `AndroidLibXrayLite`؛ به‌همراه `libtun2socks.so` برای حالت VPN/TUN.
4. برنامه یک **بک‌اند اختصاصی** دارد: `https://managev1.xyz` (رمزنگاری‌شده با AES داخل APK،
   کلید = ۱۶ بایت اول نام پکیج) با چهار endpoint: `/api/token`, `/api/setting`,
   `/api/protocols`, `/api/configs`.
5. احراز هویت سمت کلاینت با **هش امضای APK** (هدر `sign`) + `deviceId` + `token` انجام می‌شود؛
   یعنی سرور می‌تواند تشخیص دهد APK بازامضاشده است.
6. زیرساخت ابری: پروژه‌ی Firebase با شناسه‌ی **`vixent-5ac3f`** (appspot + FCM + Crashlytics +
   Analytics + Remote Config) و کلید عمومی Google API.
7. مدل درآمد: **تبلیغ جایزه‌ای (rewarded ad) در ازای «الماس»**؛ با الماس سرور پرسرعت می‌خرید.
   `connectionTimeLimit` و `connectedUntil` هم سقف زمان اتصال رایگان را کنترل می‌کنند.
8. تبلیغات/آنالیتیکس: AdMob (با App ID تستی گوگل!)، Fyber/FairBid + Inneractive، Flurry،
   Digital Turbine؛ رده‌های ByteDance/Pangle فقط به‌صورت رشته باقی مانده‌اند (کد حذف شده).
9. کد محافظت‌شده: **NP Manager / ApkDex2C 3.1.14** (کلاس‌های اصلی به کد بومی منتقل شده‌اند) +
   `libstub.so` + رشته‌ی `https://github.com/L-JINBIN/ApkSignatureKillerEx` (دور زدن بررسی امضا).
10. امضای APK **کلید تست اندروید** است (`CN=Android, O=Android, android@android.com`,
    SHA-256 `a40da80a…5dc`). ترکیب «کلید تست + SignatureKiller + dex2c + کانال تلگرام
    `t.me/Vpn_Click`» یعنی این نسخه **بازبسته‌بندی‌شده (repack)** است، نه خروجی رسمی Play.

---

## ۱. شناسنامه‌ی فایل

| مورد | مقدار | منبع |
| --- | --- | --- |
| نام فایل | `base.apk` (۳۸٬۵۵۹٬۷۶۷ بایت) | فایل |
| SHA-256 | `d88660885b63c1c7bac59889f9a174b021a179781d183a43181199e6b001abb6` | REA `inspect-apk-signature` |
| MD5 | `be8a3595026d704ae57219494a49d5ce` | `md5sum` |
| پکیج | `co.asiven.vixentvpn` | Manifest |
| نام نمایشی | Vixen VPN (رشته‌ی `Vixen Beta` هم موجود) | `resources.arsc` |
| نسخه | `3.2.0` / versionCode `1004220` | Manifest |
| minSdk / targetSdk / compileSdk | 21 / 34 / 34 | Manifest |
| entry activity | `co.dev.ui.WelcomeActivity` | Manifest |
| کلاس Application | `com.v2ray.ang.AngApplication` | Manifest |
| تعداد DEX | ۳ فایل (~۲۲٫۴ مگابایت) | ZIP |
| تعداد کلاس | **۲۱٬۰۷۹** | androguard |
| تعداد ورودی ZIP | ۱٬۳۹۲ | ZIP |
| امضا | v1 + v2، هر دو با کلید تست AOSP | REA |

نکته‌ی مهم در Manifest: `com.android.vending.splits`، `com.android.stamp.type =
STAMP_TYPE_DISTRIBUTION_APK` و `derived.apk.id=3` نشان می‌دهد این فایل **base یک اپ Split**
منتشرشده در Google Play است که بعداً از دستگاه/فروشگاه استخراج شده است.

---

## ۲. معماری داخلی — چهار لایه

```
┌─────────────────────────────────────────────────────────────────┐
│  UI اختصاصی سازنده:  co.dev.ui.{WelcomeActivity, ConnectedActivity}│
│  مدل‌ها: co.dev.models.{Setting, Protocol, Config, Token, Speed,   │
│                       Sponsor, Social, CheckerResult, ProtocolUsage}│
├─────────────────────────────────────────────────────────────────┤
│  SDK اختصاصی «Nevisa»: co.nevisa.commonlib.*                      │
│    volley (شبکه) · remoteConfig · firebase (push/update)          │
│    admob · fairbid (تبلیغات و مدیاسیون)                            │
├─────────────────────────────────────────────────────────────────┤
│  لایه‌ی داده/تنظیمات اپ:  k4.b (endpointها) · k4.d (MMKV)          │
│  ذخیره‌سازی:  MMKV (Tencent) + SharedPreferences + Room            │
├─────────────────────────────────────────────────────────────────┤
│  موتور متن‌باز: com.v2ray.ang (فورک v2rayNG)                       │
│    V2RayVpnService · V2RayProxyOnlyService · AngConfigManager     │
│    MmkvManager · V2rayConfigUtil · SpeedtestUtil · QSTileService  │
│    هسته: libgojni.so (Xray-core) + libtun2socks.so                │
└─────────────────────────────────────────────────────────────────┘
```

حجم کد: `com.google.*` ≈ ۱۰٬۲۳۵ کلاس (AdMob/GMS/Firebase/MLKit)، `com.fyber.*` ≈ ۲٬۸۸۰،
`com.flurry.*` ≈ ۵۵۱، `com.v2ray.ang.*` = ۳۷۴، `co.nevisa.*` = ۶۳، `co.dev.*` = ۳۰.

---

## ۳. پروسه‌ی کار برنامه — گام‌به‌گام

مسیر اجرا از `co.dev.ui.WelcomeActivity.onCreate` بازسازی شد:

**گام ۱ — بررسی امنیتی دستگاه.**
پرچم‌های MMKV خوانده می‌شوند: `checkRoot`, `checkUsbDebugging`, `checkEmulator`
(پیش‌فرض فعال). اگر شرط برقرار نباشد، پیام «Device Security Warning» / «The app cannot
run on an emulator. The app will now close.» نمایش داده می‌شود. رشته‌های تشخیص:
`/system/bin/su`, `/sbin/su`, `test-keys`, `goldfish`, `/proc/self/maps` و لاگ
`isRooted=… , isEmulator=…`.

**گام ۲ — هویت دستگاه.**
`deviceId = Settings.Secure.getString(android_id)` → ذخیره در MMKV با کلید `deviceId`.

**گام ۳ — صفحه‌ی حریم خصوصی.**
پرچم‌های `shownPrivacyScreen` و `accept_policy`؛ دکمه‌ی «Accept & Continue» و لینک سیاست
حریم خصوصی از `k4.d.h()` که پیش‌فرضش `https://sites.google.com/view/vixent/privacy` است.

**گام ۴ — سه درخواست موازی به بک‌اند** (به‌ترتیب وابستگی):

| تابع | endpoint | کار |
| --- | --- | --- |
| `getToken()` | `GET/POST {api}/api/token` | گرفتن توکن دستگاه و ذخیره در MMKV (`token`) |
| `getAppSetting()` | `{api}/api/setting` | دریافت تنظیمات اپ (مدل `Setting`) با کش (`settingCacheTime`) |
| `getData()` | `GET {api}/api/protocols/` | دریافت فهرست پروتکل‌ها/سرورها (مدل `Protocol`) |

پس از دریافت `Setting`، تابع `updateAppSettings()` این مقادیر را در MMKV می‌نویسد:
`connectionTimeLimit`, `connectedUntil`, `connectionTimeInitValue`,
`connectionTimeIncentivePolicy`, `privacyUrl`, `socialMedia`, `sponsor`, `testUrl`,
`admobKeys`, `admobStatus`, `admob*Targets`, `fairbidKeys`, `fairbid*Targets` و …

**گام ۵ — دریافت توکن FCM.**
`FirebaseMessaging.getInstance().getToken()` → هدر `firebase_token` روی درخواست‌ها
(`VolleyHelper.addParamToHeader`). سرویس `co.dev.firebase.MyFireBaseMessagingService`
پیام‌های `token` و `clear_token` را پردازش می‌کند → push برای اعلان/به‌روزرسانی/دیالوگ.

**گام ۶ — تنظیمات موتور Xray.**
`updateV2RaySetting(Setting)` این کلیدهای SharedPreferences را می‌نویسد:
`pref_prefer_ipv6`, `pref_proxy_sharing_enabled`, `pref_allow_insecure`, `pref_mux_enabled`,
`pref_fragment_enabled`, `pref_auto_update_subscription(+_interval)`, `pref_speed_enabled`,
`pref_routing_domain_strategy`, `pref_v2ray_routing_{blocked,agent,direct}`, `global_setting`/`testUrl`.

**گام ۷ — اتصال.**
`WelcomeActivity` → `MainActivity` (v2rayNG) و برای شروع تونل → `V2RayVpnService`
(فرآیند جدا: `:RunSoLibV2RayDaemon`, `foregroundServiceType=specialUse`, `BIND_VPN_SERVICE`).
سپس `ConnectedActivity` باز می‌شود که تبلیغ interstitial/native/rewarded را مدیریت می‌کند.

**گام ۸ — چرخه‌ی درآمدزایی.**
- تایمر سقف زمان اتصال (`connectionTimeLimit` + `connectedUntil`).
- «الماس» (diamonds): با تماشای ویدیوی تشویقی ۳۰ ثانیه‌ای به دست می‌آید.
- با الماس، «سرور اختصاصی/پرسرعت» خریداری می‌شود (`Protocol.price`).
- پیام‌ها: «Your diamonds are not enough to buy this server… You can increase your
  diamonds by watching promotional videos» و «Get %s hour additional connection time».
- لایه‌های پلن: `more_plans`, `premium`, `premium_first`, `reward`, `skip_rewarded_dialog`.

**گام ۹ — تغییر دامنه از راه دور.**
`WelcomeActivity.setDomain(String)` اجازه می‌دهد سرور یک دامنه‌ی جدید بدهد؛ اپ آن را
رمزنگاری/رمزگشایی کرده و `apiUrl` را در MMKV به‌روز می‌کند (مکانیزم مقابله با بلاک شدن API).

---

## ۴. بک‌اند و API — جزئیات کامل

### ۴.۱ دامنه‌ی پایه (کشف و رمزگشایی‌شده)

کلاس `k4.d` تابع `a()` را دارد که مقدار پیش‌فرض رمزنگاری‌شده‌ی زیر را از MMKV می‌خواند
و با `z.d.v(cipher, key)` رمزگشایی می‌کند:

```
cipher : tyBT242ubuxXa/YbRfrkGQVlNflSzufT6Q7TJTa5t0M=
scheme : AES/CBC/PKCS5Padding
key    : co.asiven.vixent          (۱۶ بایت اول نام پکیج "co.asiven.vixentvpn")
IV     : همان ۱۶ بایت
result : https://managev1.xyz
```

### ۴.۲ endpointها (کلاس `k4.b`)

| فیلد | مسیر کامل | مصرف‌کننده |
| --- | --- | --- |
| `c` | `https://managev1.xyz/api/` | پایه |
| `d` | `…/api/protocols` | `getData()` — فهرست سرور/پروتکل |
| `e` | `…/api/protocols` (نسخه‌ی همراه با اسلش) | `getData()` |
| `f` | `…/api/configs` | پیکربندی/کانفیگ‌های آماده |
| `g` | `…/api/token` | `getToken()` — توکن دستگاه |
| `h` | `…/api/setting` | `getAppSetting()` — تنظیمات اپ |

فراخوانی با `VolleyHelper.apply(method, url, jsonBody, callback, tag)` و تگ‌های
`get_data`, `get_token`, `get_setting`, `firebase_token`.

### ۴.۳ هدرها و امضای درخواست (`co.nevisa.commonlib.volley`)

`VolleyHelper.initHeaders()` این هدرها را می‌سازد (نام‌ها در کد به‌صورت پازل
`...=key=...=key` نگه داشته شده‌اند و با `getVar()` استخراج می‌شوند):

| هدر | مقدار |
| --- | --- |
| `Content-Type` | `application/json` |
| `app_name` | نام پکیج (`context.getPackageName()`) |
| `version_code` | versionCode بیلد |
| `admobSeen` | شمارنده/مقدار `seen` |
| `token` | توکن ذخیره‌شده |
| `sign` | `Base64(MessageDigest.digest(PackageInfo.signatures[0].toByteArray()))` |
| `sha_hexadecimal` | هش hex امضا (به‌همراه کاما) |
| `Authorization` | `bearer <token>` (در صورت وجود) |
| `firebase_token` | توکن FCM |

**نکته‌ی امنیتی کلیدی:** `getSign()` هشِ گواهی امضای APK را می‌فرستد. یعنی سرور می‌تواند
نسخه‌ی بازامضاشده را رد کند. در همین APK رشته‌ی
`https://github.com/L-JINBIN/ApkSignatureKillerEx` وجود دارد — کتابخانه‌ای که
`PackageManager.getPackageInfo().signatures` را قلابی می‌کند تا همین بررسی دور زده شود.

### ۴.۴ مدل داده‌ی تنظیمات (`co.dev.models.Setting`)

فیلدهای کامل: `apiUrl`, `policyUrl`, `testUrl`, `socialMedia`, `sponsor`, `admobKeys`,
`admobStatus`, `admobInterstitialTargets`, `admobRewardTargets`,
`admobRewardInterstitialTargets`, `admobNativeTargets`, `fairbidKeys`, `fairbidStatus`,
`fairbidInterstitialTargets`, `fairbidRewardTargets`, `connectionTimeInit`,
`connectionTimeLimit`, `connectionTimeIncentivePolicy`, `connectedActivityDuration`,
`connectionFromLan`, `subAutoUpdate`, `subAutoUpdateInterval`, `showSpeed`, `preferIPV6`,
`mux`, `fragment`, `insecure`, `domainStrategy`, `v2RaySetting`, `appSetting`,
`customRuleBlocked`, `customRuleProxy`, `customRuleDirect`.

مدل‌های دیگر: `Protocol{id,name,serverId,flag,value,price,usage}`،
`Config{key,value}`، `Token{name}`، `Speed{download,upload}`،
`Sponsor{title,description,image,link,btnText,label}`،
`Social{telegram,instagram,facebook,youtube,twitter,tiktok,share}`،
`CheckerResult{Id,Operator,Ping}`، `ProtocolUsage{ServerId,ProtocolId,DeviceId,…}`.

---

## ۵. Firebase و کلیدها

| مورد | مقدار | منبع |
| --- | --- | --- |
| Project ID | `vixent-5ac3f` | `resources.arsc` |
| دامنه‌ی App Engine | `vixent-5ac3f.appspot.com` | `resources.arsc` |
| Firebase App ID | `1:834191356570:android:9bb2699ab2eaac1c166523` | `resources.arsc` |
| Google API Key | `AIzaSyD9oHHJLnmn9uSU0ri5qyX7v9w71LZIQyY` | `resources.arsc` |
| AdMob App ID | `ca-app-pub-3940256099942544~3347511713` ⚠️ **کلید تست رسمی گوگل** | Manifest |
| FCM | `com.google.android.c2dm.permission.RECEIVE` + `MyFireBaseMessagingService` | Manifest |
| Crashlytics / Analytics / Sessions | فعال (رجیسترارها در Manifest) | Manifest |
| Remote Config keys | `remote_config_api`, `reward_ad_off`, `reward_off_ad_in_hour`, `admob_reward_targets`, `admob_rewarded_interstitial_targets`, `mehmet_reward_targets`, `mehmet_interstitial_targets`, `gdpr*` | کلاس‌های `co.nevisa.commonlib.remoteConfig` و `commonlib/firebase` |

> کلید Google API در APK‌های اندروید معمولاً «محرمانه» نیست و با محدودیت بسته/امضا
> استفاده می‌شود؛ اما افشای آن در اینجا یعنی هر کسی می‌تواند تا وقتی محدودیت سمت
> Google Cloud تنظیم نشده، سهمیه‌ی پروژه را مصرف کند.

---

## ۶. هسته‌ی VPN — دقیقاً چه چیزی اجرا می‌شود

خروجی `rea inspect-go-binary` روی `lib/arm64-v8a/libgojni.so`:

```
Go: go1.22.10   buildmode=c-shared   CGO_ENABLED=1   GOOS=android  GOARCH=arm64
main module : gobind/gobind
replaced by : C:\Users\Nevisa\go\src\XrayLiteGithub1.8.26\AndroidLibXrayLite   (devel)
key deps    : github.com/xtls/xray-core v0.0.0-20241218133935-cab2fdefd321
              github.com/xtls/reality, github.com/refraction-networking/utls v1.6.7
              github.com/quic-go/quic-go v0.47.0, github.com/sagernet/sing v0.5.1
              golang.zx2c4.com/wireguard, gvisor.dev/gvisor, google.golang.org/grpc
```

یعنی هسته **Xray-core (دسامبر ۲۰۲۴)** است، نه v2ray-core کلاسیک؛ با پشتیبانی
VLESS/VMess/Trojan/Shadowsocks/WireGuard/SOCKS، + REALITY، uTLS، QUIC، gRPC،
XHTTP/splithttp و Mux. این دقیقاً همان چیزی است که در UI هم می‌بینیم:
`activity_server_{vmess,vless,trojan,shadowsocks,socks,wireguard,custom_config}.xml`.

اجزای دیگر:

| فایل | نقش |
| --- | --- |
| `libgojni.so` (۲۸٫۷ MB arm64 / ۲۶٫۴ MB armv7) | هسته‌ی Xray (Go) |
| `libtun2socks.so` (۱۵۲ KB) | پل TUN → SOCKS برای حالت VPN |
| `libmmkv.so` (۵۲۲ KB) | ذخیره‌سازی سریع MMKV (تنظیمات، توکن، سرورها) |
| `libbarhopper_v3.so` + `libimage_processing_util_jni.so` + `assets/mlkit_*` | ML Kit بارکد/QR اسکنر (پروژه‌ی `io.github.g00fy2.quickie`) |
| `libstub.so` (۸۶۴ KB) | استاب بسته‌بندی NP Manager (`np/dcc/protect/EntryPoint`) |
| `assets/geoip.dat` (۵٫۵ MB) / `assets/geosite.dat` (۱٫۷ MB) | داده‌های geo از اکوسیستم v2fly/Xray |

### قواعد مسیریابی پیش‌فرض

`assets/custom_routing_block` → `geosite:category-ads-all`
`assets/custom_routing_proxy` → `geosite:google`, `github`, `netflix`, `steam`, `telegram`
`assets/custom_routing_direct` → ۱۳۱ دامنه‌ی محلی/ایرانی (`domain:12306.com` …)
`assets/proxy_packagename.txt` → فهرست بسته‌های per-app proxy (مرورگرها، تلگرام، ProtonMail، …)

### کانفیگ پیش‌فرض داخل APK

`assets/v2ray_config.json` یک کانفیگ نمونه است (socks 10808 + http 10809، outbound
`vmess` به `v2ray.cool:10086` با `a3482e88-686a-4a58-8126-99c9df64b7bf` و یک
shadowsocks با رمز `123456`). این همان کانفیگ دموی معروف `v2ray.cool` است و **سرور واقعی
اپ نیست**؛ سرورهای واقعی از `managev1.xyz` می‌آیند.

---

## ۷. تبلیغات، آنالیتیکس و ردیابی

| SDK | وضعیت | شاهد |
| --- | --- | --- |
| Google AdMob / GMS Ads | ✅ فعال (۵۹۶ کلاس + ۵٬۵۷۱ کلاس internal/ads) | Manifest + کد |
| Fyber FairBid + Inneractive | ✅ فعال (۲٬۸۸۰ کلاس) | Manifest + `TestSuiteActivity` |
| Digital Turbine Ignite | ✅ فعال | `com.digitalturbine.ignite` + رشته‌ی «Ads by DT» |
| Flurry Analytics | ✅ فعال (۵۵۱ کلاس) | `FlurryContentProvider` |
| Firebase Analytics/Crashlytics/Sessions | ✅ فعال | Manifest |
| ByteDance / Pangle | ⚠️ فقط رشته‌های باقی‌مانده (`com.bytedance.sdk.openadsdk.*`) — کلاس‌ها حذف شده‌اند | `classes.dex` |
| Google Sign-In | ✅ (صفحه‌ی «Sign in with Google») | `GoogleSignInOptions` |

Endpointهای تبلیغاتی صریح در DEX: `https://api.fyber.com/vcs/v1/new_credit.json`,
`https://service.fyber.com/installs/v2`, `https://offer.fyber.com/mobile`.
شناسه‌های واقعی AdMob/FairBid از پنل (endpoint `setting`) می‌آیند و در APK ثابت نیستند،
به‌جز App ID که همان **کلید تست گوگل** است.

---

## ۸. حفاظت، ضدتحلیل و اثر انگشت بازبسته‌بندی

| شاهد | معنا |
| --- | --- |
| `assets/protected_by_np/ApkDex2c_*.txt`: `ProtectTime: 2025-01-01 16:34:56`, `Function: Apk-Dex2C`, `Version: 3.1.14` | کد با **NP Manager** به کد بومی منتقل شده (Dex2C) |
| `libstub.so` → `JNI_OnLoad`, `np/dcc/protect/EntryPoint`, `https://t.me/Vpn_Click` | استاب لودر NP + کانال تلگرام بازبسته‌بند |
| ۱٬۹۶۴ کلاس دارای متد native (از جمله `MainActivity` با ۱۴۹ متد) | منطق حساس در `.so` است، نه در DEX |
| رشته‌ی `https://github.com/L-JINBIN/ApkSignatureKillerEx` | کتابخانه‌ی دور زدن بررسی امضا |
| امضا = کلید تست AOSP (`a40da80a…5dc`) | امضای عمومی، نه کلید توسعه‌دهنده‌ی اصلی |
| `usesCleartextTraffic=false` | ترافیک HTTP متن‌باز ممنوع (خوب) |
| root/emulator/USB-debug check + پیام «Device Security Warning» | ضد دیباگ/ضد تحلیل |

**جمع‌بندی این بخش:** این APK با ابزارهای کد‑محافظ (NP Manager) بسته‌بندی شده، با کلید
تست امضا شده، کتابخانه‌ی «کشنده‌ی امضا» در آن هست و یک کانال تلگرام (`Vpn_Click`) داخل
کد دارد. این الگو برای **نسخه‌های مود/کرک‌شده یا توزیع‌های غیررسمی** معمول است؛ به همین
دلیل «Old.v1.0.0» در ریلیز شما هم معنادار است.

---

## ۹. جدول یک‌جای «همه‌ی مقادیر مهم»

```
پکیج        : co.asiven.vixentvpn          نسخه : 3.2.0 (1004220)
API base    : https://managev1.xyz
endpoints   : /api/token · /api/setting · /api/protocols · /api/configs
privacy     : https://sites.google.com/view/vixent/privacy
test URL    : https://www.gstatic.com/generate_204
Firebase    : vixent-5ac3f / vixent-5ac3f.appspot.com
App ID      : 1:834191356570:android:9bb2699ab2eaac1c166523
API key     : AIzaSyD9oHHJLnmn9uSU0ri5qyX7v9w71LZIQyY
AdMob AppID : ca-app-pub-3940256099942544~3347511713   (تست گوگل)
AES key API : co.asiven.vixent   (مشتق از نام پکیج، IV = همان)
Xray core   : xtls/xray-core @ 2024-12-18  (AndroidLibXrayLite)
build host  : C:\Users\Nevisa\go\src\XrayLiteGithub1.8.26
پورت‌های محلی: 10808 (socks) · 10809 (http)
کانال تلگرام: t.me/Vpn_Click   (داخل libstub.so)
signing     : CN=Android, O=Android, android@android.com  (کلید تست)
```

---

## ۱۰. ارزیابی ریسک و توصیه‌ها

1. **این نسخه را به‌عنوان نسخه‌ی رسمی اعتماد نکنید.** امضای کلید تست + SignatureKiller +
   Dex2C یعنی کد می‌تواند بدون شفافیت تغییر کرده باشد. اگر می‌خواهید از سرویس استفاده کنید،
   نسخه‌ی رسمی Play Store را بردارید و امضایش را مقایسه کنید.
2. **توکن دستگاه و `deviceId` (ANDROID_ID)** به `managev1.xyz` ارسال می‌شود؛ این شناسه‌ی
   پایدار است. از دید حریم خصوصی، این یک ردیابی بین‌نشستی است.
3. **هدر `sign` (هش امضا)** یعنی سرور می‌فهمد کلاینت دستکاری شده؛ ترکیب با SignatureKiller
   یعنی سازنده‌ی این نسخه عمداً می‌خواسته سرور را فریب دهد.
4. **تبلیغات و تحلیل‌گر زیاد** (AdMob + Fyber + Inneractive + Flurry + DT + Firebase) →
   سطح ردیابی بالا؛ برای تست، اپ را در پروفایل جدا/شبیه‌ساز بدون حساب گوگل اجرا کنید.
5. **کلید Google API افشا شده**؛ اگر پروژه مال شماست، همین امروز محدودیت بسته/امضا و
   سهمیه‌بندی را در Google Cloud تنظیم کنید.
6. **Xray-core دسامبر ۲۰۲۴** است؛ نسخه‌های جدیدتر رفع آسیب‌پذیری دارند. اگر این اپ را
   نگه می‌دارید، هسته را به‌روز کنید.
7. اگر قصد بازسازی/فورک دارید: `managev1.xyz` و کلید AES سمت **کلاینت** هستند؛ به‌جای
   تکیه بر آن‌ها، احراز هویت واقعی (mTLS یا امضای سرور) بگذارید.

---

## ۱۱. محدودیت‌های این تحلیل (صادقانه)

- **اجرا نشد:** هیچ‌کدام از عملیات runtime (نصب، اتصال VPN، درخواست واقعی به API) انجام
  نشده؛ همه‌چیز ایستا است. رفتار شبکه‌ای «در عمل» تأیید نشده.
- **API پرسیده نشد:** `managev1.xyz` در فهرست دامنه‌های مجاز این سندباکس نیست، پس
  پاسخ واقعی `/api/setting` و `/api/protocols` دیده نشده؛ ساختار آن‌ها از مدل‌های کلاس
  (`Setting`, `Protocol`, `Config`) استنتاج شده است.
- **بخشی از کد در native است:** با Dex2C، منطق `MainActivity` و بخش‌های حساس به
  `libstub.so` منتقل شده و در DEX قابل خواندن نیست؛ تحلیل آن نیاز به مهندسی معکوس
  بومی (Ghidra/Hopper) دارد که در این سندباکس نصب نیست (دلیلش در راهنمای REA، بخش ۹).
- **`libgojni.so` و `libstub.so` با REA layout تحلیل نشدند:** provider مربوطه فقط
  x86-64/i386/ARM32/MIPS را می‌پذیرد، نه aarch64؛ به‌جایش از `readelf` و
  `inspect-go-binary` استفاده شد.
- **کلاس‌های Pangle حذف شده‌اند** ولی رشته‌هایشان مانده؛ نمی‌توان گفت در نسخه‌های دیگر
  فعال بوده‌اند یا نه.

---

## ۱۲. بازتولید تحلیل (دستورها)

```bash
# 1) هویت و امضا
rea inspect-apk-signature base.apk --json

# 2) Manifest و اجزا
python3 - <<'PY'
from loguru import logger; logger.remove()
from androguard.core.axml import AXMLPrinter
print(AXMLPrinter(open('AndroidManifest.xml','rb').read()).get_xml().decode())
PY

# 3) استخراج رشته‌ها/کلیدها
grep -a -o 'AIza[0-9A-Za-z_-]\{35\}' resources.arsc
grep -a -o '1:[0-9]*:android:[0-9a-f]*' resources.arsc

# 4) هسته‌ی Xray
rea inspect-go-binary libgojni.so --json

# 5) رمزگشایی دامنه‌ی API
python3 -c "
import base64;from Crypto.Cipher import AES
k=b'co.asiven.vixent'
print(AES.new(k,AES.MODE_CBC,k).decrypt(base64.b64decode('tyBT242ubuxXa/YbRfrkGQVlNflSzufT6Q7TJTa5t0M=')))"
```

---

# پیوست A — عملکرد دقیق: جریان اتصال، مدل پریمیوم، تونل/پروکسی و سابسکریپشن

با اینکه `MainActivity` با Dex2C به کد بومی منتقل شده، **نام متدها در DEX باقی مانده** و همین
نام‌ها + مسیرهای کدِ محافظت‌نشده، جریان کار را کامل مشخص می‌کنند.

## A.1 ترتیب دقیق اجرا

```
WelcomeActivity.onCreate
 ├─ چک root/emulator/USB-debug   (MMKV: checkRoot, checkUsbDebugging, checkEmulator)
 ├─ صفحه‌ی حریم خصوصی            (shownPrivacyScreen, accept_policy)
 ├─ deviceId = ANDROID_ID        (MMKV: deviceId)
 ├─ getToken()      → /api/token      → MMKV: token
 ├─ getAppSetting() → /api/setting    → MMKV: connectionTimeLimit, connectedUntil,
 │                                       connectionTimeInitValue, privacyUrl, apiUrl,
 │                                       admobKeys, fairbidKeys, testUrl, …
 ├─ GoogleSignIn (اختیاری) + FirebaseMessaging.getToken() → هدر firebase_token
 └─ getData()       → /api/protocols  → فهرست Protocol
        └─ AngConfigManager.importConfig(id, subId, ServerConfig, Protocol)
           AngConfigManager.importBatchConfig(id, subId, Z, Protocol)
              → MmkvManager.encodeServerConfig(...)   // ذخیره در استور v2rayNG
                 (Protocol به‌عنوان customConfig داخل ServerConfig می‌نشیند)

MainActivity
 ├─ initData(list) → MainRecyclerAdapter (هر ردیف = یک ServerConfig + Protocol)
 │     └─ updateRowUi(...)   ← price و usage هر سرور را می‌خواند (نمایش قیمت/وضعیت)
 ├─ connectClick(view)
 │     └─ i4.c.a(ServerConfig, callback) : Z    ← «دروازه‌ی» پریمیوم (پایین)
 ├─ requestVpnPermission → V2RayVpnService (یا V2RayProxyOnlyService)
 │     └─ V2RayServiceManager.startV2Ray / startV2rayPoint  → libgojni (Xray)
 │        V2RayVpnService.setup() → runTun2socks() → sendFd() → vpnProtect()
 ├─ initConnectionTimer / startConnectionTimer / calculateUsingTime
 │     MMKV: connectedUntil, connectionTimeLimit, connectionTimeInitValue
 ├─ connected(Z) → ConnectedActivity (progress + تبلیغ interstitial/native)
 └─ حین اتصال: initAd, showInterstitial, showInterstitialReward, initSponsor,
    initSocialMedia, checkPushUpdate (FCM), delayDisconnect, extendConnectionTime,
    boostTimeIncentivePolicy, increaseServerUsage / decreaseServerUsage
```

## A.2 مدل «پریمیوم» — اکانت نیست، قفلِ هر سرور است

`Li4/c;->a(ServerConfig config, callback) : boolean` — قلب منطق:

```java
Protocol p      = config.getCustomConfig();
int price       = p.getPrice();          // قیمت سرور به «الماس»
int serverId    = p.getServerId();
String bought   = MMKV("boughtServers").getString(...); // شناسه‌های خریداری‌شده، جداشده با '-'
int coins       = MMKV("coins").getInt(...);            // موجودی الماس
// اگر سرور قبلاً خریداری نشده و coins < price  →  false + دیالوگ/ویدیوی جایزه‌ای
// در غیر این صورت: coins -= price ; ذخیره coins ; افزودن serverId به boughtServers
```

نتیجه‌های مهم:

* **هیچ بررسی حساب کاربری/پرمیوم سمت سرور دیده نمی‌شود**؛ وضعیت خرید در **MMKV محلی**
  (`coins`, `boughtServers`) نگه داشته می‌شود. یعنی قفل، سمت کلاینت است.
* علاوه بر قفل هر سرور، یک **سهمیه‌ی زمانی اتصال** هم هست: `connectionTimeLimit`,
  `connectedUntil`, `connectionTimeInitValue`, `connectionTimeIncentivePolicy` +
  `initConnectionTimer` / `remainingTimeToText` / `extendConnectionTime` /
  `boostTimeIncentivePolicy(Z)` / `delayDisconnect(J)`.
* الماس از کجا؟ `ConnectedActivity.showRewarded` / `showRewardedInterstitial` /
  `MainRecyclerAdapter.getServerSideVerificationOptions()` (AdMob **SSV**) →
  اعتبارسنجی سمت سرور تبلیغ و واریز الماس.
* `increaseServerUsage()/decreaseServerUsage()` + خواندن `Protocol.usage` در
  `updateRowUi` = شمارنده‌ی مصرف هر سرور (کنترل ظرفیت/سهمیه‌ی سرورهای رایگان).
* `MainViewModel.connectAuto()` هم `price` و `serverId` را می‌خواند → اتصال خودکار
  سرورهای پولی را رد می‌کند.

> نکته‌ی رمزنگاری: در همین متدها رشته‌های `ScKit-<hash>` دیده می‌شود؛ اینها کلید
> رمزنگاری رشته‌های NP Manager هستند، پس متن‌های UI این بخش‌ها در DEX خوانا نیستند
> و در زمان اجرا رمزگشایی می‌شوند.

## A.3 تونل است یا پروکسی؟ — هر دو

| حالت | شاهد |
| --- | --- |
| **VPN / TUN (پیش‌فرض)** | `V2RayVpnService` با `BIND_VPN_SERVICE` + `setup()`, `runTun2socks()`, `sendFd()`, `vpnProtect()`, `libtun2socks.so` |
| **فقط پروکسی (Proxy only)** | `V2RayProxyOnlyService` + کلید `pref_mode` با مقادیر `VPN` / `PROXY` |
| **پورت‌های محلی** | `pref_socks_port` (10808), `pref_http_port` (10809) |
| **اشتراک در LAN** | `pref_proxy_sharing_enabled` |
| **per-app proxy** | `pref_per_app_proxy` + `assets/proxy_packagename.txt` |
| **DNS** | `pref_vpn_dns`, `pref_fake_dns_enabled`, `pref_local_dns_enabled/port`, `pref_remote_dns`, `pref_domestic_dns` |
| **ضد DPI** | `pref_fragment_enabled/packets/length/interval` + `pref_mux_*` |
| **sniffing / routing** | `pref_sniffing_enabled`, `pref_routing_mode`, `pref_routing_domain_strategy` |

یعنی دقیقاً مثل v2rayNG: در حالت VPN همه‌ی ترافیک دستگاه از Xray رد می‌شود (با
tun2socks)، و در حالت پروکسی فقط یک SOCKS/HTTP محلی می‌دهد.

## A.4 سابسکریپشن

**داخل خود اپ (ورودی):** کامل موجود است —
`MmkvManager.importUrlAsSubscription`, `decodeSubscriptions`, `removeSubscription`,
`AngConfigManager.importSubscription`, `SubscriptionUpdater`,
اکتیویتی‌های `SubSettingActivity` / `SubEditActivity`, و کلیدهای
`pref_auto_update_subscription` + `pref_auto_update_interval`.
پس می‌توانید لینک سابسکریپشن دلخواه (vmess/vless/trojan/ss) را داخل این اپ ایمپورت کنید.

**خروجی (بردن سرورهای این اپ به کلاینت خودتان):** بله، با ابزارهای اشتراک‌گذاری
v2rayNG که دست‌نخورده مانده‌اند:
`shareConfig`, `share2Clipboard`, `share2QRCode`, `shareFullContent2Clipboard`,
`shareNonCustomConfigsToClipboard`, `exportAllConfig`, `doShare`, `getShareUrl`
→ لینک‌های استاندارد `vmess://` / `vless://` / `trojan://` تولید می‌شود که در هر
کلاینت v2ray/Xray کار می‌کند.

**برعکس (بک‌اند این اپ را به‌عنوان ساب در v2ray گذاشتن):** خیر —
هیچ endpoint سابسکریپشنی وجود ندارد؛ API با `token` دستگاه + هدر `sign`
(هش امضای APK) کار می‌کند و سرورها per-device هستند (`ProtocolUsage.DeviceId`).
تنها راه انتقال، خروجی گرفتن تک‌تک/کلی سرورها از داخل اپ است.

## A.5 سرور پرمیوم جداگانه؟

نه — **یک فهرست واحد** (`/api/protocols`) با فیلد `price` برای هر سرور:

* `price = 0` → سرور آزاد (با سهمیه‌ی زمانی/مصرف)
* `price > 0` → قفل، خرید با الماس (ویدیوی جایزه‌ای)
* سرورهای دیگر (sponsor / social / plans) از `/api/setting` می‌آیند، نه از یک
  endpoint جداگانه‌ی «پریمیوم»
