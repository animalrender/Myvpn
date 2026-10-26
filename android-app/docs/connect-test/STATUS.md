# connect-test — run 6

- branch: arena/b9372ae1-myvpn
- sha: 94156653fe390d486a41c9b082f578146abe6cce
- started: 2026-10-26T05:04:24Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 26 04:58 /dev/kvm
- booted: 1
- apk: android-app/app/build/outputs/apk/release/app-release.apk
Performing Streamed Install
Success
Starting: Intent { cmp=co.asiven.vixentvpn/.trial.ui.MainActivity }
Status: ok
LaunchState: COLD
Activity: co.asiven.vixentvpn/.trial.ui.MainActivity
TotalTime: 4737
WaitTime: 4754
Complete

- connect-drive exit: 0

## Xray server access log
```
2026/10/26 05:05:59.687301 from 127.0.0.1:36662 accepted tcp:www.gstatic.com:443
2026/10/26 05:05:59.763714 from 127.0.0.1:36672 accepted tcp:www.gstatic.com:443
2026/10/26 05:06:00.307226 from 127.0.0.1:36680 accepted tcp:www.gstatic.com:443
2026/10/26 05:06:00.831846 from 127.0.0.1:36686 accepted tcp:dl.google.com:443
2026/10/26 05:06:02.050197 from 127.0.0.1:36712 accepted tcp:dl.google.com:443
2026/10/26 05:06:07.335514 from 127.0.0.1:57190 accepted tcp:www.gstatic.com:443
2026/10/26 05:06:09.383866 from 127.0.0.1:57194 accepted tcp:www.gstatic.com:443
2026/10/26 05:06:09.407652 from 127.0.0.1:57200 accepted tcp:www.gstatic.com:443
2026/10/26 05:06:09.472246 from 127.0.0.1:57204 accepted tcp:www.gstatic.com:443
2026/10/26 05:06:09.554227 from 127.0.0.1:57218 accepted tcp:www.gstatic.com:443
2026/10/26 05:06:10.179462 from 127.0.0.1:57220 accepted tcp:www.gstatic.com:443
2026/10/26 05:06:10.255739 from 127.0.0.1:57234 accepted tcp:www.gstatic.com:443
2026/10/26 05:06:10.283517 from 127.0.0.1:57240 accepted tcp:www.gstatic.com:443
2026/10/26 05:06:10.335884 from 127.0.0.1:57244 accepted tcp:www.gstatic.com:443
2026/10/26 05:06:14.263360 from 127.0.0.1:46180 accepted tcp:mtalk.google.com:5228
2026/10/26 05:06:14.443058 from 127.0.0.1:46182 accepted tcp:pagead2.googlesyndication.com:443
2026/10/26 05:06:15.587073 from 127.0.0.1:46184 accepted tcp:android.googleapis.com:443
2026/10/26 05:06:16.379200 from 127.0.0.1:46188 accepted tcp:voilatile-pa.googleapis.com:443
2026/10/26 05:06:18.723562 from 127.0.0.1:46192 accepted udp:142.251.153.119:443
2026/10/26 05:06:18.727595 from 127.0.0.1:46206 accepted tcp:www.google.com:443
2026/10/26 05:06:18.727603 from 127.0.0.1:46194 accepted tcp:www.google.com:443
2026/10/26 05:06:18.775907 from 127.0.0.1:46212 accepted tcp:www.google.com:443
2026/10/26 05:06:20.127251 from 127.0.0.1:46222 accepted tcp:www.googleapis.com:443
2026/10/26 05:06:20.147358 from 127.0.0.1:46228 accepted tcp:android.googleapis.com:443
2026/10/26 05:06:23.399251 from 127.0.0.1:46892 accepted tcp:www.googleapis.com:443
2026/10/26 05:06:28.555118 from 127.0.0.1:46902 accepted tcp:dl.google.com:443
2026/10/26 05:06:33.140495 from 127.0.0.1:59760 accepted tcp:rcs-acs-tmo-us.jibe.google.com:443
2026/10/26 05:06:40.015521 from 127.0.0.1:59774 accepted udp:172.217.112.4:443
2026/10/26 05:06:43.444267 from 127.0.0.1:60782 accepted udp:8.8.8.8:443
2026/10/26 05:06:43.450181 from 127.0.0.1:60786 accepted tcp:8.8.8.8:853
2026/10/26 05:06:43.460703 from 127.0.0.1:60788 accepted tcp:1.1.1.1:853
2026/10/26 05:06:43.736559 from 127.0.0.1:60794 accepted udp:1.1.1.1:53
2026/10/26 05:06:43.739094 from 127.0.0.1:60808 accepted udp:1.1.1.1:53
2026/10/26 05:06:43.741052 from 127.0.0.1:60814 accepted udp:8.8.8.8:53
2026/10/26 05:06:43.968279 from 127.0.0.1:60828 accepted udp:172.217.117.4:443
2026/10/26 05:06:43.972759 from 127.0.0.1:60842 accepted udp:8.8.8.8:443
2026/10/26 05:06:45.596477 from 127.0.0.1:60856 accepted udp:172.217.116.4:443
2026/10/26 05:06:46.307698 from 127.0.0.1:60870 accepted tcp:www.gstatic.com:80
2026/10/26 05:06:49.621959 from 127.0.0.1:60880 rejected  proxy/vmess/encoding: failed to read request header > websocket: close 1000 (normal)
2026/10/26 05:06:50.192620 from 127.0.0.1:60882 accepted udp:172.217.115.4:443
```
## Xray server error log
```
2026/10/26 05:06:43.450236 [Info] [2071920664] transport/internet/tcp: dialing TCP to tcp:8.8.8.8:853
2026/10/26 05:06:43.452869 [Info] [2071920664] proxy/freedom: connection opened to tcp:8.8.8.8:853, local endpoint 10.1.0.144:39110, remote endpoint 8.8.8.8:853
2026/10/26 05:06:43.460588 [Info] [3892215779] proxy/vmess/inbound: received request for tcp:1.1.1.1:853
2026/10/26 05:06:43.460739 [Info] [3892215779] app/dispatcher: default route for tcp:1.1.1.1:853
2026/10/26 05:06:43.460747 [Info] [3892215779] transport/internet/tcp: dialing TCP to tcp:1.1.1.1:853
2026/10/26 05:06:43.462702 [Info] [3892215779] proxy/freedom: connection opened to tcp:1.1.1.1:853, local endpoint 10.1.0.144:42846, remote endpoint 1.1.1.1:853
2026/10/26 05:06:43.736421 [Info] [32447166] proxy/vmess/inbound: received request for udp:1.1.1.1:53
2026/10/26 05:06:43.736490 [Info] [32447166] app/dispatcher: default route for udp:1.1.1.1:53
2026/10/26 05:06:43.736581 [Info] [32447166] proxy/freedom: connection opened to udp:1.1.1.1:53, local endpoint [::]:35274, remote endpoint 1.1.1.1:53
2026/10/26 05:06:43.738953 [Info] [1417924352] proxy/vmess/inbound: received request for udp:1.1.1.1:53
2026/10/26 05:06:43.739030 [Info] [1417924352] app/dispatcher: default route for udp:1.1.1.1:53
2026/10/26 05:06:43.739107 [Info] [1417924352] proxy/freedom: connection opened to udp:1.1.1.1:53, local endpoint [::]:57551, remote endpoint 1.1.1.1:53
2026/10/26 05:06:43.740978 [Info] [3258984273] proxy/vmess/inbound: received request for udp:8.8.8.8:53
2026/10/26 05:06:43.740993 [Info] [3258984273] app/dispatcher: default route for udp:8.8.8.8:53
2026/10/26 05:06:43.741100 [Info] [3258984273] proxy/freedom: connection opened to udp:8.8.8.8:53, local endpoint [::]:58476, remote endpoint 8.8.8.8:53
2026/10/26 05:06:43.968147 [Info] [3189050357] proxy/vmess/inbound: received request for udp:172.217.117.4:443
2026/10/26 05:06:43.968275 [Info] [3189050357] app/dispatcher: default route for udp:172.217.117.4:443
2026/10/26 05:06:43.968287 [Info] [3189050357] proxy/freedom: connection opened to udp:172.217.117.4:443, local endpoint [::]:39824, remote endpoint 172.217.117.4:443
2026/10/26 05:06:43.972682 [Info] [1597614699] proxy/vmess/inbound: received request for udp:8.8.8.8:443
2026/10/26 05:06:43.972734 [Info] [1597614699] app/dispatcher: default route for udp:8.8.8.8:443
2026/10/26 05:06:43.972779 [Info] [1597614699] proxy/freedom: connection opened to udp:8.8.8.8:443, local endpoint [::]:47736, remote endpoint 8.8.8.8:443
2026/10/26 05:06:45.596127 [Info] [3498291493] proxy/vmess/inbound: received request for udp:172.217.116.4:443
2026/10/26 05:06:45.596500 [Info] [3498291493] app/dispatcher: default route for udp:172.217.116.4:443
2026/10/26 05:06:45.597420 [Info] [3498291493] proxy/freedom: connection opened to udp:172.217.116.4:443, local endpoint [::]:40759, remote endpoint 172.217.116.4:443
2026/10/26 05:06:46.307603 [Info] [3196753239] proxy/vmess/inbound: received request for tcp:www.gstatic.com:80
2026/10/26 05:06:46.307685 [Info] [3196753239] app/dispatcher: default route for tcp:www.gstatic.com:80
2026/10/26 05:06:46.308574 [Info] [3196753239] transport/internet/tcp: dialing TCP to tcp:www.gstatic.com:80
2026/10/26 05:06:46.312153 [Info] [3196753239] proxy/freedom: connection opened to tcp:www.gstatic.com:80, local endpoint 10.1.0.144:58002, remote endpoint 172.253.63.94:80
2026/10/26 05:06:49.621927 [Info] [750773064] app/proxyman/inbound: connection ends > proxy/vmess/inbound: invalid request from 127.0.0.1:60880 > proxy/vmess/encoding: failed to read request header > websocket: close 1000 (normal)
2026/10/26 05:06:50.192792 [Info] [3798303755] proxy/vmess/inbound: received request for udp:172.217.115.4:443
2026/10/26 05:06:50.192820 [Info] [3798303755] app/dispatcher: default route for udp:172.217.115.4:443
2026/10/26 05:06:50.192831 [Info] [3798303755] proxy/freedom: connection opened to udp:172.217.115.4:443, local endpoint [::]:50095, remote endpoint 172.217.115.4:443
2026/10/26 05:06:51.485572 [Info] [3189050357] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:06:51.485749 [Info] [1417924352] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:06:51.491524 [Info] [3798303755] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:06:51.491546 [Info] [2803451942] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:06:51.491552 [Info] [3258984273] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:06:51.491558 [Info] [3498291493] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:06:51.491564 [Info] [1597614699] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 05:06:51.491573 [Info] [32447166] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
```
