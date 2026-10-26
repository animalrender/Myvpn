# قرارداد API اپ اصلی و نسخهٔ آزمایشی

همهٔ مقادیر این سند از دی‌کامپایل APK اصلی (`co.asiven.vixentvpn` 3.2.0 / `versionCode` 1004220)
و از پروب‌های واقعی بک‌اند (فایل‌های `tools/probe-*.py` که در GitHub Actions اجرا می‌شوند) به‌دست آمده‌اند.

## ۱) آدرس پایه

| منبع | مقدار |
| --- | --- |
| `k4/b.c` | `apiUrl + "/api/"` |
| `k4/d.a()` | مقدار MMKV کلید `apiUrl`؛ اگر نبود: AES/CBC/PKCS5 با کلید=IV=۱۶ بایت اول `co.asiven.vixentvpn.debug` روی بلاب `tyBT242ubuxXa/YbRfrkGQVlNflSzufT6Q7TJTa5t0M=` |
| نتیجه | `https://managev1.xyz` |

## ۲) اندپوینت‌ها

| اندپوینت | متد | پارامترها | رفتار مشاهده‌شده (۲۰۲۶-۱۰) |
| --- | --- | --- | --- |
| `/api/token` | GET | `?deviceId=<16 hex>` | `{"statusCode":0,"status":false,"data":"The app token is disabled"}` — توکن در این بک‌اند غیرفعال است. `POST` → `405`. |
| `/api/setting` | GET | — | `{"statusCode":200,"status":true,"data":null}` (تنظیمات سمت سرور خالی است؛ اپ از پیش‌فرض‌ها استفاده می‌کند) |
| `/api/protocols` | GET | — | `200` + ۱۰۵ آیتم؛ `value` رمزشده (base64) |
| `/api/protocols/<operator>` | GET | هر مقداری | همان پاسخ قبلی؛ مسیر `<operator>` در این بک‌اند نادیده گرفته می‌شود |
| `/api/protocols` | POST | هر بدنه | `{"statusCode":0,"status":false,"data":"the protocol id is incorrect!"}` |
| `/api/v2/protocols` | GET | — | `200` + ۱۰۵ آیتم، با سه کلید اضافی `configKey`/`routeKey`/`endpointKey` |
| `/api/configs` | GET/POST | `deviceId`، `serverId`، `protocolId` | `404` در بک‌اند فعلی |

> در اپ اصلی: `k4/b` فیلدهای `d`/`e` = `.../api/protocols`، `f` = `.../api/configs`،
> `g` = `.../api/token`، `h` = `.../api/setting`. کلاس `MainActivity.getData()` و سایر منطق‌ها
> با Dex2C به کد native منتقل شده‌اند (`Lnp/dcc/protect/EntryPoint;->stub(I)V`).

## ۳) هدرها (ترتیب و مقدار دقیق)

از `co.nevisa.commonlib.volley.VolleyHelper.initHeaders()` (نام هدرها از `Vars.getVar(s)=s.split("=")[1]`):

| هدر | مقدار | شرط ارسال |
| --- | --- | --- |
| `Content-Type` | `application/json` | همیشه |
| `app_name` | `co.asiven.vixentvpn` — **ثابت** (از `BuildConfig.HEADER_APP_NAME`)، حتی با اینکه این نسخه با شناسهٔ `co.asiven.vixentvpn.trial` نصب می‌شود | همیشه |
| `version_code` | `String.valueOf(Lo4/b.b)` → `1004220` | همیشه |
| `seen` | `String.valueOf(Lz/d.y("admobSeen", 0))` → `0` | همیشه |
| `token` | `Lo4/b.f` | اگر مقدار داشته باشد |
| `sign` | `Base64(MD5(signature.toByteArray()))` | اگر `Lo4/c.d` |
| `sha_hexadecimal` | `hex(SHA-256(SHA-256(signature)))`، چند گواهی با `,` | اگر `Lo4/c.d` |
| `Authorization` | `bearer <Lo4/c.c>` | اگر خالی نباشد |

- `signature` همان `Signature.toByteArray()` است، یعنی **DER گواهی امضای APK**.
- گواهی اپ اصلی: `SHA-256 = A4:0D:A8:0A:…:F5:DC` (AOSP testkey) — ورک‌فلو با همان testkey امضا می‌کند.
- `sign` و `sha_hexadecimal` اجباری‌اند: بدون `sign` پاسخ
  `{"statusCode":400,"status":false,"data":"Proxy Mode : Application sign is missing."}` است
  (با HTTP 200!). همین موضوع باعث می‌شد نسخهٔ قبل «Internal server error» ببیند.

## ۴) تشخیص خطا

قاعدهٔ اپ آزمایشی (`ApiClient.execute`):

1. اگر HTTP خارج از `200..299` بود → خطا.
2. اگر بدنه JSON و `statusCode != 200` یا `status == false` بود → خطا با متن `data`.
3. اگر `data` آرایه/آبجکت نبود یا خالی بود → «فهرست دریافت نشد».

این کار لازم است چون بک‌اند خطاهای منطقی را با HTTP 200 برمی‌گرداند.

## ۵) شکل آیتم سرور

