# e2e-real — run 36

- branch: arena/b9372ae1-myvpn
- sha: d53589642e9f9d401e31ab3b94aab5b106837957
- started: 2026-10-27T04:20:18Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 27 04:10 /dev/kvm
- booted: 1
- apk: android-app/app/build/outputs/apk/release/app-release.apk
Performing Streamed Install
Success

- e2e exit: 1
- outcome jdk: success
- outcome sdk: success
- outcome chmod: success
- outcome aar: success
- outcome hev: success
- outcome key: success
- outcome gradlesetup: success
- outcome apk: success
- outcome emusetup: success
- outcome drive: failure

## gradle
```
```

---

# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-27T04:30:42Z
- آدرس آزمون: `http://1.1.1.1/cdn-cgi/trace`
- سرور متصل‌شده: `🇫🇮 Finland`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `None` (success/United States)
- درخواست بدون تونل: HTTP 301
- فهرست بارگذاری شد: 3 ردیف روی صفحه — خلاصه: `103/104 پینگ…`
- نمونهٔ برچسب ردیف‌ها: `🇫🇮 Finland`، `🇦🇺 Australia`، `🇨🇦 Canada`
- مرتب‌سازی: ناموفق — گزینهٔ «الفبا · صعودی» در دیالوگ نبود
- کپی همهٔ لینک‌ها: درست — 103 لینک v2ray در کلیپ‌بورد قرار گرفت
- پایان پینگ همه: بله
- سروری که برنامه خودش انتخاب کرد: `🌐  🇫🇮 Finland` (پینگ 195 ms)
- ردیف‌های دارای پینگ در فهرست: 25
- اتصال به سرور انتخاب‌شده: `🇫🇮 Finland`
- دیالوگ مجوز VPN تأیید شد
- وضعیت تونل: `متصل — &#127467;&#127470; Finland (VPN)`
- رابط tun0: موجود
- درخواست از داخل تونل: HTTP 301
- ترافیک از تونل عبور کرد (تلاش 1 از 3)
- IP خروج داخل تونل: `2a01:4f9:c010:7583::1` (FI — HEL)
- ردیف‌های نامزد برای تغییر سرور: 24 (از 25 ردیف دارای پینگ)
- تغییر سرور به: `🇨🇦 Canada` (175 ms)
- وضعیت تونل: `متصل — &#127464;&#127462; Canada (VPN)`
- برچسب دکمه پس از انتخاب سرور دوم: `قطع اتصال`
- درخواست پس از تغییر سرور: HTTP no-response
- تغییر سرور به: `🇺🇸 United States` (129 ms)
- وضعیت تونل: `متصل — &#127482;&#127480; United States (VPN)`
- برچسب دکمه پس از انتخاب سرور دوم: `قطع اتصال`
- درخواست پس از تغییر سرور: HTTP 301
- برچسب دکمه پیش از قطع: `قطع اتصال`
- پس از قطع اتصال: tun0 حذف شد

## تصاویر

![01-loaded](01-loaded.png)

![04-copy-all-dialog](04-copy-all-dialog.png)

![02-ping-all](02-ping-all.png)

![03-selected](03-selected.png)

![03-connected](03-connected.png)

![07-selected](07-selected.png)

![07-connected](07-connected.png)

![07-selected](07-selected.png)

![07-connected](07-connected.png)

![08-disconnected](08-disconnected.png)

## نتیجه

**ناموفق**: sort-not-applied, probe-after-switch-no-response
