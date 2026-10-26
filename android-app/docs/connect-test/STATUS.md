# connect-test — run 1

- branch: arena/b9372ae1-myvpn
- sha: 3bf4a57b65be9a2ad6a3c6c20f92d3933727a879
- started: 2026-10-26T03:50:11Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 26 03:45 /dev/kvm
- booted: 1
- apk: android-app/app/build/outputs/apk/release/app-release.apk
Performing Streamed Install
Success
Starting: Intent { cmp=co.asiven.vixentvpn/.trial.ui.MainActivity }
Status: ok
LaunchState: COLD
Activity: co.asiven.vixentvpn/.trial.ui.MainActivity
TotalTime: 3519
WaitTime: 3523
Complete

- connect-drive exit: 1

## Xray server access log
```
2026/10/26 03:53:24.111311 from 127.0.0.1:55798 accepted tcp:www.gstatic.com:443
```
## Xray server error log
```
2026/10/26 03:46:34.325003 [Info] transport/internet/tcp: listening tcp on 0.0.0.0:10086
2026/10/26 03:46:34.325031 [Warning] core: Xray 26.10.21 started
2026/10/26 03:53:24.111058 [Info] [3052424560] proxy/vless/inbound: firstLen = 1460
2026/10/26 03:53:24.111266 [Info] [3052424560] proxy/vless/inbound: received request for tcp:www.gstatic.com:443
2026/10/26 03:53:24.111276 [Info] [3052424560] app/dispatcher: default route for tcp:www.gstatic.com:443
2026/10/26 03:53:24.113845 [Info] [3052424560] transport/internet/tcp: dialing TCP to tcp:www.gstatic.com:443
2026/10/26 03:53:24.117064 [Info] [3052424560] proxy/freedom: connection opened to tcp:www.gstatic.com:443, local endpoint 10.1.0.4:40566, remote endpoint 142.251.157.120:443
```
