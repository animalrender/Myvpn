# ui-snapshot — run 8

- branch: arena/b9372ae1-myvpn
- sha: 635a1930afdd334fddcfc5f97d946bc83bdaf5c9
- started: 2026-10-26T01:37:30Z
- kvm: crw-rw---- 1 root kvm 10, 232 Oct 26 01:34 /dev/kvm
- user: runner / groups: runner adm users docker systemd-journal
- python: Python 3.12.3
- adb: Android Debug Bridge version 1.0.41

## Emulator setup
- kvm: crw-rw-rw- 1 root kvm 10, 232 Oct 26 01:34 /dev/kvm
- emulator: /usr/local/lib/android/sdk/emulator/qemu/linux-x86_64/qemu-system-x86_64: error while loading shared libraries: libpulse.so.0: cannot open shared object file: No such file or directory
- avds: 
- images: x86_64 

## Device
- booted: 0 (waited 1000s)
- model: adb: no devices/emulators found
- api: adb: no devices/emulators found
- abi: adb: no devices/emulators found
- devices: List of devices attached

emulator did not boot; tail of /tmp/emulator.log:
```
INFO         | Android emulator version 37.2.12.0 (build_id 16428233) (CL:N/A)
INFO         | Graphics backend: gfxstream
ERROR        | Unknown AVD name [mvpn], use -list-avds to see valid list.
ERROR        | HOME is defined but there is no file mvpn.ini in $HOME/.android/avd
ERROR        | (Note: Directories are searched in the order $ANDROID_AVD_HOME, $ANDROID_SDK_HOME/avd and $HOME/.android/avd)
```
