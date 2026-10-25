#!/usr/bin/env bash
# Builds hev-socks5-tunnel's JNI shared library for arm64-v8a with the package name this
# app expects, and stages it into app/src/main/jniLibs/arm64-v8a/.
#
# Same approach as v2rayNG's compile-hevtun.sh: ndk-build over a temporary jni/ tree that
# symlinks the hev source, with -DPKGNAME=<our java package>.
set -euo pipefail

HEV_VERSION="${HEV_VERSION:-2.19.3}"
# Java package that hosts the native methods (see service/TProxyService.java).
PKGNAME="${HEV_PKGNAME:-co/asiven/vixentvpn/service}"
CLSNAME="${HEV_CLSNAME:-TProxyService}"
ABI="${HEV_ABI:-arm64-v8a}"
API_LEVEL="${HEV_API:-24}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
JNI_DIR="$ROOT/app/src/main/jniLibs"
NDK_HOME="${NDK_HOME:-${ANDROID_NDK_LATEST_HOME:-}}"
if [[ -z "$NDK_HOME" || ! -d "$NDK_HOME" ]]; then
  NDK_HOME="$(ls -d "${ANDROID_HOME:-/usr/local/lib/android/sdk}"/ndk/* 2>/dev/null | sort -V | tail -1 || true)"
fi
if [[ -z "$NDK_HOME" || ! -d "$NDK_HOME" ]]; then
  echo "!! Android NDK not found (set NDK_HOME)" >&2
  exit 1
fi
echo "==> NDK: $NDK_HOME"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "==> fetching hev-socks5-tunnel $HEV_VERSION"
TARBALL="$TMPDIR/hev.tar.gz"
curl -fL --retry 5 --retry-delay 3 --retry-all-errors --connect-timeout 20 \
  -o "$TARBALL" \
  "https://github.com/heiher/hev-socks5-tunnel/archive/refs/tags/${HEV_VERSION}.tar.gz"
tar -xzf "$TARBALL" -C "$TMPDIR"
SRC_DIR="$(find "$TMPDIR" -maxdepth 1 -type d -name 'hev-socks5-tunnel-*' | head -1)"
[[ -n "$SRC_DIR" ]] || { echo "!! unexpected tarball layout" >&2; exit 1; }

mkdir -p "$TMPDIR/build/jni"
ln -s "$SRC_DIR" "$TMPDIR/build/jni/hev-socks5-tunnel"
echo 'include $(call all-subdir-makefiles)' > "$TMPDIR/build/jni/Android.mk"

pushd "$TMPDIR/build" >/dev/null
"$NDK_HOME/ndk-build" \
  NDK_PROJECT_PATH=. \
  APP_BUILD_SCRIPT=jni/Android.mk \
  "APP_ABI=$ABI" \
  "APP_PLATFORM=android-$API_LEVEL" \
  NDK_LIBS_OUT="$TMPDIR/libs" \
  NDK_OUT="$TMPDIR/obj" \
  "APP_CFLAGS=-O3 -DPKGNAME=$PKGNAME -DCLSNAME=$CLSNAME" \
  "APP_LDFLAGS=-Wl,--build-id=none -Wl,--hash-style=gnu"
popd >/dev/null

LIB="$TMPDIR/libs/$ABI/libhev-socks5-tunnel.so"
[[ -f "$LIB" ]] || { echo "!! build produced no library" >&2; exit 1; }

mkdir -p "$JNI_DIR/$ABI"
cp "$LIB" "$JNI_DIR/$ABI/libhev-socks5-tunnel.so"
echo "==> staged $(du -h "$JNI_DIR/$ABI/libhev-socks5-tunnel.so" | cut -f1) at app/src/main/jniLibs/$ABI/"
file "$JNI_DIR/$ABI/libhev-socks5-tunnel.so" || true
