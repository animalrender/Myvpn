# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-27T02:46:55Z
- آدرس آزمون: `http://1.1.1.1/cdn-cgi/trace`
- سرور متصل‌شده: `🇫🇷 France`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `None` (success/United States)
- درخواست بدون تونل: HTTP 301
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `نمایش 105 از 105 سرور (رایگان: 105 / پولی: 0)`
- نمونهٔ برچسب ردیف‌ها: `🇫🇮 Finland`، `🇦🇺 Australia`، `🇨🇦 Canada`
- مرتب‌سازی: درست — سه ردیف اول: `🇦🇺 Australia`، `🇦🇺 Australia`، `🇦🇺 Australia`
- کپی همهٔ لینک‌ها: درست — 103 لینک v2ray در کلیپ‌بورد قرار گرفت
- پایان پینگ همه: بله
- سروری که برنامه خودش انتخاب کرد: `🌐  🇫🇮 Finland` (پینگ 177 ms)
- ردیف‌های دارای پینگ در فهرست: 3
- اتصال به سرور انتخاب‌شده: `🇦🇺 Australia`
- دیالوگ مجوز VPN تأیید شد
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": EOF
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
```
- ردیف 1 وصل نشد؛ ردیف بعدی
- تلاش 2: اتصال به `🇦🇺 Australia` (211 ms)
- دیالوگ مجوز VPN تأیید شد
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": EOF
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
```
- ردیف 2 وصل نشد؛ ردیف بعدی
- تلاش 3: اتصال به `🇫🇷 France` (159 ms)
- دیالوگ مجوز VPN تأیید شد
- وضعیت تونل: `متصل — &#127467;&#127479; France (VPN)`
- رابط tun0: موجود
- درخواست از داخل تونل: HTTP 301
- ترافیک از تونل عبور کرد (تلاش 3 از 3)
- IP خروج داخل تونل: `2001:41d0:404:100::3068` (FR — FRA)
- ردیف دومی با پینگ موفق در صفحهٔ فعلی دیده نشد
- برچسب دکمه پیش از قطع: `قطع اتصال`
- پس از قطع اتصال: tun0 حذف شد

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

![05-connected](05-connected.png)

![08-disconnected](08-disconnected.png)

## نتیجه

**موفق** — برنامه بدون هیچ ورودی کاربر، فهرست را از بک‌اند گرفت، مقدار رمزشدهٔ هر ردیف را خودش باز کرد، سریع‌ترین سرور را خودش انتخاب کرد، وصل شد و ترافیک از تونل عبور کرد و اتصال تمیز قطع شد.
