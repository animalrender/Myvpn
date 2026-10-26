# connect-test — run 3

- branch: arena/b9372ae1-myvpn
- sha: 0c4d130c1f4f2675e287e7a99e7139ab8fd202e0
- started: 2026-10-26T04:15:06Z
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 26 04:11 /dev/kvm
- booted: 1
- apk: android-app/app/build/outputs/apk/release/app-release.apk
Performing Streamed Install
Success
Starting: Intent { cmp=co.asiven.vixentvpn/.trial.ui.MainActivity }
Status: ok
LaunchState: COLD
Activity: co.asiven.vixentvpn/.trial.ui.MainActivity
TotalTime: 3042
WaitTime: 3056
Complete

- connect-drive exit: 1

## Xray server access log
```
2026/10/26 04:16:27.827013 from 127.0.0.1:38486 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:29.258178 from 127.0.0.1:38500 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:29.353556 from 127.0.0.1:38502 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:29.570679 from 127.0.0.1:38516 accepted tcp:www.gstatic.com:80
2026/10/26 04:16:30.211586 from 127.0.0.1:38528 accepted udp:172.217.112.4:443
2026/10/26 04:16:30.395481 from 127.0.0.1:38530 accepted udp:172.217.112.4:443
2026/10/26 04:16:30.517564 from 127.0.0.1:38546 accepted udp:172.217.118.4:443
2026/10/26 04:16:30.606889 from 127.0.0.1:38548 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:30.699857 from 127.0.0.1:38562 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:30.710735 from 127.0.0.1:38570 accepted udp:172.217.118.4:443
2026/10/26 04:16:30.807179 from 127.0.0.1:38580 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:31.131024 from 127.0.0.1:38592 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:31.186422 from 127.0.0.1:38608 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:31.198311 from 127.0.0.1:38614 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:31.573012 from 127.0.0.1:38628 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:31.590002 from 127.0.0.1:38634 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:32.290956 from 127.0.0.1:38654 accepted udp:172.217.118.4:443
2026/10/26 04:16:32.489520 from 127.0.0.1:38666 accepted udp:172.217.118.4:443
2026/10/26 04:16:33.019530 from 127.0.0.1:55062 accepted udp:172.217.117.4:443
2026/10/26 04:16:33.403147 from 127.0.0.1:55076 accepted tcp:android.apis.google.com:443
2026/10/26 04:16:33.900681 from 127.0.0.1:55090 accepted tcp:connectivitycheck.gstatic.com:80
2026/10/26 04:16:33.904608 from 127.0.0.1:55094 accepted tcp:rcs-acs-tmo-us.jibe.google.com:443
2026/10/26 04:16:34.818974 from 127.0.0.1:55100 accepted tcp:android.googleapis.com:443
2026/10/26 04:16:35.871128 from 127.0.0.1:55104 accepted tcp:mtalk.google.com:5228
2026/10/26 04:16:36.539196 from 127.0.0.1:55106 accepted tcp:pagead2.googlesyndication.com:443
2026/10/26 04:16:37.135206 from 127.0.0.1:55110 accepted tcp:android.googleapis.com:443
2026/10/26 04:16:37.626904 from 127.0.0.1:55124 accepted tcp:voilatile-pa.googleapis.com:443
2026/10/26 04:16:40.410565 from 127.0.0.1:55126 accepted tcp:www.gstatic.com:443
2026/10/26 04:16:41.411313 from 127.0.0.1:55138 accepted tcp:www.googleapis.com:443
2026/10/26 04:16:42.374854 from 127.0.0.1:55146 accepted tcp:android.googleapis.com:443
2026/10/26 04:16:43.355772 from 127.0.0.1:50022 accepted tcp:www.googleapis.com:443
2026/10/26 04:16:48.764108 from 127.0.0.1:50042 accepted udp:142.251.150.119:443
2026/10/26 04:16:48.764691 from 127.0.0.1:50034 accepted tcp:www.google.com:443
2026/10/26 04:16:48.839402 from 127.0.0.1:50050 accepted udp:172.217.115.4:443
2026/10/26 04:16:50.475408 from 127.0.0.1:50066 accepted tcp:android.googleapis.com:443
2026/10/26 04:16:50.719971 from 127.0.0.1:50082 accepted udp:172.217.117.4:443
2026/10/26 04:16:51.507674 from 127.0.0.1:50090 accepted tcp:android.googleapis.com:443
2026/10/26 04:17:02.315863 from 127.0.0.1:52100 accepted udp:172.217.113.4:443
2026/10/26 04:17:05.575798 from 127.0.0.1:52486 accepted tcp:dl.google.com:443
2026/10/26 04:17:12.447938 from 127.0.0.1:52494 accepted udp:172.217.117.4:443
```
## Xray server error log
```
2026/10/26 04:16:48.764090 [Info] [1612559775] proxy/vless/inbound: received request for udp:142.251.150.119:443
2026/10/26 04:16:48.764095 [Info] [1612559775] app/dispatcher: default route for udp:142.251.150.119:443
2026/10/26 04:16:48.764101 [Info] [1612559775] proxy/freedom: connection opened to udp:142.251.150.119:443, local endpoint [::]:47345, remote endpoint 142.251.150.119:443
2026/10/26 04:16:48.764703 [Info] [2269625834] proxy/vless/inbound: firstLen = 554
2026/10/26 04:16:48.764708 [Info] [2269625834] proxy/vless/inbound: received request for tcp:www.google.com:443
2026/10/26 04:16:48.764712 [Info] [2269625834] app/dispatcher: default route for tcp:www.google.com:443
2026/10/26 04:16:48.768192 [Info] [2269625834] transport/internet/tcp: dialing TCP to tcp:www.google.com:443
2026/10/26 04:16:48.772328 [Info] [2269625834] proxy/freedom: connection opened to tcp:www.google.com:443, local endpoint 10.1.0.217:59364, remote endpoint 142.251.157.119:443
2026/10/26 04:16:48.839350 [Info] [3199032005] proxy/vless/inbound: firstLen = 1360
2026/10/26 04:16:48.839368 [Info] [3199032005] proxy/vless/inbound: received request for udp:172.217.115.4:443
2026/10/26 04:16:48.839373 [Info] [3199032005] app/dispatcher: default route for udp:172.217.115.4:443
2026/10/26 04:16:48.839380 [Info] [3199032005] proxy/freedom: connection opened to udp:172.217.115.4:443, local endpoint [::]:52459, remote endpoint 172.217.115.4:443
2026/10/26 04:16:50.475358 [Info] [2593379537] proxy/vless/inbound: firstLen = 562
2026/10/26 04:16:50.475381 [Info] [2593379537] proxy/vless/inbound: received request for tcp:android.googleapis.com:443
2026/10/26 04:16:50.475386 [Info] [2593379537] app/dispatcher: default route for tcp:android.googleapis.com:443
2026/10/26 04:16:50.477384 [Info] [2593379537] transport/internet/tcp: dialing TCP to tcp:android.googleapis.com:443
2026/10/26 04:16:50.489776 [Info] [2593379537] proxy/freedom: connection opened to tcp:android.googleapis.com:443, local endpoint 10.1.0.217:49000, remote endpoint 172.217.117.4:443
2026/10/26 04:16:50.719926 [Info] [3470989157] proxy/vless/inbound: firstLen = 1278
2026/10/26 04:16:50.719951 [Info] [3470989157] proxy/vless/inbound: received request for udp:172.217.117.4:443
2026/10/26 04:16:50.719957 [Info] [3470989157] app/dispatcher: default route for udp:172.217.117.4:443
2026/10/26 04:16:50.719964 [Info] [3470989157] proxy/freedom: connection opened to udp:172.217.117.4:443, local endpoint [::]:58277, remote endpoint 172.217.117.4:443
2026/10/26 04:16:51.507652 [Info] [3034152350] proxy/vless/inbound: firstLen = 562
2026/10/26 04:16:51.507671 [Info] [3034152350] proxy/vless/inbound: received request for tcp:android.googleapis.com:443
2026/10/26 04:16:51.507677 [Info] [3034152350] app/dispatcher: default route for tcp:android.googleapis.com:443
2026/10/26 04:16:51.508794 [Info] [3034152350] transport/internet/tcp: dialing TCP to tcp:android.googleapis.com:443
2026/10/26 04:16:51.512949 [Info] [3034152350] proxy/freedom: connection opened to tcp:android.googleapis.com:443, local endpoint 10.1.0.217:60104, remote endpoint 172.217.118.4:443
2026/10/26 04:17:02.315820 [Info] [3675087683] proxy/vless/inbound: firstLen = 1278
2026/10/26 04:17:02.315853 [Info] [3675087683] proxy/vless/inbound: received request for udp:172.217.113.4:443
2026/10/26 04:17:02.315860 [Info] [3675087683] app/dispatcher: default route for udp:172.217.113.4:443
2026/10/26 04:17:02.315871 [Info] [3675087683] proxy/freedom: connection opened to udp:172.217.113.4:443, local endpoint [::]:53289, remote endpoint 172.217.113.4:443
2026/10/26 04:17:05.575757 [Info] [1890693615] proxy/vless/inbound: firstLen = 553
2026/10/26 04:17:05.575782 [Info] [1890693615] proxy/vless/inbound: received request for tcp:dl.google.com:443
2026/10/26 04:17:05.575788 [Info] [1890693615] app/dispatcher: default route for tcp:dl.google.com:443
2026/10/26 04:17:05.576616 [Info] [1890693615] transport/internet/tcp: dialing TCP to tcp:dl.google.com:443
2026/10/26 04:17:05.581444 [Info] [1890693615] proxy/freedom: connection opened to tcp:dl.google.com:443, local endpoint 10.1.0.217:37536, remote endpoint 192.178.164.91:443
2026/10/26 04:17:12.403830 [Info] [1954226650] app/proxyman/inbound: connection ends > EOF
2026/10/26 04:17:12.447888 [Info] [2050389053] proxy/vless/inbound: firstLen = 1460
2026/10/26 04:17:12.447911 [Info] [2050389053] proxy/vless/inbound: received request for udp:172.217.117.4:443
2026/10/26 04:17:12.447917 [Info] [2050389053] app/dispatcher: default route for udp:172.217.117.4:443
2026/10/26 04:17:12.447951 [Info] [2050389053] proxy/freedom: connection opened to udp:172.217.117.4:443, local endpoint [::]:60608, remote endpoint 172.217.117.4:443
```
