# gomobile / libv2ray (keep is explicit even though minification is off for this trial build)
-keep class libv2ray.** { *; }
-keep class go.** { *; }
-keep class co.asiven.vixentvpn.service.TProxyService { *; }
-keepclasseswithmembernames class * { native <methods>; }
