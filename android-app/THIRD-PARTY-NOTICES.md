# Third-party notices — MVPN Trial

این اپ چند مؤلفهٔ شخص ثالث را در زمان ساخت (در CI) دانلود/کامپایل می‌کند و در APK قرار می‌دهد.
هیچ‌کدام از این فایل‌ها داخل مخزن کامیت نمی‌شوند (`app/libs/*.aar`، `app/src/main/jniLibs/`،
`signing/` در `.gitignore` هستند).

| مؤلفه | نسخهٔ پین‌شده | مجوز | منبع | محل استفاده |
| --- | --- | --- | --- | --- |
| `libv2ray.aar` (AndroidLibXrayLite) | `v26.6.27` | GPL-3.0 | https://github.com/2dust/AndroidLibXrayLite | `core/XrayCore.kt` — اجرای هسته و پینگ |
| Xray-core (داخل همان AAR) | build 2026-06-27 | MPL-2.0 | https://github.com/XTLS/Xray-core | موتور پروتکل‌ها |
| hev-socks5-tunnel | `2.19.3` | GPL-3.0 | https://github.com/heiher/hev-socks5-tunnel | `service/HevTunnel.kt` + `TProxyService.java` — TUN→SOCKS |
| AndroidX Core / AppCompat / RecyclerView / CardView / ConstraintLayout / Lifecycle | طبق `app/build.gradle.kts` | Apache-2.0 | https://developer.android.com/jetpack | رابط کاربری |
| Material Components for Android | `1.12.0` | Apache-2.0 | https://github.com/material-components/material-components-android | تم Material 3 |
| Kotlin Coroutines | `1.8.1` | Apache-2.0 | https://github.com/Kotlin/kotlinx.coroutines | کارهای پس‌زمینه |
| Firebase Messaging | `24.0.2` | Google APIs Terms | https://firebase.google.com | دریافت توکن FCM (`firebase_token`) |

## چرا GPL مهم است

`libv2ray.aar` و `hev-socks5-tunnel` هر دو GPL-3.0 هستند. اگر APK این پروژه را **عمومی توزیع**
می‌کنید، توزیع شما هم تحت GPL-3.0 خواهد بود و باید:

1. متن مجوز GPL-3.0 را همراه توزیع بگذارید؛
2. سورس کامل (شامل تغییرات محلی) را در دسترس بگذارید؛
3. اعلان‌های کپی‌رایت/مجوز مؤلفه‌ها را حذف نکنید.

فایل‌های سورس مؤلفه‌های GPL از مخازن بالا در دسترس‌اند و اسکریپت ساخت آن‌ها در
[`tools/fetch-libv2ray.sh`](tools/fetch-libv2ray.sh) و [`tools/build-hevtun.sh`](tools/build-hevtun.sh)
قابل بازتولید است (تگ نسخه‌ها در همین اسکریپت‌ها پین شده‌اند).

## کلید امضا

APK با **AOSP testkey** امضا می‌شود
(`SHA-256: a40da80a59d170caa950cf15c18c454d47a39b26989d8b640ecd745ba71bf5dc`). این کلید عمومی و
آزمایشی است و در مخزن AOSP منتشر شده؛ صرفاً برای تطبیق هدرهای `sign`/`sha_hexadecimal` با بک‌اند
استفاده می‌شود و هیچ نقش امنیتی برای محافظت از محتوای APK ندارد.

## نام‌های تجاری

این پروژه یک کلاینت **آزمایشی/شخصی** برای تحلیل رفتار یک اپ اندروید است. هیچ ارتباط رسمی با
سازندهٔ اپ اصلی یا اپراتور بک‌اند ندارد و نام‌ها/نشان‌های تجاری متعلق به صاحبان آن‌هاست.
