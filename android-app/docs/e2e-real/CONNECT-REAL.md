# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-27T01:43:03Z
- آدرس آزمون: `http://1.1.1.1/cdn-cgi/trace`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `None` (success/United States)
- درخواست بدون تونل: HTTP 301
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `نمایش 105 از 105 سرور (رایگان: 105 / پولی: 0)`
- نمونهٔ برچسب ردیف‌ها: `🇨🇦 Canada`، `🇸🇪 Sweden`، `🇩🇪 Germany`
- مرتب‌سازی: درست — سه ردیف اول: `🇦🇺 Australia`، `🇦🇺 Australia`، `🇦🇺 Australia`
- کپی همهٔ لینک‌ها: درست — 103 لینک v2ray در کلیپ‌بورد قرار گرفت
- پایان پینگ همه: بله
- سروری که برنامه خودش انتخاب کرد: `🌐  🇺🇸 United States` (پینگ 18 ms)
- ردیف‌های دارای پینگ در فهرست: 9
- اتصال به سرور انتخاب‌شده: `🇨🇦 Canada`
- دیالوگ مجوز VPN تأیید شد
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: config load error: infra/conf/serial: failed to parse json config > infra/conf: failed to build outbound config with tag proxy > infra/conf: vless without TLS or other encryption is prohibited unless the server address is a private IP or domain
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
```
- ردیف 1 وصل نشد؛ ردیف بعدی
- تلاش 2: اتصال به `🇨🇦 Canada` (74 ms)
- دیالوگ مجوز VPN تأیید شد
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: config load error: infra/conf/serial: failed to parse json config > infra/conf: failed to build outbound config with tag proxy > infra/conf: vless without TLS or other encryption is prohibited unless the server address is a private IP or domain
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
```
- ردیف 2 وصل نشد؛ ردیف بعدی
- تلاش 3: اتصال به `🇨🇦 Canada` (77 ms)
- دیالوگ مجوز VPN تأیید شد
- خطاهای برنامه:
```
سنجش تأخیر ناموفق
go.Universe$proxyerror: config load error: infra/conf/serial: failed to parse json config > infra/conf: failed to build outbound config with tag proxy > infra/conf: vless without TLS or other encryption is prohibited unless the server address is a private IP or domain
go.Universe$proxyerror: Get "https://www.gstatic.com/generate_204": io: read/write on closed pipe
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
