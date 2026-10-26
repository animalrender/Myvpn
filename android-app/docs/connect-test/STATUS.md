# connect-test — run 7

- branch: arena/b9372ae1-myvpn
- sha: 80253e516d74e628f28584d85df0e8a6b7aaa463
- started: 2026-10-26T05:18:32Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 26 05:14 /dev/kvm
- booted: 1
- apk: android-app/app/build/outputs/apk/release/app-release.apk
Performing Streamed Install
Success
Starting: Intent { cmp=co.asiven.vixentvpn/.trial.ui.MainActivity }
Status: ok
LaunchState: COLD
Activity: co.asiven.vixentvpn/.trial.ui.MainActivity
TotalTime: 3447
WaitTime: 3538
Complete

- connect-drive exit: 1

## Xray server access log
```
2026/10/26 05:20:14.559125 from 127.0.0.1:48154 accepted tcp:www.gstatic.com:443
2026/10/26 05:20:15.476300 from 127.0.0.1:48176 accepted tcp:www.gstatic.com:443
2026/10/26 05:20:18.248288 from 127.0.0.1:48186 accepted tcp:rcs-acs-tmo-us.jibe.google.com:443
2026/10/26 05:20:18.542401 from 127.0.0.1:48200 accepted tcp:www.gstatic.com:443
2026/10/26 05:20:18.630751 from 127.0.0.1:48214 accepted tcp:www.gstatic.com:443
2026/10/26 05:20:18.881898 from 127.0.0.1:48228 accepted tcp:www.gstatic.com:443
2026/10/26 05:20:19.042609 from 127.0.0.1:48236 accepted tcp:www.gstatic.com:443
2026/10/26 05:20:19.588266 from 127.0.0.1:48238 accepted tcp:www.gstatic.com:443
2026/10/26 05:20:19.857888 from 127.0.0.1:48250 accepted tcp:www.gstatic.com:443
2026/10/26 05:20:19.957489 from 127.0.0.1:48266 accepted tcp:www.gstatic.com:443
2026/10/26 05:20:20.006378 from 127.0.0.1:48280 accepted tcp:www.gstatic.com:443
2026/10/26 05:20:28.115533 from 127.0.0.1:55474 accepted udp:142.251.152.119:443
2026/10/26 05:20:28.118987 from 127.0.0.1:55490 accepted tcp:www.google.com:443
2026/10/26 05:20:28.120247 from 127.0.0.1:55478 accepted tcp:www.google.com:443
2026/10/26 05:20:28.182369 from 127.0.0.1:55514 accepted tcp:www.google.com:443
2026/10/26 05:20:28.183230 from 127.0.0.1:55504 accepted tcp:www.google.com:443
2026/10/26 05:20:29.422339 from 127.0.0.1:55526 accepted tcp:android.googleapis.com:443
2026/10/26 05:20:31.281986 from 127.0.0.1:55538 accepted tcp:mtalk.google.com:5228
2026/10/26 05:20:31.924508 from 127.0.0.1:55554 accepted tcp:pagead2.googlesyndication.com:443
2026/10/26 05:20:32.826534 from 127.0.0.1:53396 accepted tcp:android.googleapis.com:443
2026/10/26 05:20:33.350698 from 127.0.0.1:53404 accepted tcp:android.googleapis.com:443
2026/10/26 05:20:33.654462 from 127.0.0.1:53414 accepted tcp:voilatile-pa.googleapis.com:443
2026/10/26 05:20:37.026537 from 127.0.0.1:53418 accepted tcp:dl.google.com:443
2026/10/26 05:20:39.140217 from 127.0.0.1:53424 accepted udp:172.217.115.4:443
2026/10/26 05:20:39.142002 from 127.0.0.1:53430 accepted tcp:play.googleapis.com:443
2026/10/26 05:20:46.727143 from 127.0.0.1:38332 accepted tcp:android.googleapis.com:443
2026/10/26 05:20:47.404315 from 127.0.0.1:38336 accepted tcp:www.googleapis.com:443
2026/10/26 05:20:47.822165 from 127.0.0.1:38348 accepted udp:172.217.116.4:443
2026/10/26 05:20:48.665848 from 127.0.0.1:38356 accepted tcp:www.googleapis.com:443
2026/10/26 05:20:51.540909 from 127.0.0.1:38364 accepted udp:172.217.118.4:443
2026/10/26 05:20:53.831941 from 127.0.0.1:60804 accepted udp:172.217.116.4:443
2026/10/26 05:20:57.753490 from 127.0.0.1:39422 accepted udp:8.8.8.8:443
2026/10/26 05:20:57.760127 from 127.0.0.1:39426 accepted tcp:alt8-mtalk.google.com:5228
2026/10/26 05:20:57.784801 from 127.0.0.1:39434 accepted tcp:alt8-mtalk.google.com:5228
2026/10/26 05:20:57.826099 from 127.0.0.1:39442 accepted tcp:8.8.8.8:853
2026/10/26 05:20:57.845889 from 127.0.0.1:39454 accepted tcp:1.1.1.1:853
2026/10/26 05:20:58.243420 from 127.0.0.1:39464 accepted udp:8.8.8.8:443
2026/10/26 05:20:58.249078 from 127.0.0.1:39472 accepted udp:1.1.1.1:53
2026/10/26 05:20:58.261942 from 127.0.0.1:39486 accepted udp:8.8.8.8:53
2026/10/26 05:21:00.670314 from 127.0.0.1:39500 accepted tcp:www.gstatic.com:80
```
## Xray server error log
```
2026/10/26 05:20:53.831943 [Info] [2606921719] proxy/vless/inbound: received request for udp:172.217.116.4:443
2026/10/26 05:20:53.831948 [Info] [2606921719] app/dispatcher: default route for udp:172.217.116.4:443
2026/10/26 05:20:53.831955 [Info] [2606921719] proxy/freedom: connection opened to udp:172.217.116.4:443, local endpoint [::]:58075, remote endpoint 172.217.116.4:443
2026/10/26 05:20:57.753312 [Info] [786404539] proxy/vmess/inbound: received request for udp:8.8.8.8:443
2026/10/26 05:20:57.753371 [Info] [786404539] app/dispatcher: default route for udp:8.8.8.8:443
2026/10/26 05:20:57.753860 [Info] [786404539] proxy/freedom: connection opened to udp:8.8.8.8:443, local endpoint [::]:40685, remote endpoint 8.8.8.8:443
2026/10/26 05:20:57.759951 [Info] [1002979956] proxy/vmess/inbound: received request for tcp:alt8-mtalk.google.com:5228
2026/10/26 05:20:57.760100 [Info] [1002979956] app/dispatcher: default route for tcp:alt8-mtalk.google.com:5228
2026/10/26 05:20:57.779505 [Info] [1002979956] transport/internet/tcp: dialing TCP to tcp:alt8-mtalk.google.com:5228
2026/10/26 05:20:57.785286 [Info] [3787224573] proxy/vmess/inbound: received request for tcp:alt8-mtalk.google.com:5228
2026/10/26 05:20:57.785326 [Info] [3787224573] app/dispatcher: default route for tcp:alt8-mtalk.google.com:5228
2026/10/26 05:20:57.797924 [Info] [3787224573] transport/internet/tcp: dialing TCP to tcp:alt8-mtalk.google.com:5228
2026/10/26 05:20:57.826022 [Info] [4143481910] proxy/vmess/inbound: received request for tcp:8.8.8.8:853
2026/10/26 05:20:57.826095 [Info] [4143481910] app/dispatcher: default route for tcp:8.8.8.8:853
2026/10/26 05:20:57.826104 [Info] [4143481910] transport/internet/tcp: dialing TCP to tcp:8.8.8.8:853
2026/10/26 05:20:57.827443 [Info] [4143481910] proxy/freedom: connection opened to tcp:8.8.8.8:853, local endpoint 10.1.0.26:57898, remote endpoint 8.8.8.8:853
2026/10/26 05:20:57.845827 [Info] [2280184845] proxy/vmess/inbound: received request for tcp:1.1.1.1:853
2026/10/26 05:20:57.845873 [Info] [2280184845] app/dispatcher: default route for tcp:1.1.1.1:853
2026/10/26 05:20:57.845881 [Info] [2280184845] transport/internet/tcp: dialing TCP to tcp:1.1.1.1:853
2026/10/26 05:20:57.847530 [Info] [2280184845] proxy/freedom: connection opened to tcp:1.1.1.1:853, local endpoint 10.1.0.26:50810, remote endpoint 1.1.1.1:853
2026/10/26 05:20:57.853297 [Info] [1002979956] proxy/freedom: connection opened to tcp:alt8-mtalk.google.com:5228, local endpoint 10.1.0.26:49498, remote endpoint 142.250.96.188:5228
2026/10/26 05:20:57.875821 [Info] [3787224573] proxy/freedom: connection opened to tcp:alt8-mtalk.google.com:5228, local endpoint 10.1.0.26:49506, remote endpoint 142.250.96.188:5228
2026/10/26 05:20:58.243187 [Info] [3692101800] proxy/vmess/inbound: received request for udp:8.8.8.8:443
2026/10/26 05:20:58.243395 [Info] [3692101800] app/dispatcher: default route for udp:8.8.8.8:443
2026/10/26 05:20:58.243413 [Info] [3692101800] proxy/freedom: connection opened to udp:8.8.8.8:443, local endpoint [::]:58874, remote endpoint 8.8.8.8:443
2026/10/26 05:20:58.248971 [Info] [2807455201] proxy/vmess/inbound: received request for udp:1.1.1.1:53
2026/10/26 05:20:58.248989 [Info] [2807455201] app/dispatcher: default route for udp:1.1.1.1:53
2026/10/26 05:20:58.249092 [Info] [2807455201] proxy/freedom: connection opened to udp:1.1.1.1:53, local endpoint [::]:59085, remote endpoint 1.1.1.1:53
2026/10/26 05:20:58.261697 [Info] [4006991325] proxy/vmess/inbound: received request for udp:8.8.8.8:53
2026/10/26 05:20:58.261921 [Info] [4006991325] app/dispatcher: default route for udp:8.8.8.8:53
2026/10/26 05:20:58.261935 [Info] [4006991325] proxy/freedom: connection opened to udp:8.8.8.8:53, local endpoint [::]:46340, remote endpoint 8.8.8.8:53
2026/10/26 05:21:00.670213 [Info] [1573186] proxy/vmess/inbound: received request for tcp:www.gstatic.com:80
2026/10/26 05:21:00.670333 [Info] [1573186] app/dispatcher: default route for tcp:www.gstatic.com:80
2026/10/26 05:21:00.671766 [Info] [1573186] transport/internet/tcp: dialing TCP to tcp:www.gstatic.com:80
2026/10/26 05:21:00.674339 [Info] [1573186] proxy/freedom: connection opened to tcp:www.gstatic.com:80, local endpoint 10.1.0.26:38104, remote endpoint 142.251.155.120:80
2026/10/26 05:21:05.751842 [Info] [786404539] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:21:05.752539 [Info] [3692101800] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:21:05.755095 [Info] [2807455201] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:21:05.786791 [Info] [4006991325] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:21:06.752626 [Info] [3787224573] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > context canceled
```
