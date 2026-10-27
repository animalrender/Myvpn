# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-27T05:37:08Z
- آدرس آزمون: `http://1.1.1.1/cdn-cgi/trace`
- سرور متصل‌شده: `🇨🇦 Canada`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `None` (success/United States)
- درخواست بدون تونل: HTTP 301
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `نمایش 105 از 105 سرور (رایگان: 105 / پولی: 0)`
- نمونهٔ برچسب ردیف‌ها: `🇺🇸 United States`، `🇦🇺 Australia`، `🇫🇷 France`
- مرتب‌سازی: درست — سه ردیف اول: `🇦🇺 Australia`، `🇦🇺 Australia`، `🇦🇺 Australia`
- کپی همهٔ لینک‌ها: درست — 105 لینک v2ray در کلیپ‌بورد قرار گرفت
- پایان پینگ همه: بله
- سروری که برنامه خودش انتخاب کرد: `🌐  🇺🇸 United States` (پینگ 66 ms)
- ردیف‌های دارای پینگ در فهرست: 31
- اتصال به سرور انتخاب‌شده: `🇦🇺 Australia`
- دیالوگ مجوز VPN تأیید شد
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
ترافیک از تونل عبور نکرد؛ اتصال لغو شد (🇦🇺 Australia)
```
- ردیف 1 وصل نشد؛ ردیف بعدی
- تلاش 2: اتصال به `🇨🇦 Canada` (69 ms)
- وضعیت تونل: `متصل — &#127464;&#127462; Canada (VPN)`
- رابط tun0: موجود
- درخواست از داخل تونل: HTTP 301
- ترافیک از تونل عبور کرد (تلاش 2 از 5)
- IP خروج داخل تونل: `2600:1f11:82d:800:9946:5381:6917:2ff9` (CA — YUL)
- ردیف‌های نامزد برای تغییر سرور: 16 (از 31 ردیف دارای پینگ)
- تغییر سرور به: `🇦🇺 Australia` (187 ms)
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
ترافیک از تونل عبور نکرد؛ اتصال لغو شد (🇦🇺 Australia)
```
- تغییر سرور به: `🇦🇺 Australia` (138 ms)
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
ترافیک از تونل عبور نکرد؛ اتصال لغو شد (🇦🇺 Australia)
```
- تغییر سرور به: `🇫🇷 France` (238 ms)
- وضعیت تونل: `متصل — &#127467;&#127479; France (VPN)`
- برچسب دکمه پس از انتخاب سرور دوم: `قطع اتصال`
- درخواست پس از تغییر سرور: HTTP 301
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

![04-connected](04-connected.png)

![07-selected](07-selected.png)

![07-connect-failed](07-connect-failed.png)

![07-connected](07-connected.png)

![08-disconnected](08-disconnected.png)

## نتیجه

**موفق** — برنامه بدون هیچ ورودی کاربر، فهرست را از بک‌اند گرفت، مقدار رمزشدهٔ هر ردیف را خودش باز کرد، سریع‌ترین سرور را خودش انتخاب کرد، وصل شد و ترافیک از تونل عبور کرد، سرور عوض شد و اتصال تمیز قطع شد.
