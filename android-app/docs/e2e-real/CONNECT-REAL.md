# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-26T16:05:59Z
- آدرس آزمون: `http://1.1.1.1/cdn-cgi/trace`
- سرور متصل‌شده: `🌐  🇫🇮 Finland`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `None` (success/United States)
- درخواست بدون تونل: HTTP 301
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `نمایش 105 از 105 سرور (رایگان: 105 / پولی: 0)`
- نمونهٔ برچسب ردیف‌ها: `🇫🇮 Finland`، `🇫🇮 Finland`، `🇫🇷 France`
- پایان پینگ همه: بله
- سروری که برنامه خودش انتخاب کرد: `🌐  🇫🇮 Finland`
- اتصال به سرور انتخاب‌شده: `🌐  🇫🇮 Finland`
- دیالوگ مجوز VPN تأیید شد
- وضعیت تونل: `متصل — &#127467;&#127470; Finland (VPN)`
- رابط tun0: موجود
- درخواست از داخل تونل: HTTP 301
- ترافیک از تونل عبور کرد (تلاش 1 از 2)
- IP خروج داخل تونل: `2a01:4f9:c010:7583::1` (FI — HEL)
- تغییر سرور به: `🇫🇮 Finland` (142 ms)
- خطاهای برنامه:
```
10-26 16:00:17.523  3407  3676 E MvpnTrial: 	at kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:111)
10-26 16:00:17.523  3407  3676 E MvpnTrial: 	at kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:99)
10-26 16:00:17.523  3407  3676 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:584)
10-26 16:00:17.523  3407  3676 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:811)
10-26 16:00:17.523  3407  3676 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:715)
10-26 16:00:17.523  3407  3676 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:702)
```
- دکمه در وضعیت «اتصال» است؛ ابتدا ردیف متصل انتخاب می‌شود: `🌐  🇫🇮 Finland`
- وضعیت تونل: `متصل — &#127467;&#127470; Finland (VPN)`
- برچسب دکمه پیش از قطع: `قطع اتصال`
- پس از قطع اتصال: tun0 حذف شد

## تصاویر

![01-loaded](01-loaded.png)

![02-ping-all](02-ping-all.png)

![03-selected](03-selected.png)

![03-connected](03-connected.png)

![07-selected](07-selected.png)

![07-connect-failed](07-connect-failed.png)

![07-selected](07-selected.png)

![07-connected](07-connected.png)

![08-disconnected](08-disconnected.png)

## نتیجه

**ناموفق**: switch-failed
