# e2e-real — run 32

- branch: arena/b9372ae1-myvpn
- sha: 88fb9374bce2786df0509d7560d243c913fb7b69
- started: 2026-10-27T02:50:57Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 27 02:47 /dev/kvm
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
e: The daemon has terminated unexpectedly on startup attempt #1 with error code: 0. The daemon process output:
    1. Kotlin compile daemon is ready
w: file:///home/runner/work/Myvpn/Myvpn/android-app/app/src/main/java/co/asiven/vixentvpn/trial/ui/MainActivity.kt:142:29 'fun setOnCheckedChangeListener(p0: ChipGroup.OnCheckedChangeListener?): Unit' is deprecated. Deprecated in Java.

> Task :app:compileReleaseJavaWithJavac
> Task :app:dexBuilderRelease
> Task :app:mergeReleaseGlobalSynthetics
```

---

# آزمون اتصال واقعی به بک‌اند اصلی (بدون هیچ ورودی کاربر)

- زمان: 2026-10-27T02:58:00Z
- آدرس آزمون: `http://1.1.1.1/cdn-cgi/trace`

## گام‌ها

- پاک‌کردن دادهٔ برنامه (بدون کش، بدون کانفیگ ذخیره‌شده)
- ابزار HTTP روی شبیه‌ساز: `nc`
- IP خروج پیش از اتصال: `None` (success/United States)
- درخواست بدون تونل: HTTP 301
- **هیچ سروری از بک‌اند بارگذاری نشد**

## تصاویر

![01-loaded](01-loaded.png)

## نتیجه

**ناموفق**: no-rows