`/api/protocols`:

```json
{"id": -5824, "name": "🇫🇮 Finland", "value": "<base64>", "price": 0, "usage": 1046, "serverId": 465}
```

`/api/v2/protocols` همان + :

```json
{"telemetryIdentityVersion": 2, "configKey": "<64 hex>", "routeKey": "<64 hex>", "endpointKey": "<64 hex>"}
```

نکات:

- `id` برای هر ردیف ثابت است (ترتیب ردیف‌ها در پاسخ عوض می‌شود) و `endpointKey` هم برای یک `serverId` ثابت است.
- `price == 0` یعنی رایگان؛ `price > 0` یعنی پولی (در نسخهٔ آزمایشی هم نمایش داده و برچسب می‌شود).
- مدل اصلی (`Lco/dev/models/Protocol`) فیلدهای `id,name,serverId,flag,value,price,usage` را دارد.
- `usage` در اپ اصلی یک آبجکت `ProtocolUsage{DeviceId,OldProtocolId,OldServerId,ProtocolId,ServerId}` است؛
  در پاسخ این بک‌اند عدد است و اپ آزمایشی هر دو شکل را می‌پذیرد.

## ۶) `value` = مقدار اتصال

قرارداد اپ اصلی این است که `value` یک لینک اشتراک (`vmess://`، `vless://`، `trojan://`، `ss://`)
یا JSON کامل Xray باشد. اپ آزمایشی همهٔ این شکل‌ها را در `ConfigBuilder` پشتیبانی می‌کند:

| شکل | پارسر |
| --- | --- |
| `vmess://base64(JSON)` و فرم Kitsunebi | `parseVmess` |
| `vless://uuid@host:port?…` (با `type/sni/fp/pbk/sid/flow/…`) | `parseVless` |
| `trojan://pass@host:port?…` | `parseTrojan` |
| `ss://base64(method:pass)@host:port` | `parseShadowsocks` |
| `socks5://`، `http://` | `parseSocks`، `parseHttpProxy` |
| JSON کامل (شامل `outbounds[]`) | `parseJson` |

**در بک‌اند فعلی مقدار `value` همیشه رمزشده است** — قرارداد آن:

| مؤلفه | مقدار |
| --- | --- |
| انتقال | base64 استاندارد |
| الگوریتم | `AES/CBC/PKCS5Padding` |
| کلید | `"key_<id>"` (همان `id` ردیف) + بایت `0x00` تا ۱۶ بایت |
| IV | برابر کلید |

اپ آزمایشی همین را در `core/PayloadCipher.kt` پیاده کرده؛ اندازه‌گیری روی پاسخ زنده:
**۱۰۵ از ۱۰۵ ردیف** با موفقیت باز می‌شوند (۹۸ `vless`، ۱ `trojan`، ۶ JSON). جزئیات:
[`value-decrypt-fa.md`](value-decrypt-fa.md).

نکته: `id` می‌تواند منفی باشد (`key_-16068`) و علامت منفی جزو کلید است.

## ۶.۱) چه چیزی واقعاً آزمایش شد (نتیجهٔ قطعی)

پروب `tools/probe-header-bisect.py` در GitHub Actions، هدرها را یکی‌یکی خراب می‌کند و پاسخ بک‌اند را
ثبت می‌کند. نتیجه (از annotationهای همان اجرا):

| تغییر | پاسخ `/api/v2/protocols` |
| --- | --- |
| هیچ تغییری (هدرهای کامل) | ۲۰۰ · `status=true` · ۱۰۵ آیتم |
| `sign` = `Base64(SHA-256(DER))` (اشتباه رایج) | ۲۰۰ · `{"statusCode":400,"data":"Internal server error."}` |
| حذف `sha_hexadecimal` | ۲۰۰ · ۱۰۵ آیتم (تحمل می‌شود) |
| حذف `seen` یا مقدار `admobSeen` | ۲۰۰ · ۱۰۵ آیتم |
| بدون `Content-Type` / با UA اوک‌اچ‌آی‌پی | ۲۰۰ · ۱۰۵ آیتم |
| `token` خالی/نامعتبر | ۲۰۰ · ۱۰۵ آیتم (هدر فرستاده نمی‌شود) |
| `POST /api/token` | **405** (فقط GET مجاز است) |

یعنی **تنها** چیزی که «Internal server error.» می‌سازد، امضای اشتباه است:
`sign` باید `Base64(MD5(DER گواهی امضا))` باشد، نه SHA-256. اپ آزمایشی همین را پیاده می‌کند
(`ApiClient.Signing`)، و «تست API و هدرها» در منو، مقدار زندهٔ `sign`/`sha_hexadecimal` و وضعیت هر
اندپوینت را نشان می‌دهد.

## ۷) کلیدهای حافظه (هم‌نام با اپ اصلی)

`apiUrl`، `token`، `deviceId`، `testUrl` (`https://www.gstatic.com/generate_204`)،
`admobSeen`، حالت اتصال. اپ آزمایشی همین نام‌ها را در `SharedPreferences` نگه می‌دارد
(به‌جای MMKV) تا معناشناسی برای بررسی‌های بعدی روشن بماند.
