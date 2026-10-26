# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-26T14:22:20Z
- آدرس آزمون: `http://connectivitycheck.gstatic.com/generate_204`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `None` (success/United States)
- درخواست بدون تونل: HTTP 204
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `نمایش 105 از 105 سرور (رایگان: 105 / پولی: 0)`
- نمونهٔ برچسب ردیف‌ها: `🇺🇸 United States`، `🇸🇪 Sweden`، `🇩🇪 Germany`
- پایان پینگ همه: بله
- سروری که برنامه خودش انتخاب کرد: `🌐  🇺🇸 United States`
- اتصال به سرور انتخاب‌شده: `🌐  🇺🇸 United States`
- دیالوگ مجوز VPN تأیید شد
- خطاهای برنامه:
```
10-26 14:19:27.701  3400  3675 E MvpnTrial: 	at kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:111)
10-26 14:19:27.701  3400  3675 E MvpnTrial: 	at kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:99)
10-26 14:19:27.701  3400  3675 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:584)
10-26 14:19:27.701  3400  3675 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:811)
10-26 14:19:27.701  3400  3675 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:715)
10-26 14:19:27.701  3400  3675 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:702)
```
- تلاش 2: اتصال به `🇸🇪 Sweden`
- دیالوگ مجوز VPN تأیید شد
- وضعیت تونل: `متصل — &#127480;&#127466; Sweden (VPN)`
- رابط tun0: موجود
- درخواست از داخل تونل: HTTP no-response
- درخواست از داخل تونل: HTTP no-response
- درخواست از داخل تونل: HTTP no-response
- ترافیک از این ردیف عبور نکرد؛ سرور بعدی آزموده می‌شود

## تصاویر

![01-loaded](01-loaded.png)

![02-ping-all](02-ping-all.png)

![03-selected](03-selected.png)

![03-connect-failed](03-connect-failed.png)

![04-selected](04-selected.png)

![04-connected](04-connected.png)

## نتیجه

**ناموفق**: not-connected-1, no-traffic-2, no-server-passed-traffic
