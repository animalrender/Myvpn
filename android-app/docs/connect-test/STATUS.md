# connect-test — run 8

- branch: arena/b9372ae1-myvpn
- sha: 519d1bb339da800179cfdf772d76235e01dcefc1
- started: 2026-10-26T05:32:46Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 26 05:27 /dev/kvm
- booted: 1
- apk: android-app/app/build/outputs/apk/release/app-release.apk
Performing Streamed Install
Success
Starting: Intent { cmp=co.asiven.vixentvpn/.trial.ui.MainActivity }
Status: ok
LaunchState: COLD
Activity: co.asiven.vixentvpn/.trial.ui.MainActivity
TotalTime: 3927
WaitTime: 3943
Complete

- connect-drive exit: 1

## Xray server access log
```
2026/10/26 05:34:24.327034 from 127.0.0.1:38528 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:24.510780 from 127.0.0.1:38540 accepted udp:142.251.152.120:443
2026/10/26 05:34:24.510799 from 127.0.0.1:38542 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:28.192404 from 127.0.0.1:33678 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:30.259119 from 127.0.0.1:33692 accepted tcp:mtalk.google.com:5228
2026/10/26 05:34:31.302856 from 127.0.0.1:33708 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:31.830293 from 127.0.0.1:33724 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:32.407209 from 127.0.0.1:33738 accepted tcp:dl.google.com:443
2026/10/26 05:34:32.955224 from 127.0.0.1:33746 accepted tcp:dl.google.com:443
2026/10/26 05:34:35.291715 from 127.0.0.1:33762 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:39.339158 from 127.0.0.1:36278 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:39.407393 from 127.0.0.1:36288 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:40.383384 from 127.0.0.1:36300 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:40.510947 from 127.0.0.1:36314 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:40.907870 from 127.0.0.1:36330 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:41.139801 from 127.0.0.1:36340 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:41.423966 from 127.0.0.1:36344 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:41.470681 from 127.0.0.1:36354 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:41.511038 from 127.0.0.1:36370 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:41.851779 from 127.0.0.1:36378 accepted tcp:www.gstatic.com:443
2026/10/26 05:34:49.247939 from 127.0.0.1:59974 accepted tcp:android.googleapis.com:443
2026/10/26 05:34:50.939179 from 127.0.0.1:59982 accepted tcp:android.googleapis.com:443
2026/10/26 05:34:50.942978 from 127.0.0.1:59992 accepted udp:172.217.118.4:443
2026/10/26 05:34:51.503772 from 127.0.0.1:59998 accepted udp:172.217.118.4:443
2026/10/26 05:34:52.103605 from 127.0.0.1:60010 accepted tcp:mtalk.google.com:5228
2026/10/26 05:34:53.078708 from 127.0.0.1:60022 accepted tcp:pagead2.googlesyndication.com:443
2026/10/26 05:34:54.362742 from 127.0.0.1:60028 accepted tcp:android.googleapis.com:443
2026/10/26 05:34:55.166696 from 127.0.0.1:60036 accepted tcp:voilatile-pa.googleapis.com:443
2026/10/26 05:35:03.901365 from 127.0.0.1:45436 accepted tcp:dl.google.com:443
2026/10/26 05:35:08.166839 from 127.0.0.1:53552 accepted tcp:android.googleapis.com:443
2026/10/26 05:35:09.819371 from 127.0.0.1:53556 accepted udp:172.217.114.4:443
2026/10/26 05:35:11.047387 from 127.0.0.1:53560 accepted tcp:www.googleapis.com:443
2026/10/26 05:35:12.523685 from 127.0.0.1:59508 accepted udp:8.8.8.8:53
2026/10/26 05:35:12.524989 from 127.0.0.1:59514 accepted tcp:8.8.8.8:853
2026/10/26 05:35:12.547650 from 127.0.0.1:59522 accepted udp:8.8.8.8:443
2026/10/26 05:35:13.274135 from 127.0.0.1:59532 accepted tcp:alt8-mtalk.google.com:5228
2026/10/26 05:35:14.692946 from 127.0.0.1:59542 accepted tcp:www.gstatic.com:80
2026/10/26 05:35:15.678751 from 127.0.0.1:59546 accepted tcp:www.googleapis.com:443
2026/10/26 05:35:19.050668 from 127.0.0.1:40390 accepted tcp:rcs-acs-tmo-us.jibe.google.com:443
2026/10/26 05:35:19.639133 from 127.0.0.1:40400 accepted udp:172.217.112.4:443
```
## Xray server error log
```
2026/10/26 05:35:11.047185 [Info] [1927076157] proxy/vless/inbound: firstLen = 558
2026/10/26 05:35:11.047219 [Info] [1927076157] proxy/vless/inbound: received request for tcp:www.googleapis.com:443
2026/10/26 05:35:11.047380 [Info] [1927076157] app/dispatcher: default route for tcp:www.googleapis.com:443
2026/10/26 05:35:11.048736 [Info] [1927076157] transport/internet/tcp: dialing TCP to tcp:www.googleapis.com:443
2026/10/26 05:35:11.054881 [Info] [1927076157] proxy/freedom: connection opened to tcp:www.googleapis.com:443, local endpoint 10.1.0.229:56726, remote endpoint 172.217.114.4:443
2026/10/26 05:35:12.523238 [Info] [2184607114] proxy/vmess/inbound: received request for udp:8.8.8.8:53
2026/10/26 05:35:12.523528 [Info] [2184607114] app/dispatcher: default route for udp:8.8.8.8:53
2026/10/26 05:35:12.523875 [Info] [2184607114] proxy/freedom: connection opened to udp:8.8.8.8:53, local endpoint [::]:53247, remote endpoint 8.8.8.8:53
2026/10/26 05:35:12.524816 [Info] [4202963239] proxy/vmess/inbound: received request for tcp:8.8.8.8:853
2026/10/26 05:35:12.525108 [Info] [4202963239] app/dispatcher: default route for tcp:8.8.8.8:853
2026/10/26 05:35:12.525131 [Info] [4202963239] transport/internet/tcp: dialing TCP to tcp:8.8.8.8:853
2026/10/26 05:35:12.528057 [Info] [4202963239] proxy/freedom: connection opened to tcp:8.8.8.8:853, local endpoint 10.1.0.229:37382, remote endpoint 8.8.8.8:853
2026/10/26 05:35:12.547444 [Info] [1822990434] proxy/vmess/inbound: received request for udp:8.8.8.8:443
2026/10/26 05:35:12.547630 [Info] [1822990434] app/dispatcher: default route for udp:8.8.8.8:443
2026/10/26 05:35:12.547643 [Info] [1822990434] proxy/freedom: connection opened to udp:8.8.8.8:443, local endpoint [::]:38351, remote endpoint 8.8.8.8:443
2026/10/26 05:35:13.273994 [Info] [2162230557] proxy/vmess/inbound: received request for tcp:alt8-mtalk.google.com:5228
2026/10/26 05:35:13.274026 [Info] [2162230557] app/dispatcher: default route for tcp:alt8-mtalk.google.com:5228
2026/10/26 05:35:13.350853 [Info] [2162230557] transport/internet/tcp: dialing TCP to tcp:alt8-mtalk.google.com:5228
2026/10/26 05:35:13.470607 [Info] [2162230557] proxy/freedom: connection opened to tcp:alt8-mtalk.google.com:5228, local endpoint 10.1.0.229:58742, remote endpoint 142.250.102.188:5228
2026/10/26 05:35:14.692986 [Info] [786270676] proxy/vmess/inbound: received request for tcp:www.gstatic.com:80
2026/10/26 05:35:14.693007 [Info] [786270676] app/dispatcher: default route for tcp:www.gstatic.com:80
2026/10/26 05:35:14.693713 [Info] [786270676] transport/internet/tcp: dialing TCP to tcp:www.gstatic.com:80
2026/10/26 05:35:14.698082 [Info] [786270676] proxy/freedom: connection opened to tcp:www.gstatic.com:80, local endpoint 10.1.0.229:43654, remote endpoint 142.250.189.99:80
2026/10/26 05:35:15.678626 [Info] [8087714] proxy/vmess/inbound: received request for tcp:www.googleapis.com:443
2026/10/26 05:35:15.678748 [Info] [8087714] app/dispatcher: default route for tcp:www.googleapis.com:443
2026/10/26 05:35:15.679646 [Info] [8087714] transport/internet/tcp: dialing TCP to tcp:www.googleapis.com:443
2026/10/26 05:35:15.683204 [Info] [8087714] proxy/freedom: connection opened to tcp:www.googleapis.com:443, local endpoint 10.1.0.229:54006, remote endpoint 172.217.113.4:443
2026/10/26 05:35:19.050590 [Info] [326175413] proxy/vmess/inbound: received request for tcp:rcs-acs-tmo-us.jibe.google.com:443
2026/10/26 05:35:19.050620 [Info] [326175413] app/dispatcher: default route for tcp:rcs-acs-tmo-us.jibe.google.com:443
2026/10/26 05:35:19.092842 [Info] [326175413] transport/internet/tcp: dialing TCP to tcp:rcs-acs-tmo-us.jibe.google.com:443
2026/10/26 05:35:19.095639 [Info] [326175413] proxy/freedom: connection opened to tcp:rcs-acs-tmo-us.jibe.google.com:443, local endpoint 10.1.0.229:38656, remote endpoint 216.239.36.155:443
2026/10/26 05:35:19.638924 [Info] [2534080905] proxy/vmess/inbound: received request for udp:172.217.112.4:443
2026/10/26 05:35:19.639110 [Info] [2534080905] app/dispatcher: default route for udp:172.217.112.4:443
2026/10/26 05:35:19.639126 [Info] [2534080905] proxy/freedom: connection opened to udp:172.217.112.4:443, local endpoint [::]:39601, remote endpoint 172.217.112.4:443
2026/10/26 05:35:20.179786 [Info] [2184607114] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:35:20.231382 [Info] [1822990434] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:35:20.231513 [Info] [2534080905] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:35:21.231554 [Info] [2162230557] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > context canceled
2026/10/26 05:35:21.231584 [Info] [8087714] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > context canceled
2026/10/26 05:35:21.231629 [Info] [326175413] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > context canceled
```
