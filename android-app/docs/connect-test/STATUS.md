# connect-test — run 2

- branch: arena/b9372ae1-myvpn
- sha: 3cf5636c94e930e7db757e0ef95d519d14450343
- started: 2026-10-26T04:02:22Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 26 03:58 /dev/kvm
- booted: 1
- apk: android-app/app/build/outputs/apk/release/app-release.apk
Performing Streamed Install
Success
Starting: Intent { cmp=co.asiven.vixentvpn/.trial.ui.MainActivity }
Status: ok
LaunchState: COLD
Activity: co.asiven.vixentvpn/.trial.ui.MainActivity
TotalTime: 4064
WaitTime: 4176
Complete

- connect-drive exit: 0

## Xray server access log
```
2026/10/26 04:03:48.924249 from 127.0.0.1:51806 accepted tcp:www.gstatic.com:443
2026/10/26 04:03:49.280500 from 127.0.0.1:51814 accepted tcp:www.gstatic.com:443
2026/10/26 04:03:49.288448 from 127.0.0.1:51818 accepted tcp:www.gstatic.com:443
2026/10/26 04:03:49.931648 from 127.0.0.1:51828 accepted tcp:www.gstatic.com:80
2026/10/26 04:03:50.380750 from 127.0.0.1:51838 accepted udp:172.217.114.4:443
2026/10/26 04:03:54.131708 from 127.0.0.1:40014 accepted tcp:www.gstatic.com:443
2026/10/26 04:03:54.151461 from 127.0.0.1:40024 accepted tcp:www.gstatic.com:443
2026/10/26 04:03:54.271300 from 127.0.0.1:40034 accepted tcp:connectivitycheck.gstatic.com:80
2026/10/26 04:03:55.553803 from 127.0.0.1:40044 accepted udp:172.217.114.4:443
2026/10/26 04:03:56.060072 from 127.0.0.1:40056 accepted udp:74.125.132.94:443
2026/10/26 04:03:56.061134 from 127.0.0.1:40066 accepted tcp:www.gstatic.com:443
2026/10/26 04:03:58.111267 from 127.0.0.1:40090 accepted udp:172.217.117.4:443
2026/10/26 04:03:58.342722 from 127.0.0.1:40092 accepted tcp:www.googleapis.com:443
2026/10/26 04:03:58.591307 from 127.0.0.1:40102 accepted tcp:1.1.1.1:80
2026/10/26 04:03:58.626962 from 127.0.0.1:40108 accepted tcp:www.gstatic.com:443
2026/10/26 04:03:59.609707 from 127.0.0.1:40114 accepted tcp:www.gstatic.com:443
2026/10/26 04:03:59.934357 from 127.0.0.1:40122 accepted tcp:dl.google.com:443
2026/10/26 04:04:00.744163 from 127.0.0.1:57042 accepted tcp:dl.google.com:443
2026/10/26 04:04:02.984271 from 127.0.0.1:57056 accepted tcp:www.gstatic.com:443
2026/10/26 04:04:05.816623 from 127.0.0.1:57064 accepted tcp:www.gstatic.com:443
2026/10/26 04:04:06.109753 from 127.0.0.1:57066 accepted tcp:www.gstatic.com:443
2026/10/26 04:04:07.247664 from 127.0.0.1:57070 accepted tcp:rcs-acs-tmo-us.jibe.google.com:443
2026/10/26 04:04:07.411041 from 127.0.0.1:57074 accepted tcp:www.gstatic.com:443
2026/10/26 04:04:07.563465 from 127.0.0.1:57082 accepted tcp:www.gstatic.com:443
2026/10/26 04:04:07.659259 from 127.0.0.1:57092 accepted tcp:www.gstatic.com:443
2026/10/26 04:04:08.071285 from 127.0.0.1:57102 accepted tcp:www.gstatic.com:443
2026/10/26 04:04:08.239334 from 127.0.0.1:57118 accepted tcp:www.gstatic.com:443
2026/10/26 04:04:08.246517 from 127.0.0.1:57128 accepted tcp:www.gstatic.com:443
2026/10/26 04:04:14.926208 from 127.0.0.1:59528 accepted tcp:android.googleapis.com:443
2026/10/26 04:04:17.023839 from 127.0.0.1:59538 accepted tcp:mtalk.google.com:5228
2026/10/26 04:04:17.734073 from 127.0.0.1:59548 accepted tcp:pagead2.googlesyndication.com:443
2026/10/26 04:04:18.294060 from 127.0.0.1:59558 accepted tcp:android.googleapis.com:443
2026/10/26 04:04:18.842466 from 127.0.0.1:59566 accepted tcp:voilatile-pa.googleapis.com:443
2026/10/26 04:04:18.935027 from 127.0.0.1:59580 accepted tcp:android.googleapis.com:443
2026/10/26 04:04:25.154231 from 127.0.0.1:47906 accepted tcp:www.googleapis.com:443
2026/10/26 04:04:26.050589 from 127.0.0.1:47918 accepted tcp:android.googleapis.com:443
2026/10/26 04:04:26.934050 from 127.0.0.1:47930 accepted tcp:dl.google.com:443
2026/10/26 04:04:27.083110 from 127.0.0.1:47946 accepted udp:172.217.112.4:443
2026/10/26 04:04:32.721529 from 127.0.0.1:35880 accepted tcp:www.googleapis.com:443
2026/10/26 04:04:34.802424 from 127.0.0.1:35892 accepted udp:172.217.114.4:443
```
## Xray server error log
```
2026/10/26 04:04:18.294892 [Info] [2912090805] transport/internet/tcp: dialing TCP to tcp:android.googleapis.com:443
2026/10/26 04:04:18.309007 [Info] [2912090805] proxy/freedom: connection opened to tcp:android.googleapis.com:443, local endpoint 10.1.0.85:57830, remote endpoint 172.217.114.4:443
2026/10/26 04:04:18.842416 [Info] [2342100354] proxy/vless/inbound: firstLen = 567
2026/10/26 04:04:18.842451 [Info] [2342100354] proxy/vless/inbound: received request for tcp:voilatile-pa.googleapis.com:443
2026/10/26 04:04:18.842456 [Info] [2342100354] app/dispatcher: default route for tcp:voilatile-pa.googleapis.com:443
2026/10/26 04:04:18.843665 [Info] [2342100354] transport/internet/tcp: dialing TCP to tcp:voilatile-pa.googleapis.com:443
2026/10/26 04:04:18.862002 [Info] [2342100354] proxy/freedom: connection opened to tcp:voilatile-pa.googleapis.com:443, local endpoint 10.1.0.85:43968, remote endpoint 172.217.119.4:443
2026/10/26 04:04:18.934988 [Info] [1032033577] proxy/vless/inbound: firstLen = 562
2026/10/26 04:04:18.935015 [Info] [1032033577] proxy/vless/inbound: received request for tcp:android.googleapis.com:443
2026/10/26 04:04:18.935019 [Info] [1032033577] app/dispatcher: default route for tcp:android.googleapis.com:443
2026/10/26 04:04:18.936141 [Info] [1032033577] transport/internet/tcp: dialing TCP to tcp:android.googleapis.com:443
2026/10/26 04:04:18.950848 [Info] [1032033577] proxy/freedom: connection opened to tcp:android.googleapis.com:443, local endpoint 10.1.0.85:57838, remote endpoint 172.217.114.4:443
2026/10/26 04:04:25.154196 [Info] [1836989092] proxy/vless/inbound: firstLen = 558
2026/10/26 04:04:25.154217 [Info] [1836989092] proxy/vless/inbound: received request for tcp:www.googleapis.com:443
2026/10/26 04:04:25.154222 [Info] [1836989092] app/dispatcher: default route for tcp:www.googleapis.com:443
2026/10/26 04:04:25.161886 [Info] [1836989092] transport/internet/tcp: dialing TCP to tcp:www.googleapis.com:443
2026/10/26 04:04:25.178324 [Info] [1836989092] proxy/freedom: connection opened to tcp:www.googleapis.com:443, local endpoint 10.1.0.85:52326, remote endpoint 172.217.118.4:443
2026/10/26 04:04:26.050560 [Info] [18045660] proxy/vless/inbound: firstLen = 562
2026/10/26 04:04:26.050578 [Info] [18045660] proxy/vless/inbound: received request for tcp:android.googleapis.com:443
2026/10/26 04:04:26.050582 [Info] [18045660] app/dispatcher: default route for tcp:android.googleapis.com:443
2026/10/26 04:04:26.051681 [Info] [18045660] transport/internet/tcp: dialing TCP to tcp:android.googleapis.com:443
2026/10/26 04:04:26.067970 [Info] [18045660] proxy/freedom: connection opened to tcp:android.googleapis.com:443, local endpoint 10.1.0.85:52340, remote endpoint 172.217.118.4:443
2026/10/26 04:04:26.933917 [Info] [1357827866] proxy/vless/inbound: firstLen = 553
2026/10/26 04:04:26.933940 [Info] [1357827866] proxy/vless/inbound: received request for tcp:dl.google.com:443
2026/10/26 04:04:26.934041 [Info] [1357827866] app/dispatcher: default route for tcp:dl.google.com:443
2026/10/26 04:04:26.934850 [Info] [1357827866] transport/internet/tcp: dialing TCP to tcp:dl.google.com:443
2026/10/26 04:04:26.958912 [Info] [1357827866] proxy/freedom: connection opened to tcp:dl.google.com:443, local endpoint 10.1.0.85:45988, remote endpoint 64.233.181.91:443
2026/10/26 04:04:27.083038 [Info] [363851402] proxy/vless/inbound: firstLen = 1278
2026/10/26 04:04:27.083062 [Info] [363851402] proxy/vless/inbound: received request for udp:172.217.112.4:443
2026/10/26 04:04:27.083068 [Info] [363851402] app/dispatcher: default route for udp:172.217.112.4:443
2026/10/26 04:04:27.083124 [Info] [363851402] proxy/freedom: connection opened to udp:172.217.112.4:443, local endpoint [::]:59559, remote endpoint 172.217.112.4:443
2026/10/26 04:04:32.721697 [Info] [3909644412] proxy/vless/inbound: firstLen = 558
2026/10/26 04:04:32.721710 [Info] [3909644412] proxy/vless/inbound: received request for tcp:www.googleapis.com:443
2026/10/26 04:04:32.721715 [Info] [3909644412] app/dispatcher: default route for tcp:www.googleapis.com:443
2026/10/26 04:04:32.722615 [Info] [3909644412] transport/internet/tcp: dialing TCP to tcp:www.googleapis.com:443
2026/10/26 04:04:32.748108 [Info] [3909644412] proxy/freedom: connection opened to tcp:www.googleapis.com:443, local endpoint 10.1.0.85:36164, remote endpoint 172.217.114.4:443
2026/10/26 04:04:34.802138 [Info] [664881388] proxy/vless/inbound: firstLen = 1278
2026/10/26 04:04:34.802400 [Info] [664881388] proxy/vless/inbound: received request for udp:172.217.114.4:443
2026/10/26 04:04:34.802418 [Info] [664881388] app/dispatcher: default route for udp:172.217.114.4:443
2026/10/26 04:04:34.802491 [Info] [664881388] proxy/freedom: connection opened to udp:172.217.114.4:443, local endpoint [::]:58799, remote endpoint 172.217.114.4:443
```
