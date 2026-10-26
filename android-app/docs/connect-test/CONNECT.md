# آزمون اتصال واقعی (CI)

- زمان: 2026-10-26T05:35:28Z
- سرورهای آزمون: `CI-Local-A`, `CI-Local-B`
- آدرس آزمون: `https://www.gstatic.com/generate_204`

## گام‌ها

- ورود کانفیگ اول با intent: `vless://11111111-2222-3333-4444-555555555555@10.0.2.2:10086?…`
- کانفیگ «CI-Local-A» در فهرست دیده شد
- دکمهٔ اتصال زده شد
- دیالوگ مجوز VPN تأیید شد
- وضعیت «متصل — CI-Local-A» دیده شد
- رابط tun0: موجود
- درخواست از پوستهٔ ادمین (HTTPS): خروجی='204' — ردِ سرور: دیده شد (617 بایت لاگ تازه)
-   نمونهٔ لاگ سرور: `2026/10/26 05:34:17.329471 from 127.0.0.1:38438 accepted tcp:www.gstatic.com:80`
- درخواست از پوستهٔ ادمین (HTTP): خروجی='204' — ردِ سرور: دیده شد (581 بایت لاگ تازه)
-   نمونهٔ لاگ سرور: `2026/10/26 05:34:21.598813 from 127.0.0.1:38502 accepted tcp:connectivitycheck.gstatic.com:80`
- اجرای «پینگ همه» و بررسی اینکه سرور متصل عوض نشود
- وضعیت بعد از پینگ همه: `متصل — CI-Local-A (VPN)`
- ورود کانفیگ دوم: `vmess://eyJ2IjoiMiIsInBzIjoiQ0ktTG9jYWwtQiIsImFkZCI6IjEwLjAu…`
- برچسب دکمهٔ اتصال در این حالت: `قطع اتصال`
- دکمهٔ زده‌شده: `قطع اتصال`
- درخواست تغییر سرور زده شد
- تونل به «CI-Local-B» منتقل شد
- درخواست از پوستهٔ ادمین (HTTPS بعد از تغییر سرور): خروجی='204' — ردِ سرور: دیده شد (164 بایت لاگ تازه)
-   نمونهٔ لاگ سرور: `2026/10/26 05:35:14.692946 from 127.0.0.1:59542 accepted tcp:www.gstatic.com:80`
- پس از قطع: tun0 حذف شد

## تصاویر

![01-imported](01-imported.png)

![02-selected](02-selected.png)

![03-connected](03-connected.png)

![04-traffic](04-traffic.png)

![05-ping-all](05-ping-all.png)

![06-second-imported](06-second-imported.png)

![07-switched](07-switched.png)

![08-disconnected](08-disconnected.png)

## نتیجه

**ناموفق**: switch-label
