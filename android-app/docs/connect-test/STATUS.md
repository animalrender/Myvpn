# connect-test — run 4

- branch: arena/b9372ae1-myvpn
- sha: d3c937c3fd9f656d02a965d7ee938511ae324c48
- started: 2026-10-26T04:28:40Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 26 04:24 /dev/kvm
- booted: 1
- apk: android-app/app/build/outputs/apk/release/app-release.apk
Performing Streamed Install
Success
Starting: Intent { cmp=co.asiven.vixentvpn/.trial.ui.MainActivity }
Status: ok
LaunchState: COLD
Activity: co.asiven.vixentvpn/.trial.ui.MainActivity
TotalTime: 3208
WaitTime: 3614
Complete

- connect-drive exit: 0

## Xray server access log
```
2026/10/26 04:30:28.338949 from 127.0.0.1:59044 accepted tcp:www.gstatic.com:443
2026/10/26 04:30:28.658512 from 127.0.0.1:59058 accepted tcp:dl.google.com:443
2026/10/26 04:30:31.318834 from 127.0.0.1:59070 accepted udp:142.251.150.119:443
2026/10/26 04:30:31.349354 from 127.0.0.1:59084 accepted tcp:www.google.com:443
2026/10/26 04:30:31.746724 from 127.0.0.1:59100 accepted tcp:www.gstatic.com:443
2026/10/26 04:30:34.484081 from 127.0.0.1:40482 accepted tcp:www.gstatic.com:443
2026/10/26 04:30:34.578789 from 127.0.0.1:40490 accepted tcp:www.gstatic.com:443
2026/10/26 04:30:34.726731 from 127.0.0.1:40498 accepted tcp:rcs-acs-tmo-us.jibe.google.com:443
2026/10/26 04:30:34.754664 from 127.0.0.1:40508 accepted tcp:www.gstatic.com:443
2026/10/26 04:30:35.523400 from 127.0.0.1:40522 accepted tcp:www.gstatic.com:443
2026/10/26 04:30:35.639057 from 127.0.0.1:40530 accepted tcp:www.gstatic.com:443
2026/10/26 04:30:35.675795 from 127.0.0.1:40542 accepted tcp:www.gstatic.com:443
2026/10/26 04:30:42.066622 from 127.0.0.1:40552 accepted tcp:android.googleapis.com:443
2026/10/26 04:30:42.271039 from 127.0.0.1:40566 accepted udp:172.217.119.4:443
2026/10/26 04:30:43.235096 from 127.0.0.1:40568 accepted udp:172.217.119.4:443
2026/10/26 04:30:43.431308 from 127.0.0.1:40570 accepted tcp:android.googleapis.com:443
2026/10/26 04:30:43.958494 from 127.0.0.1:39452 accepted tcp:mtalk.google.com:5228
2026/10/26 04:30:45.286873 from 127.0.0.1:39460 accepted tcp:android.googleapis.com:443
2026/10/26 04:30:45.298351 from 127.0.0.1:39466 accepted tcp:android.googleapis.com:443
2026/10/26 04:30:45.595444 from 127.0.0.1:39468 accepted tcp:voilatile-pa.googleapis.com:443
2026/10/26 04:30:47.403909 from 127.0.0.1:39488 accepted udp:172.217.119.4:443
2026/10/26 04:30:47.406976 from 127.0.0.1:39472 accepted tcp:play.googleapis.com:443
2026/10/26 04:30:48.091030 from 127.0.0.1:39498 accepted udp:172.217.119.4:443
2026/10/26 04:30:49.934128 from 127.0.0.1:39512 accepted tcp:dl.google.com:443
2026/10/26 04:30:50.851030 from 127.0.0.1:39516 accepted udp:172.217.119.4:443
2026/10/26 04:30:51.361466 from 127.0.0.1:39528 accepted udp:172.217.119.4:443
2026/10/26 04:31:00.990887 from 127.0.0.1:48506 accepted tcp:android.googleapis.com:443
2026/10/26 04:31:01.508108 from 127.0.0.1:48516 accepted udp:172.217.119.4:443
2026/10/26 04:31:03.530402 from 127.0.0.1:39908 accepted udp:1.1.1.1:53
2026/10/26 04:31:03.534087 from 127.0.0.1:39920 accepted udp:8.8.8.8:443
2026/10/26 04:31:03.545853 from 127.0.0.1:39930 accepted tcp:1.1.1.1:853
2026/10/26 04:31:03.559464 from 127.0.0.1:52808 accepted tcp:alt2-mtalk.google.com:443
2026/10/26 04:31:03.577053 from 127.0.0.1:52814 accepted tcp:alt2-mtalk.google.com:443
2026/10/26 04:31:03.681266 from 127.0.0.1:52822 accepted tcp:8.8.8.8:853
2026/10/26 04:31:04.232650 from 127.0.0.1:52838 accepted udp:8.8.8.8:443
2026/10/26 04:31:04.245378 from 127.0.0.1:52850 accepted udp:8.8.8.8:53
2026/10/26 04:31:06.186859 from 127.0.0.1:52862 accepted tcp:www.gstatic.com:80
2026/10/26 04:31:09.531806 from 127.0.0.1:52866 accepted udp:172.217.116.4:443
2026/10/26 04:31:09.541428 from 127.0.0.1:52870 accepted tcp:mtalk.google.com:5228
2026/10/26 04:31:09.636861 from 127.0.0.1:52884 accepted tcp:www.googleapis.com:443
```
## Xray server error log
```
2026/10/26 04:31:03.577089 [Info] [3099186418] app/dispatcher: default route for tcp:alt2-mtalk.google.com:443
2026/10/26 04:31:03.607870 [Info] [3099186418] transport/internet/tcp: dialing TCP to tcp:alt2-mtalk.google.com:443
2026/10/26 04:31:03.607894 [Info] [3251302091] transport/internet/tcp: dialing TCP to tcp:alt2-mtalk.google.com:443
2026/10/26 04:31:03.662861 [Info] [3251302091] proxy/freedom: connection opened to tcp:alt2-mtalk.google.com:443, local endpoint 10.1.0.60:45990, remote endpoint 192.178.231.188:443
2026/10/26 04:31:03.662891 [Info] [3099186418] proxy/freedom: connection opened to tcp:alt2-mtalk.google.com:443, local endpoint 10.1.0.60:46002, remote endpoint 192.178.231.188:443
2026/10/26 04:31:03.681115 [Info] [1591160929] proxy/vmess/inbound: received request for tcp:8.8.8.8:853
2026/10/26 04:31:03.681306 [Info] [1591160929] app/dispatcher: default route for tcp:8.8.8.8:853
2026/10/26 04:31:03.681313 [Info] [1591160929] transport/internet/tcp: dialing TCP to tcp:8.8.8.8:853
2026/10/26 04:31:03.685990 [Info] [1591160929] proxy/freedom: connection opened to tcp:8.8.8.8:853, local endpoint 10.1.0.60:40510, remote endpoint 8.8.8.8:853
2026/10/26 04:31:04.078726 [Info] [3099186418] app/proxyman/outbound: app/proxyman/outbound: failed to process outbound traffic > proxy/freedom: connection ends > proxy: failed to process response > read tcp 10.1.0.60:46002->192.178.231.188:443: read: connection reset by peer
2026/10/26 04:31:04.078904 [Info] [3099186418] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > io: read/write on closed pipe
2026/10/26 04:31:04.232417 [Info] [4291268309] proxy/vmess/inbound: received request for udp:8.8.8.8:443
2026/10/26 04:31:04.232610 [Info] [4291268309] app/dispatcher: default route for udp:8.8.8.8:443
2026/10/26 04:31:04.232638 [Info] [4291268309] proxy/freedom: connection opened to udp:8.8.8.8:443, local endpoint [::]:43727, remote endpoint 8.8.8.8:443
2026/10/26 04:31:04.245278 [Info] [805762247] proxy/vmess/inbound: received request for udp:8.8.8.8:53
2026/10/26 04:31:04.245365 [Info] [805762247] app/dispatcher: default route for udp:8.8.8.8:53
2026/10/26 04:31:04.245372 [Info] [805762247] proxy/freedom: connection opened to udp:8.8.8.8:53, local endpoint [::]:56794, remote endpoint 8.8.8.8:53
2026/10/26 04:31:06.186548 [Info] [1840793647] proxy/vmess/inbound: received request for tcp:www.gstatic.com:80
2026/10/26 04:31:06.186843 [Info] [1840793647] app/dispatcher: default route for tcp:www.gstatic.com:80
2026/10/26 04:31:06.188588 [Info] [1840793647] transport/internet/tcp: dialing TCP to tcp:www.gstatic.com:80
2026/10/26 04:31:06.195829 [Info] [1840793647] proxy/freedom: connection opened to tcp:www.gstatic.com:80, local endpoint 10.1.0.60:57180, remote endpoint 142.250.73.99:80
2026/10/26 04:31:09.531663 [Info] [2313348601] proxy/vmess/inbound: received request for udp:172.217.116.4:443
2026/10/26 04:31:09.531781 [Info] [2313348601] app/dispatcher: default route for udp:172.217.116.4:443
2026/10/26 04:31:09.531795 [Info] [2313348601] proxy/freedom: connection opened to udp:172.217.116.4:443, local endpoint [::]:54894, remote endpoint 172.217.116.4:443
2026/10/26 04:31:09.541332 [Info] [3859742570] proxy/vmess/inbound: received request for tcp:mtalk.google.com:5228
2026/10/26 04:31:09.541403 [Info] [3859742570] app/dispatcher: default route for tcp:mtalk.google.com:5228
2026/10/26 04:31:09.543469 [Info] [3859742570] transport/internet/tcp: dialing TCP to tcp:mtalk.google.com:5228
2026/10/26 04:31:09.554359 [Info] [3859742570] proxy/freedom: connection opened to tcp:mtalk.google.com:5228, local endpoint 10.1.0.60:41314, remote endpoint 108.177.98.188:5228
2026/10/26 04:31:09.636771 [Info] [1437058009] proxy/vmess/inbound: received request for tcp:www.googleapis.com:443
2026/10/26 04:31:09.636791 [Info] [1437058009] app/dispatcher: default route for tcp:www.googleapis.com:443
2026/10/26 04:31:09.638504 [Info] [1437058009] transport/internet/tcp: dialing TCP to tcp:www.googleapis.com:443
2026/10/26 04:31:09.644886 [Info] [1437058009] proxy/freedom: connection opened to tcp:www.googleapis.com:443, local endpoint 10.1.0.60:46164, remote endpoint 172.217.116.4:443
2026/10/26 04:31:11.543701 [Info] [829182881] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 04:31:11.544114 [Info] [805762247] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 04:31:11.544124 [Info] [2313348601] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 04:31:11.544130 [Info] [4291268309] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 04:31:11.544175 [Info] [3284857692] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 04:31:12.544408 [Info] [1437058009] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > context canceled
2026/10/26 04:31:12.544463 [Info] [3251302091] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > context canceled
2026/10/26 04:31:12.544470 [Info] [3859742570] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > context canceled
```
