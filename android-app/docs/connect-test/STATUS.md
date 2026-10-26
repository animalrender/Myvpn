# connect-test — run 5

- branch: arena/b9372ae1-myvpn
- sha: 5c1682b3858d620a68ab015f69f8e1cadfc8b176
- started: 2026-10-26T04:50:33Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 26 04:45 /dev/kvm
- booted: 1
- apk: android-app/app/build/outputs/apk/release/app-release.apk
Performing Streamed Install
Success
Starting: Intent { cmp=co.asiven.vixentvpn/.trial.ui.MainActivity }
Status: ok
LaunchState: COLD
Activity: co.asiven.vixentvpn/.trial.ui.MainActivity
TotalTime: 4210
WaitTime: 4223
Complete

- connect-drive exit: 0

## Xray server access log
```
2026/10/26 04:51:57.084613 from 127.0.0.1:55260 accepted tcp:www.gstatic.com:443
2026/10/26 04:51:57.629379 from 127.0.0.1:55268 accepted tcp:www.gstatic.com:443
2026/10/26 04:51:57.850714 from 127.0.0.1:55280 accepted tcp:www.gstatic.com:443
2026/10/26 04:51:57.939075 from 127.0.0.1:55300 accepted udp:172.217.117.4:443
2026/10/26 04:51:58.595413 from 127.0.0.1:55308 accepted tcp:www.gstatic.com:443
2026/10/26 04:51:58.859381 from 127.0.0.1:55312 accepted tcp:rcs-acs-tmo-us.jibe.google.com:443
2026/10/26 04:51:58.905831 from 127.0.0.1:55320 accepted tcp:www.gstatic.com:80
2026/10/26 04:52:00.224478 from 127.0.0.1:45202 accepted tcp:android.apis.google.com:443
2026/10/26 04:52:01.792348 from 127.0.0.1:45216 accepted tcp:mtalk.google.com:5228
2026/10/26 04:52:01.852406 from 127.0.0.1:45228 accepted tcp:pagead2.googlesyndication.com:443
2026/10/26 04:52:02.832726 from 127.0.0.1:45232 accepted tcp:android.googleapis.com:443
2026/10/26 04:52:03.209579 from 127.0.0.1:45238 accepted tcp:voilatile-pa.googleapis.com:443
2026/10/26 04:52:03.236229 from 127.0.0.1:45244 accepted tcp:connectivitycheck.gstatic.com:80
2026/10/26 04:52:05.461394 from 127.0.0.1:45260 accepted tcp:android.googleapis.com:443
2026/10/26 04:52:06.208664 from 127.0.0.1:45272 accepted tcp:www.googleapis.com:443
2026/10/26 04:52:09.917679 from 127.0.0.1:45280 accepted tcp:www.gstatic.com:443
2026/10/26 04:52:10.476205 from 127.0.0.1:40854 accepted tcp:www.googleapis.com:443
2026/10/26 04:52:13.201015 from 127.0.0.1:40858 accepted udp:172.217.114.4:443
2026/10/26 04:52:15.025785 from 127.0.0.1:40862 accepted udp:142.251.154.119:443
2026/10/26 04:52:15.031481 from 127.0.0.1:40868 accepted tcp:www.google.com:443
2026/10/26 04:52:15.044787 from 127.0.0.1:40876 accepted tcp:www.google.com:443
2026/10/26 04:52:15.249295 from 127.0.0.1:40884 accepted tcp:android.googleapis.com:443
2026/10/26 04:52:16.096877 from 127.0.0.1:40898 accepted tcp:android.googleapis.com:443
2026/10/26 04:52:16.145911 from 127.0.0.1:40910 accepted udp:172.217.117.4:443
2026/10/26 04:52:19.781262 from 127.0.0.1:40920 accepted udp:172.217.113.4:443
2026/10/26 04:52:32.801617 from 127.0.0.1:34924 accepted tcp:dl.google.com:443
2026/10/26 04:52:35.691696 from 127.0.0.1:34936 accepted udp:172.217.117.4:443
2026/10/26 04:52:50.326553 from 127.0.0.1:33890 accepted udp:8.8.8.8:443
2026/10/26 04:52:50.328421 from 127.0.0.1:33916 accepted tcp:8.8.8.8:853
2026/10/26 04:52:50.328976 from 127.0.0.1:33900 accepted tcp:1.1.1.1:853
2026/10/26 04:52:50.592978 from 127.0.0.1:33930 accepted tcp:1.1.1.1:853
2026/10/26 04:52:50.754487 from 127.0.0.1:33946 accepted udp:8.8.8.8:443
2026/10/26 04:52:51.132966 from 127.0.0.1:33956 accepted udp:1.1.1.1:53
2026/10/26 04:52:52.150837 from 127.0.0.1:33962 accepted tcp:8.8.8.8:853
2026/10/26 04:52:52.468401 from 127.0.0.1:33978 accepted udp:8.8.8.8:443
2026/10/26 04:52:52.729592 from 127.0.0.1:33988 accepted udp:8.8.8.8:53
2026/10/26 04:52:52.733140 from 127.0.0.1:33992 accepted tcp:www.gstatic.com:80
2026/10/26 04:52:52.758026 from 127.0.0.1:33996 accepted tcp:mtalk.google.com:5228
2026/10/26 04:52:53.462089 from 127.0.0.1:34010 accepted udp:172.217.112.4:443
2026/10/26 04:52:53.481897 from 127.0.0.1:34020 accepted tcp:android.googleapis.com:443
```
## Xray server error log
```
2026/10/26 04:52:50.592903 [Info] [2462110247] transport/internet/tcp: dialing TCP to tcp:1.1.1.1:853
2026/10/26 04:52:50.611383 [Info] [2462110247] proxy/freedom: connection opened to tcp:1.1.1.1:853, local endpoint 10.1.0.34:42088, remote endpoint 1.1.1.1:853
2026/10/26 04:52:50.754388 [Info] [2820406809] proxy/vmess/inbound: received request for udp:8.8.8.8:443
2026/10/26 04:52:50.754416 [Info] [2820406809] app/dispatcher: default route for udp:8.8.8.8:443
2026/10/26 04:52:50.754507 [Info] [2820406809] proxy/freedom: connection opened to udp:8.8.8.8:443, local endpoint [::]:57369, remote endpoint 8.8.8.8:443
2026/10/26 04:52:51.132818 [Info] [4108107321] proxy/vmess/inbound: received request for udp:1.1.1.1:53
2026/10/26 04:52:51.132953 [Info] [4108107321] app/dispatcher: default route for udp:1.1.1.1:53
2026/10/26 04:52:51.132960 [Info] [4108107321] proxy/freedom: connection opened to udp:1.1.1.1:53, local endpoint [::]:60144, remote endpoint 1.1.1.1:53
2026/10/26 04:52:52.149738 [Info] [2502836553] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1006 (abnormal closure): unexpected EOF
2026/10/26 04:52:52.149900 [Info] [684879858] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1006 (abnormal closure): unexpected EOF
2026/10/26 04:52:52.150706 [Info] [3965965953] proxy/vmess/inbound: received request for tcp:8.8.8.8:853
2026/10/26 04:52:52.150718 [Info] [1495948857] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1006 (abnormal closure): unexpected EOF
2026/10/26 04:52:52.150848 [Info] [3965965953] app/dispatcher: default route for tcp:8.8.8.8:853
2026/10/26 04:52:52.150852 [Info] [3965965953] transport/internet/tcp: dialing TCP to tcp:8.8.8.8:853
2026/10/26 04:52:52.161434 [Info] [3965965953] proxy/freedom: connection opened to tcp:8.8.8.8:853, local endpoint 10.1.0.34:39568, remote endpoint 8.8.8.8:853
2026/10/26 04:52:52.468362 [Info] [1633253456] proxy/vmess/inbound: received request for udp:8.8.8.8:443
2026/10/26 04:52:52.468391 [Info] [1633253456] app/dispatcher: default route for udp:8.8.8.8:443
2026/10/26 04:52:52.468451 [Info] [1633253456] proxy/freedom: connection opened to udp:8.8.8.8:443, local endpoint [::]:38973, remote endpoint 8.8.8.8:443
2026/10/26 04:52:52.729461 [Info] [2111316701] proxy/vmess/inbound: received request for udp:8.8.8.8:53
2026/10/26 04:52:52.729521 [Info] [2111316701] app/dispatcher: default route for udp:8.8.8.8:53
2026/10/26 04:52:52.729607 [Info] [2111316701] proxy/freedom: connection opened to udp:8.8.8.8:53, local endpoint [::]:41652, remote endpoint 8.8.8.8:53
2026/10/26 04:52:52.733073 [Info] [2633077371] proxy/vmess/inbound: received request for tcp:www.gstatic.com:80
2026/10/26 04:52:52.733132 [Info] [2633077371] app/dispatcher: default route for tcp:www.gstatic.com:80
2026/10/26 04:52:52.734180 [Info] [2633077371] transport/internet/tcp: dialing TCP to tcp:www.gstatic.com:80
2026/10/26 04:52:52.745885 [Info] [2633077371] proxy/freedom: connection opened to tcp:www.gstatic.com:80, local endpoint 10.1.0.34:53488, remote endpoint 142.251.155.120:80
2026/10/26 04:52:52.757880 [Info] [1456123019] proxy/vmess/inbound: received request for tcp:mtalk.google.com:5228
2026/10/26 04:52:52.758019 [Info] [1456123019] app/dispatcher: default route for tcp:mtalk.google.com:5228
2026/10/26 04:52:52.760243 [Info] [1456123019] transport/internet/tcp: dialing TCP to tcp:mtalk.google.com:5228
2026/10/26 04:52:52.785581 [Info] [1456123019] proxy/freedom: connection opened to tcp:mtalk.google.com:5228, local endpoint 10.1.0.34:54144, remote endpoint 74.125.137.188:5228
2026/10/26 04:52:53.461952 [Info] [2334285889] proxy/vmess/inbound: received request for udp:172.217.112.4:443
2026/10/26 04:52:53.461995 [Info] [2334285889] app/dispatcher: default route for udp:172.217.112.4:443
2026/10/26 04:52:53.462097 [Info] [2334285889] proxy/freedom: connection opened to udp:172.217.112.4:443, local endpoint [::]:48592, remote endpoint 172.217.112.4:443
2026/10/26 04:52:53.481810 [Info] [951436340] proxy/vmess/inbound: received request for tcp:android.googleapis.com:443
2026/10/26 04:52:53.481825 [Info] [951436340] app/dispatcher: default route for tcp:android.googleapis.com:443
2026/10/26 04:52:53.482612 [Info] [951436340] transport/internet/tcp: dialing TCP to tcp:android.googleapis.com:443
2026/10/26 04:52:53.494631 [Info] [951436340] proxy/freedom: connection opened to tcp:android.googleapis.com:443, local endpoint 10.1.0.34:56288, remote endpoint 172.217.117.4:443
2026/10/26 04:52:57.818729 [Info] [2111316701] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 04:52:57.818849 [Info] [1633253456] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 04:52:57.820444 [Info] [2334285889] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > proxy/vmess/inbound: failed to transfer request > websocket: close 1000 (normal)
2026/10/26 04:52:58.820201 [Info] [1456123019] app/proxyman/inbound: connection ends > proxy/vmess/inbound: connection ends > context canceled
```
