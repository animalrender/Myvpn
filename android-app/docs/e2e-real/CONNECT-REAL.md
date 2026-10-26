# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-26T13:53:33Z
- آدرس آزمون: `http://connectivitycheck.gstatic.com/generate_204`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `None` (success/United States)
- درخواست بدون تونل: HTTP 204
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `نمایش 105 از 105 سرور (رایگان: 105 / پولی: 0)`
- نمونهٔ برچسب ردیف‌ها: `🇫🇮 Finland`، `🇺🇸 United States`، `🇸🇪 Sweden`
- **خطای غیرمنتظره در درایور آزمون**: `NameError: name 'bulk_ping_finished' is not defined`

## تصاویر

![01-loaded](01-loaded.png)

## نتیجه

**ناموفق**: driver-crash, NameError
