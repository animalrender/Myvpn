#!/usr/bin/env bash
# Fetches libv2ray.aar (gomobile build of xtls/xray-core) from the AndroidLibXrayLite
# release and drops it into app/libs. Runs inside GitHub Actions, where release assets
# are reachable.
set -euo pipefail

VERSION="${LIBV2RAY_VERSION:-v26.10.21}"
DEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/app/libs"
DEST="$DEST_DIR/libv2ray.aar"

mkdir -p "$DEST_DIR"

URLS=(
  "https://github.com/2dust/AndroidLibXrayLite/releases/download/${VERSION}/libv2ray.aar"
  "https://github.com/2dust/AndroidLibXrayLite/releases/latest/download/libv2ray.aar"
)

for url in "${URLS[@]}"; do
  echo "==> downloading $url"
  if curl -fL --retry 5 --retry-delay 3 --retry-all-errors --connect-timeout 20 -o "$DEST" "$url"; then
    if unzip -l "$DEST" >/dev/null 2>&1; then
      echo "==> ok: $(du -h "$DEST" | cut -f1)"
      # sanity: the AAR must contain arm64 JNI code and the libv2ray classes
      unzip -l "$DEST" | grep -q "lib/arm64-v8a/" || { echo "!! no arm64 JNI in AAR"; exit 1; }
      unzip -l "$DEST" | grep -q "classes.jar" || { echo "!! no classes.jar in AAR"; exit 1; }
      unzip -p "$DEST" classes.jar > /tmp/libv2ray-classes.jar
      unzip -l /tmp/libv2ray-classes.jar | grep -q "libv2ray/Libv2ray.class" \
        || { echo "!! libv2ray.Libv2ray not found in classes.jar"; exit 1; }
      echo "==> libv2ray.aar verified"
      exit 0
    fi
    echo "!! downloaded file is not a zip"
  fi
  rm -f "$DEST"
done

echo "!! could not obtain libv2ray.aar" >&2
exit 1
