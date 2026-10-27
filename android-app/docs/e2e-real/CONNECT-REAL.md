# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-27T01:16:49Z
- آدرس آزمون: `http://1.1.1.1/cdn-cgi/trace`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `None` (success/United States)
- درخواست بدون تونل: HTTP 301
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `نمایش 105 از 105 سرور (رایگان: 105 / پولی: 0)`
- نمونهٔ برچسب ردیف‌ها: `🇫🇮 Finland`، `🇫🇮 Finland`، `🇫🇷 France`
- مرتب‌سازی: درست — سه ردیف اول: `🇦🇺 Australia`، `🇦🇺 Australia`، `🇦🇺 Australia`
- کپی همهٔ لینک‌ها: درست — 102 لینک v2ray در کلیپ‌بورد قرار گرفت
- پایان پینگ همه: بله
- سروری که برنامه خودش انتخاب کرد: `🌐  🇫🇮 Finland` (پینگ 191 ms)
- ردیف‌های دارای پینگ در فهرست: 9
- اتصال به سرور انتخاب‌شده: `🇦🇺 Australia`
- دیالوگ مجوز VPN تأیید شد
- خطاهای برنامه:
```
10-27 01:02:38.415  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:111)
10-27 01:02:38.415  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:99)
10-27 01:02:38.415  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:584)
10-27 01:02:38.415  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:811)
10-27 01:02:38.415  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:715)
10-27 01:02:38.415  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:702)
```
- ردیف 1 وصل نشد؛ ردیف بعدی
- تلاش 2: اتصال به `🇨🇦 Canada` (75 ms)
- خطاهای برنامه:
```
10-27 01:04:37.203  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:111)
10-27 01:04:37.203  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:99)
10-27 01:04:37.203  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:584)
10-27 01:04:37.203  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:811)
10-27 01:04:37.203  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:715)
10-27 01:04:37.203  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:702)
```
- ردیف 2 وصل نشد؛ ردیف بعدی
- تلاش 3: اتصال به `🇨🇦 Canada` (71 ms)
- خطاهای برنامه:
```
10-27 01:10:54.189  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.internal.LimitedDispatcher$Worker.run(LimitedDispatcher.kt:111)
10-27 01:10:54.189  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.TaskImpl.run(Tasks.kt:99)
10-27 01:10:54.189  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler.runSafely(CoroutineScheduler.kt:584)
10-27 01:10:54.189  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.executeTask(CoroutineScheduler.kt:811)
10-27 01:10:54.189  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.runWorker(CoroutineScheduler.kt:715)
10-27 01:10:54.189  3421  3685 E MvpnTrial: 	at kotlinx.coroutines.scheduling.CoroutineScheduler$Worker.run(CoroutineScheduler.kt:702)
```
- ردیف 3 وصل نشد؛ ردیف بعدی

## تصاویر

![01-loaded](01-loaded.png)

![03-sorted](03-sorted.png)

![04-copy-all-dialog](04-copy-all-dialog.png)

![02-ping-all](02-ping-all.png)

![03-selected](03-selected.png)

![03-connect-failed](03-connect-failed.png)

![04-selected](04-selected.png)

![04-connect-failed](04-connect-failed.png)

![05-selected](05-selected.png)

![05-connect-failed](05-connect-failed.png)

## نتیجه

**ناموفق**: no-server-passed-traffic
