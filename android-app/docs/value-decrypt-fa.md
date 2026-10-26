# باز کردن `value` — کشف نهایی و پیاده‌سازی در کلاینت آزمایشی

این سند پاسخ یک پرسش را می‌دهد: **چگونه نسخهٔ آزمایشی بدون گرفتن هیچ کانفیگ/لینکی از کاربر،
سرورها را خودش می‌گیرد و وصل می‌شود؟**

## ۱) خلاصه در یک نگاه

| مؤلفه | مقدار |
|---|---|
| الگوریتم | `AES/CBC/PKCS5Padding` (PKCS7 هم همان است) |
| اندازهٔ کلید | ۱۲۸ بیت (یک بلوک ۱۶ بایتی) |
| گذرواژه | رشتهٔ `"key_<id>"` که با بایت `0x00` از سمت راست تا ۱۶ بایت پر می‌شود |
| IV | **دقیقاً همان کلید** |
| ورودی | مقدار فیلد `value` هر ردیف از `/api/protocols` (base64 استاندارد) |
| خروجی | لینک اشتراک (`vless://`، `vmess://`، `trojan://`، `ss://`) یا JSON کامل Xray |
| پیاده‌سازی در اپ | `app/src/main/java/co/asiven/vixentvpn/trial/core/PayloadCipher.kt` |

`id` همان شناسهٔ ردیف در پاسخ است و **می‌تواند منفی باشد** (مثلاً `-16068`)؛ علامت منفی هم بخشی از
کلید است: `key_-16068`.

قطعهٔ اصلی:

```kotlin
fun keyFor(protocolId: Int): ByteArray {
    val material = ("key_" + protocolId).toByteArray(Charsets.US_ASCII)
    val key = ByteArray(16)
    System.arraycopy(material, 0, key, 0, minOf(material.size, 16))
    return key
}

val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
cipher.init(Cipher.DECRYPT_MODE, SecretKeySpec(key, "AES"), IvParameterSpec(key))
val plaintext = cipher.doFinal(Base64.decode(value, Base64.DEFAULT))
```

## ۲) چگونه پیدا شد

مسیرهای قبلی (که در `re-analysis-fa.md` بخش ۸ مستند شده‌اند) همه بسته بودند:

- کلید در `base.apk` نیست: `libstub.so` فقط `javax/crypto` را صدا می‌زند، اما مقدار `value` را
  دست‌نخورده به `AngConfigManager.importBatchConfig` می‌دهد؛
- هیچ اندپوینتی نسخهٔ متن‌باز برنمی‌گرداند (`probe-v3.py` سی‌ویک شکل URL را آزمود و همه `404`
  یا `405` بودند — نتیجه در `docs/probe-rows/endpoint-shapes.txt`)؛
- جست‌وجوی هدر/نسخه (`probe-legacy.py`) هم بی‌نتیجه بود: همهٔ `version_code`ها همان blob رمزشده
  را می‌گیرند (`docs/probe-rows/legacy-version-sweep.txt`).

قدم آخر، جست‌وجوی عمومی کد بود: دامنهٔ `managev1.xyz` در مخزن عمومی
[`vefghmhassan/vpn-pannel`](https://github.com/vefghmhassan/vpn-pannel) (پنل مدیریت همین خانوادهٔ
سرویس) ظاهر می‌شود، و در فایل `internal/utils/tools.go` همان پنل تابعی به نام `DecryptValue`
وجود دارد که قاعدهٔ کلید را دقیقاً همین‌طور می‌سازد: `"key_%d"` + پرکردن صفر تا ۱۶ بایت و
`IV = key`. با همان قاعده، نمونهٔ واقعی ردیف‌ها **بدون هیچ تغییری** باز شد.

## ۳) شواهد عددی (اجرای CI، ۱۰۵ ردیف)

`tools/probe-decrypt.py` در GitHub Actions روی پاسخ زندهٔ `/api/v2/protocols` اجرا شد
(خروجی: `docs/probe-rows/decrypt-coverage.txt`):

```
rows: 105
scheme counts: {'json': 6, 'vless': 98, 'trojan': 1}
transport counts: {'vless/xhttp/reality': 2, 'hysteria/?/tls': 1,
                   'vless/tcp/none': 3, 'vless:uri': 98, 'trojan:uri': 1}
failures: 0
decrypt-coverage: 100.00%
```

یعنی **۱۰۵ از ۱۰۵ ردیف** درست باز می‌شوند: ۹۸ لینک `vless`، ۱ لینک `trojan` و ۶ کانفیگ JSON
(که ۲ تای آن `vless` روی `xhttp` با `reality`، ۳ تا `vless` روی `tcp` و یکی `hysteria` است).

نکتهٔ مهم دربارهٔ ابهام قبلی «`value` در هر درخواست عوض می‌شود»: blob برای هر ردیف **قطعی و
ثابت** است؛ آنچه در هر درخواست تغییر می‌کند فقط **ترتیب** ردیف‌هاست. پس کلید، جلسه‌ای نیست و
همان قاعدهٔ بالا همیشه کار می‌کند.

## ۴) نتیجه برای نسخهٔ آزمایشی

- فهرست ۱۰۵ ردیف بدون هیچ ورودی از کاربر گرفته می‌شود، `value` در همان لحظه در خود دستگاه باز
  می‌شود و سرور با هستهٔ Xray + hev-socks5-tunnel (همان پشتهٔ اپ اصلی) بالا می‌آید.
- «پینگ همه» روی همان ۱۰۵ ردیف اجرا می‌شود و سریع‌ترین ردیفی که پاسخ داده **خودکار انتخاب**
  می‌شود؛ کاربر فقط «اتصال» را می‌زند.
- اگر روزی فیلد `value` متن‌باز برگردد یا کاربر کانفیگ خودش را وارد کند، همان مسیر بدون تغییر
  کار می‌کند (`PayloadCipher.unwrap` مقادیر خوانا را دست‌نخورده رد می‌کند).
- ردیفی که پروتکلش را هستهٔ Xray نمی‌تواند اجرا کند (مثل `hysteria`) با برچسب صریح نشان داده
  می‌شود و هرگز وانمود نمی‌کند وصل شده است.
