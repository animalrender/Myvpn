# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-26T12:13:29Z
- آدرس آزمون: `http://connectivitycheck.gstatic.com/generate_204`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `None` (success/United States)
- درخواست بدون تونل: HTTP 204
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `نمایش 105 از 105 سرور (رایگان: 105 / پولی: 0)`
- نمونهٔ برچسب ردیف‌ها: `🇫🇮 Finland`، `🇫🇮 Finland`، `🇦🇺 Australia`
- پایان پینگ همه: بله
- سروری که برنامه خودش انتخاب کرد: `🌐  🇫🇮 Finland`
- اتصال به سرور انتخاب‌شده: `🌐  🇫🇮 Finland`
- دیالوگ مجوز VPN تأیید شد
- وضعیت تونل: `متصل — &#127467;&#127470; Finland (VPN)`
- رابط tun0: موجود
- درخواست از داخل تونل: HTTP 204
- IP خروج داخل تونل: `65.109.210.46` (success — Finland)
- تغییر سرور به: `🇫🇮 Finland` (143 ms)
- وضعیت تونل: `متصل — &#127467;&#127470; Finland (VPN)`
- **خطای غیرمنتظره در درایور آزمون**: `NameError: name 'connect_button_text' is not defined`

## تصاویر

![01-loaded](01-loaded.png)

![02-ping-all](02-ping-all.png)

![03-selected](03-selected.png)

![03-connected](03-connected.png)

![04-selected](04-selected.png)

![04-connected](04-connected.png)

## نتیجه

**ناموفق**: driver-crash, NameError
