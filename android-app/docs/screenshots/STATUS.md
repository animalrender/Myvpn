# ui-snapshot — run 16

- branch: arena/b9372ae1-myvpn
- sha: c668b7d388e251fa3fed11e3de576c2b574b20e7
- started: 2026-10-26T02:51:49Z
- kvm: crw-rw---- 1 root kvm 10, 232 Oct 26 02:51 /dev/kvm
- user: runner / groups: runner adm users docker systemd-journal
- python: Python 3.12.3
- adb: Android Debug Bridge version 1.0.41

## Emulator setup
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 26 02:51 /dev/kvm
- emulator: Android emulator version 37.2.12.0 (build_id 16428233) (CL:N/A) Copyright (C) 2006-2024 The Android Open Source Project and many others. This program is a derivative of the QEMU CPU emulator (www.qemu.org). 
- avd create: Loading local repository...                                                     [=========                              ] 25% Loading local repository...       [=========                              ] 25% Fetch remote repository...        [=======================================] 100% Fetch remote repository...        Auto-selecting single ABI x86_64 
- avd files: mvpn.avd mvpn.ini 
- images: x86_64 

## Device
- booted: 1 (waited 40s)
- model: sdk_gphone64_x86_64
- api: 34
- abi: x86_64
- devices: List of devices attachedemulator-5554	device
Physical size: 1080x2280
Physical density: 440
- apk: android-app/app/build/outputs/apk/release/app-release.apk (47M)

## Steps
- install: Performing Streamed Install
Success
- start: Starting: Intent { cmp=co.asiven.vixentvpn/.trial.ui.MainActivity } Status: ok LaunchState: COLD Activity: co.asiven.vixentvpn/.trial.ui.MainActivity TotalTime: 2924 WaitTime: 2963 Complete 
- ui-drive exit: 0
- pid: 3306
