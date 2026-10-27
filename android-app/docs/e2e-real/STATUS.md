# e2e-real — run 33

- branch: arena/b9372ae1-myvpn
- sha: c069fc1d184078fa7d5ce8c0fd3f6594f062ead5
- started: 2026-10-27T03:18:47Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 27 03:13 /dev/kvm
- booted: 1
- apk: android-app/app/build/outputs/apk/release/app-release.apk
Performing Streamed Install
Success

- e2e exit: 1
- outcome jdk: success
- outcome sdk: success
- outcome chmod: success
- outcome aar: success
- outcome hev: success
- outcome key: success
- outcome gradlesetup: success
- outcome apk: success
- outcome emusetup: success
- outcome drive: failure

## gradle
```
```

---

# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-27T03:30:07Z
- آدرس آزمون: `http://1.1.1.1/cdn-cgi/trace`
- IP خروج پیش از اتصال: `20.161.30.200`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `20.161.30.200` (success/United States)
- درخواست بدون تونل: HTTP 301
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `نمایش 105 از 105 سرور (رایگان: 105 / پولی: 0)`
- نمونهٔ برچسب ردیف‌ها: `🇺🇸 United States`، `🇨🇦 Canada`، `🇸🇪 Sweden`
- مرتب‌سازی: درست — سه ردیف اول: `🇦🇺 Australia`، `🇦🇺 Australia`، `🇦🇺 Australia`
- کپی همهٔ لینک‌ها: درست — 105 لینک v2ray در کلیپ‌بورد قرار گرفت
- پایان پینگ همه: بله
- سروری که برنامه خودش انتخاب کرد: `🌐  🇺🇸 United States` (پینگ 25 ms)
- ردیف‌های دارای پینگ در فهرست: 2
- اتصال به سرور انتخاب‌شده: `🇩🇪 Germany`
- دیالوگ مجوز VPN تأیید شد
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
تجزیهٔ پیکربندی ناموفق: هستهٔ Xray اتصال vless بدون TLS به IP عمومی (57.129.89.152) را رد می‌کند؛ این ردیف با این هسته قابل استفاده نیست
```
- ردیف 1 وصل نشد؛ ردیف بعدی
- تلاش 2: اتصال به `🇩🇪 Germany` (106 ms)
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
تجزیهٔ پیکربندی ناموفق: هستهٔ Xray اتصال vless بدون TLS به IP عمومی (57.129.89.152) را رد می‌کند؛ این ردیف با این هسته قابل استفاده نیست
```
- ردیف 2 وصل نشد؛ ردیف بعدی

## تصاویر

![01-loaded](01-loaded.png)

![03-sorted](03-sorted.png)

![04-copy-all-dialog](04-copy-all-dialog.png)

![02-ping-all](02-ping-all.png)

![03-selected](03-selected.png)

![03-connect-failed](03-connect-failed.png)

![04-selected](04-selected.png)

![04-connect-failed](04-connect-failed.png)

## نتیجه

**ناموفق**: no-server-passed-traffic
- outcome jdk: success
- outcome sdk: success
- outcome chmod: success
- outcome aar: success
- outcome hev: success
- outcome key: success
- outcome gradlesetup: success
- outcome apk: failure
- outcome emusetup: skipped
- outcome drive: skipped

## gradle
```
e: The daemon has terminated unexpectedly on startup attempt #1 with error code: 0. The daemon process output:
    1. Kotlin compile daemon is ready
e: file:///home/runner/work/Myvpn/Myvpn/android-app/app/src/main/java/co/asiven/vixentvpn/trial/core/XrayCore.kt:58:36 Too many arguments for 'fun startLoop(p0: String!): Unit'.

> Task :app:compileReleaseKotlin FAILED
> Task :app:mergeExtDexRelease
gradle/actions: Writing build results to /home/runner/work/_temp/.gradle-actions/build-results/apk-1793072588530.json

FAILURE: Build failed with an exception.
> Task :app:compileReleaseKotlin FAILED
FAILURE: Build failed with an exception.
* What went wrong:
```

---

# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-27T03:30:07Z
- آدرس آزمون: `http://1.1.1.1/cdn-cgi/trace`
- IP خروج پیش از اتصال: `20.161.30.200`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `20.161.30.200` (success/United States)
- درخواست بدون تونل: HTTP 301
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `نمایش 105 از 105 سرور (رایگان: 105 / پولی: 0)`
- نمونهٔ برچسب ردیف‌ها: `🇺🇸 United States`، `🇨🇦 Canada`، `🇸🇪 Sweden`
- مرتب‌سازی: درست — سه ردیف اول: `🇦🇺 Australia`، `🇦🇺 Australia`، `🇦🇺 Australia`
- کپی همهٔ لینک‌ها: درست — 105 لینک v2ray در کلیپ‌بورد قرار گرفت
- پایان پینگ همه: بله
- سروری که برنامه خودش انتخاب کرد: `🌐  🇺🇸 United States` (پینگ 25 ms)
- ردیف‌های دارای پینگ در فهرست: 2
- اتصال به سرور انتخاب‌شده: `🇩🇪 Germany`
- دیالوگ مجوز VPN تأیید شد
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
تجزیهٔ پیکربندی ناموفق: هستهٔ Xray اتصال vless بدون TLS به IP عمومی (57.129.89.152) را رد می‌کند؛ این ردیف با این هسته قابل استفاده نیست
```
- ردیف 1 وصل نشد؛ ردیف بعدی
- تلاش 2: اتصال به `🇩🇪 Germany` (106 ms)
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
تجزیهٔ پیکربندی ناموفق: هستهٔ Xray اتصال vless بدون TLS به IP عمومی (57.129.89.152) را رد می‌کند؛ این ردیف با این هسته قابل استفاده نیست
```
- ردیف 2 وصل نشد؛ ردیف بعدی

## تصاویر

![01-loaded](01-loaded.png)

![03-sorted](03-sorted.png)

![04-copy-all-dialog](04-copy-all-dialog.png)

![02-ping-all](02-ping-all.png)

![03-selected](03-selected.png)

![03-connect-failed](03-connect-failed.png)

![04-selected](04-selected.png)

![04-connect-failed](04-connect-failed.png)

## نتیجه

**ناموفق**: no-server-passed-traffic
