# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-26T15:43:09Z
- آدرس آزمون: `http://1.1.1.1/cdn-cgi/trace`
- سرور متصل‌شده: `🇫🇷 France`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `None` (success/United States)
- درخواست بدون تونل: HTTP 301
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `نمایش 105 از 105 سرور (رایگان: 105 / پولی: 0)`
- نمونهٔ برچسب ردیف‌ها: `🇦🇺 Australia`، `🇸🇪 Sweden`، `🇫🇷 France`
- پایان پینگ همه: بله
- سروری که برنامه خودش انتخاب کرد: `🌐  🇦🇺 Australia`
- اتصال به سرور انتخاب‌شده: `🌐  🇦🇺 Australia`
- دیالوگ مجوز VPN تأیید شد
- وضعیت تونل: `متصل — &#127462;&#127482; Australia (VPN)`
- رابط tun0: موجود
- درخواست از داخل تونل: HTTP no-response
- درخواست از داخل تونل: HTTP no-response
- درخواست از داخل تونل: HTTP no-response
- ترافیک از این ردیف عبور نکرد؛ سرور بعدی آزموده می‌شود
- تلاش 2: اتصال به `🇦🇺 Australia`
- خطاهای برنامه:
```
10-26 15:34:57.937  3571  3764 E MvpnTrial: 	at kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:111)
10-26 15:34:57.937  3571  3764 E MvpnTrial: 	at kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:99)
10-26 15:34:57.937  3571  3764 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:584)
10-26 15:34:57.937  3571  3764 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:811)
10-26 15:34:57.937  3571  3764 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:715)
10-26 15:34:57.937  3571  3764 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:702)
```
- تلاش 3: اتصال به `🇫🇷 France`
- وضعیت تونل: `متصل — &#127467;&#127479; France (VPN)`
- رابط tun0: موجود
- درخواست از داخل تونل: HTTP 301
- IP خروج داخل تونل: `2001:41d0:404:100::10ea` (FR — FRA)
- ردیف دومی با پینگ موفق در صفحهٔ فعلی دیده نشد
- برچسب دکمه پیش از قطع: `قطع اتصال`
- پس از قطع اتصال: tun0 حذف شد

## تصاویر

![01-loaded](01-loaded.png)

![02-ping-all](02-ping-all.png)

![03-selected](03-selected.png)

![03-connected](03-connected.png)

![04-selected](04-selected.png)

![04-connect-failed](04-connect-failed.png)

![05-selected](05-selected.png)

![05-connected](05-connected.png)

![08-disconnected](08-disconnected.png)

## نتیجه

**ناموفق**: no-traffic-1, not-connected-2
