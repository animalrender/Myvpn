# معماری نسخهٔ آزمایشی

## ۱) هدف طراحی

اپ اصلی یک کلاینت Xray است (پایهٔ v2rayNG) که سرورها را از بک‌اند خودش می‌گیرد، تبلیغ
(Admob/FairBid) نشان می‌دهد، برای سرورهای پولی سکه/اشتراک می‌فروشد و منطق زمان اتصال و
پاداش دارد. نسخهٔ آزمایشی **همان مسیر فنی** را نگه می‌دارد و لایه‌های تجاری را حذف می‌کند:

```
┌─────────────────────────────── MVPN Trial ───────────────────────────────┐
│ MainActivity (RTL، تم تیره)                                              │
│   ├── دکمهٔ «دریافت و بازآوری همهٔ سرورها» → ApiClient                     │
│   ├── ServerAdapter (RecyclerView) → برچسب‌ها، پینگ، انتخاب، کپی لینک      │
│   └── دکمهٔ اتصال/قطع + انتخاب حالت (VPN / PROXY)                          │
│                                                                          │
│ ApiClient  ── headers(sign، sha_hexadecimal، token، …) ──► managev1.xyz  │
│ ConfigBuilder: value → outbound Xray → کانفیگ اجرا/پینگ/لینک اشتراک       │
│                                                                          │
│ VpnTunnelService (Foreground)                                            │
│   ├── mode=VPN : VpnService → TUN 10.10.10.2/24, MTU 1500 → tunFd         │
│   └── mode=PROXY: tunFd = 0 (فقط SOCKS/HTTP محلی)                        │
│            │                                                             │
│            ├── HevTunnel → TProxyService(jni) → hev-socks5-tunnel        │
│            └── XrayCore  → libv2ray.aar → xray-core (libgojni.so)        │
└──────────────────────────────────────────────────────────────────────────┘
```

## ۲) چرا این دو کتابخانه؟

اپ اصلی در `lib/arm64-v8a/` این‌ها را دارد: `libgojni.so` (هستهٔ gomobile اکستری)،
`libtun2socks.so` (BadVPN tun2socks)، `libmmkv.so`، `libstub.so` (Dex2C). مسیر بازتولیدپذیر:

- **`libv2ray.aar`** از [AndroidLibXrayLite](https://github.com/2dust/AndroidLibXrayLite) (تگ
  `v26.10.21`) — همان build گوموبایل `xtls/xray-core`. API استفاده‌شده:
  `Libv2ray.initCoreEnv(assetPath, xudpKey)`، `Libv2ray.newCoreController(handler)`،
  `controller.startLoop(config, tunFd)`، `controller.stopLoop()`،
  `Libv2ray.measureOutboundDelay(config, testUrl)`، `Libv2ray.checkVersionX()`.
- **`hev-socks5-tunnel`** (تگ `2.19.3`) — جانشین `libtun2socks.so` با همان نقش؛ سورس در CI با
  `ndk-build` و ثابت‌های `-DPKGNAME=co/asiven/vixentvpn/service -DCLSNAME=TProxyService` ساخته
  می‌شود تا `JNI_OnLoad` کلاس اعلان‌کنندهٔ متدهای native را پیدا کند.

`TProxyService.java` عمداً جاوا است (نه Kotlin) تا نام/امضای متدهای native صد‌درصد مطابق
`RegisterNatives` در `hev-jni.c` باشد:

```java
public static native boolean TProxyStartService(String configPath, int fd);
public static native boolean TProxyStopService();
public static native boolean TProxyIsRunning();
public static long[] TProxyGetStats();
```

## ۳) پیکربندی TUN و hev

`VpnTunnelService` (بر اساس رفتار `VpnTunnelService`/`CoreVpnService` اپ اصلی و v2rayNG):

