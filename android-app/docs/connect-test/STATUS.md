# connect-test — run 9

- branch: arena/b9372ae1-myvpn
- sha: 978fac006367d5a446c3eadef23d5e32cfd8a68c
- started: 2026-10-26T05:46:39Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 26 05:42 /dev/kvm
- booted: 1
- apk: android-app/app/build/outputs/apk/release/app-release.apk
Performing Streamed Install
Success
Starting: Intent { cmp=co.asiven.vixentvpn/.trial.ui.MainActivity }
Status: ok
LaunchState: COLD
Activity: co.asiven.vixentvpn/.trial.ui.MainActivity
TotalTime: 3207
WaitTime: 3216
Complete

- connect-drive exit: 0

## Xray server access log
```
2026/10/26 05:48:20.941808 from 127.0.0.1:52586 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:21.131005 from 127.0.0.1:52600 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:21.159644 from 127.0.0.1:52608 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:21.807845 from 127.0.0.1:52614 accepted tcp:dl.google.com:443
2026/10/26 05:48:22.032171 from 127.0.0.1:52616 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:22.447130 from 127.0.0.1:52628 accepted tcp:dl.google.com:443
2026/10/26 05:48:26.046390 from 127.0.0.1:52634 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:26.750550 from 127.0.0.1:52644 accepted tcp:android.googleapis.com:443
2026/10/26 05:48:30.207538 from 127.0.0.1:49962 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:30.263329 from 127.0.0.1:49978 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:30.406474 from 127.0.0.1:49984 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:30.811457 from 127.0.0.1:50000 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:30.842863 from 127.0.0.1:50008 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:30.916668 from 127.0.0.1:50012 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:31.247340 from 127.0.0.1:50018 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:31.366827 from 127.0.0.1:50028 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:31.455188 from 127.0.0.1:50044 accepted tcp:www.gstatic.com:443
2026/10/26 05:48:34.942784 from 127.0.0.1:50048 accepted tcp:rcs-acs-tmo-us.jibe.google.com:443
2026/10/26 05:48:35.782792 from 127.0.0.1:50054 accepted tcp:mtalk.google.com:5228
2026/10/26 05:48:36.318922 from 127.0.0.1:50070 accepted tcp:pagead2.googlesyndication.com:443
2026/10/26 05:48:37.051010 from 127.0.0.1:50072 accepted tcp:android.googleapis.com:443
2026/10/26 05:48:37.858738 from 127.0.0.1:50088 accepted tcp:voilatile-pa.googleapis.com:443
2026/10/26 05:48:43.610806 from 127.0.0.1:52294 accepted tcp:android.googleapis.com:443
2026/10/26 05:48:44.530796 from 127.0.0.1:52302 accepted tcp:www.googleapis.com:443
2026/10/26 05:48:46.987173 from 127.0.0.1:52310 accepted tcp:dl.google.com:443
2026/10/26 05:48:57.466988 from 127.0.0.1:42816 accepted tcp:www.googleapis.com:443
2026/10/26 05:48:59.091916 from 127.0.0.1:42832 accepted tcp:android.googleapis.com:443
2026/10/26 05:49:01.415010 from 127.0.0.1:58450 accepted tcp:android.googleapis.com:443
2026/10/26 05:49:03.079091 from 127.0.0.1:58462 accepted udp:172.217.119.4:443
2026/10/26 05:49:04.731697 from 127.0.0.1:58472 accepted udp:172.217.117.4:443
2026/10/26 05:49:06.731901 from 127.0.0.1:39484 accepted udp:8.8.8.8:443
2026/10/26 05:49:06.846970 from 127.0.0.1:39490 accepted tcp:1.1.1.1:853
2026/10/26 05:49:06.852751 from 127.0.0.1:39506 accepted tcp:8.8.8.8:853
2026/10/26 05:49:07.203433 from 127.0.0.1:39512 accepted udp:8.8.8.8:443
2026/10/26 05:49:07.208370 from 127.0.0.1:39514 accepted udp:8.8.8.8:53
2026/10/26 05:49:07.217526 from 127.0.0.1:39526 accepted udp:1.1.1.1:53
2026/10/26 05:49:09.558646 from 127.0.0.1:39538 accepted tcp:www.gstatic.com:80
2026/10/26 05:49:12.855476 from 127.0.0.1:43138 accepted udp:172.217.112.4:443
2026/10/26 05:49:13.563729 from 127.0.0.1:43150 rejected  proxy/vmess/encoding: failed to read request header > websocket: close 1000 (normal)
2026/10/26 05:49:13.566410 from 127.0.0.1:43160 accepted udp:172.217.117.4:443
```
## Xray server error log
```
2026/10/26 05:49:04.731672 [Info] [1533074343] proxy/vless/inbound: received request for udp:172.217.117.4:443
2026/10/26 05:49:04.731680 [Info] [1533074343] app/dispatcher: default route for udp:172.217.117.4:443
2026/10/26 05:49:04.731688 [Info] [1533074343] proxy/freedom: connection opened to udp:172.217.117.4:443, local endpoint [::]:43164, remote endpoint 172.217.117.4:443
2026/10/26 05:49:06.731486 [Info] [3432982289] proxy/vmess/inbound: received request for udp:8.8.8.8:443
2026/10/26 05:49:06.731625 [Info] [3432982289] app/dispatcher: default route for udp:8.8.8.8:443
2026/10/26 05:49:06.731962 [Info] [3432982289] proxy/freedom: connection opened to udp:8.8.8.8:443, local endpoint [::]:44049, remote endpoint 8.8.8.8:443
2026/10/26 05:49:06.846820 [Info] [1960237334] proxy/vmess/inbound: received request for tcp:1.1.1.1:853
2026/10/26 05:49:06.847014 [Info] [1960237334] app/dispatcher: default route for tcp:1.1.1.1:853
2026/10/26 05:49:06.847045 [Info] [1960237334] transport/internet/tcp: dialing TCP to tcp:1.1.1.1:853
2026/10/26 05:49:06.848645 [Info] [1960237334] proxy/freedom: connection opened to tcp:1.1.1.1:853, local endpoint 10.1.0.180:58962, remote endpoint 1.1.1.1:853
2026/10/26 05:49:06.852616 [Info] [859487141] proxy/vmess/inbound: received request for tcp:8.8.8.8:853
2026/10/26 05:49:06.852769 [Info] [859487141] app/dispatcher: default route for tcp:8.8.8.8:853
2026/10/26 05:49:06.852779 [Info] [859487141] transport/internet/tcp: dialing TCP to tcp:8.8.8.8:853
2026/10/26 05:49:06.855237 [Info] [859487141] proxy/freedom: connection opened to tcp:8.8.8.8:853, local endpoint 10.1.0.180:35838, remote endpoint 8.8.8.8:853
2026/10/26 05:49:07.203303 [Info] [2708999005] proxy/vmess/inbound: received request for udp:8.8.8.8:443
2026/10/26 05:49:07.203396 [Info] [2708999005] app/dispatcher: default route for udp:8.8.8.8:443
2026/10/26 05:49:07.203453 [Info] [2708999005] proxy/freedom: connection opened to udp:8.8.8.8:443, local endpoint [::]:40427, remote endpoint 8.8.8.8:443
2026/10/26 05:49:07.208229 [Info] [2721463695] proxy/vmess/inbound: received request for udp:8.8.8.8:53
2026/10/26 05:49:07.208352 [Info] [2721463695] app/dispatcher: default route for udp:8.8.8.8:53
2026/10/26 05:49:07.208363 [Info] [2721463695] proxy/freedom: connection opened to udp:8.8.8.8:53, local endpoint [::]:46161, remote endpoint 8.8.8.8:53
2026/10/26 05:49:07.217419 [Info] [4217789102] proxy/vmess/inbound: received request for udp:1.1.1.1:53
2026/10/26 05:49:07.217552 [Info] [4217789102] app/dispatcher: default route for udp:1.1.1.1:53
2026/10/26 05:49:07.217561 [Info] [4217789102] proxy/freedom: connection opened to udp:1.1.1.1:53, local endpoint [::]:36567, remote endpoint 1.1.1.1:53
2026/10/26 05:49:09.558503 [Info] [1245728596] proxy/vmess/inbound: received request for tcp:www.gstatic.com:80
2026/10/26 05:49:09.558601 [Info] [1245728596] app/dispatcher: default route for tcp:www.gstatic.com:80
2026/10/26 05:49:09.559826 [Info] [1245728596] transport/internet/tcp: dialing TCP to tcp:www.gstatic.com:80
2026/10/26 05:49:09.562704 [Info] [1245728596] proxy/freedom: connection opened to tcp:www.gstatic.com:80, local endpoint 10.1.0.180:56674, remote endpoint 142.251.150.120:80
2026/10/26 05:49:12.855356 [Info] [182296954] proxy/vmess/inbound: received request for udp:172.217.112.4:443
2026/10/26 05:49:12.855390 [Info] [182296954] app/dispatcher: default route for udp:172.217.112.4:443
2026/10/26 05:49:12.855499 [Info] [182296954] proxy/freedom: connection opened to udp:172.217.112.4:443, local endpoint [::]:42021, remote endpoint 172.217.112.4:443
2026/10/26 05:49:13.563734 [Info] [2500874725] app/proxyman/inbound: connection ends > proxy/vmess/inbound: invalid request from 127.0.0.1:43150 > proxy/vmess/encoding: failed to read request header > websocket: close 1000 (normal)
2026/10/26 05:49:13.566228 [Info] [3851910830] proxy/vmess/inbound: received request for udp:172.217.117.4:443
2026/10/26 05:49:13.566388 [Info] [3851910830] app/dispatcher: default route for udp:172.217.117.4:443
2026/10/26 05:49:13.566402 [Info] [3851910830] proxy/freedom: connection opened to udp:172.217.117.4:443, local endpoint [::]:52021, remote endpoint 172.217.117.4:443
2026/10/26 05:49:14.650400 [Info] [2708999005] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:49:14.650556 [Info] [3432982289] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:49:14.655607 [Info] [182296954] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:49:14.655894 [Info] [2721463695] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:49:14.655903 [Info] [4217789102] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:49:14.656791 [Info] [3851910830] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
```