| مورد | مقدار |
| --- | --- |
| MTU | 1500 |
| آدرس TUN | `10.10.10.2/24` |
| مسیر | `0.0.0.0/0` (همه ترافیک) |
| DNS | `1.1.1.1`، `8.8.8.8` |
| استثنا | `addDisallowedApplication(ownPackage)` تا خود اپ از تونل خارج بماند |

`HevTunnel` فایل `tunnel.ini` را می‌نویسد (همان شکل `conf/main.yml` پروژهٔ hev):

```yaml
tunnel:
  mtu: 1500
  ipv4: 10.10.10.2
socks5:
  port: 10808
  address: 127.0.0.1
  udp: udp
misc:
  task-stack-size: 86016
  connect-timeout: 10000
  log-level: warn
```

## ۴) کانفیگ Xray

`ConfigBuilder.runtimeConfig(outbound)`:

- inbound «socks» روی `127.0.0.1:10808` (با `udp: true` و sniffing `http,tls`)
- inbound «http» روی `127.0.0.1:10809`
- outbound سرور (`tag=proxy`) + `direct` (freedom) + `block` (blackhole)
- routing فقط برای شبکه‌های خصوصی به `direct` (بدون نیاز به `geoip.dat`/`geosite.dat`)
- `dns: 1.1.1.1, 8.8.8.8`

`ConfigBuilder.pingConfig(outbound)` فقط همان outbound را دارد؛ `measureOutboundDelay` با
`https://www.gstatic.com/generate_204` (همان `testUrl` اپ اصلی) تأخیر واقعی را برمی‌گرداند.
پینگ همه با ۴ کار هم‌زمان (`Semaphore`) انجام می‌شود تا هسته و شبکه اشباع نشود.

## ۵) بازسازی لینک اشتراک

`ConfigBuilder.shareLink(server)`:

- اگر `value` خودش لینک باشد → بدون تغییر برگردانده می‌شود.
- اگر JSON باشد → از outbound ساختهٔ خودمان لینک ساخته می‌شود:
  `vmess://base64(json)`، `vless://uuid@host:port?type=…&security=…&sni=…&fp=…&pbk=…&sid=…#name`،
  `trojan://pass@host:port?…`، `ss://base64(method:pass)@host:port#name`.

این خروجی در کلیپ‌بورد کپی می‌شود و در v2rayNG/nekobox/… قابل import است.

## ۶) هم‌زیستی با اپ اصلی

`applicationId` عیناً `co.asiven.vixentvpn` است، چون بک‌اند هدر `app_name` را با نام پکیج
مقایسه می‌کند و `sign` را با گواهی امضا. پیامدها:

- اپ آزمایشی روی گوشی‌ای که اپ اصلی نصب است، **جای آن نصب می‌شود** (امضای متفاوت → نیاز به حذف
  اپ اصلی یا استفاده از پروفایل کاری/کاربر دوم). برای تست کنار هم، از یک دستگاه/کاربر جدا استفاده کنید.
- `debug` build پسوند `.debug` دارد و هدر `app_name` آن با بک‌اند نمی‌خواند (فقط برای UI).

## ۷) نکات پیاده‌سازی

- UI با ViewBinding و `Material3.Dark`؛ همهٔ متن‌ها فارسی و چیدمان RTL است.
- کش سرورها در `SharedPreferences` (`protocolsCache`) تا اجرای بعدی فوری لیست داشته باشد؛
  دکمهٔ دریافت همیشه از بک‌اند تازه می‌گیرد.
- اعلان وضعیت روی کانال `mvpn_tunnel`؛ روی اندروید ۱۳+ اجازهٔ `POST_NOTIFICATIONS` گرفته می‌شود
  (نبودِ آن تونل را متوقف نمی‌کند).
- خطاها هم در UI و هم در «لاگ‌ها» (`AppLog`: حلقهٔ حافظه + فایل) ثبت می‌شوند تا بدون `adb logcat`
  هم بتوان عیب‌یابی کرد.
