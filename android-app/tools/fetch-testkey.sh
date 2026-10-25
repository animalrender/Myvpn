#!/usr/bin/env bash
# Builds the release keystore for the trial build.
#
# WHY THE AOSP TEST KEY:
#   The analysed APK is signed with the *public* AOSP test key
#   (cert SHA-256 a40da80a59d170caa950cf15c18c454d47a39b26989d8b640ecd745ba71bf5dc).
#   The backend authenticates every request with `sign` / `sha_hexadecimal`, which are
#   SHA-256 hashes of the *signing certificate*. Signing this trial build with the same
#   key makes those headers byte-identical to the original client, which is required for
#   the API to answer. Nothing secret is involved: it is the well-known Android testkey.
#
# Output: android-app/signing/keystore.properties + keystore.p12 (git-ignored).
# If the key cannot be fetched, a throw-away keystore is generated instead and the build
# continues (the release notes then warn that the API may reject the signature).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT/signing"
mkdir -p "$OUT_DIR"
EXPECTED="a40da80a59d170caa950cf15c18c454d47a39b26989d8b640ecd745ba71bf5dc"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fetch() { # $1=url  $2=output  $3=b64?
  curl -fL --retry 4 --retry-delay 2 --retry-all-errors --connect-timeout 20 -o "$TMP/raw" "$1" || return 1
  if [[ "${3:-}" == "b64" ]]; then
    base64 -d "$TMP/raw" > "$2" 2>/dev/null || return 1
  else
    cp "$TMP/raw" "$2"
  fi
  [[ -s "$2" ]]
}

PK8="$TMP/testkey.pk8"
PEM="$TMP/testkey.x509.pem"
GOT_KEY=0

try_pair() { # $1=pk8 url  $2=pem url  $3=b64 (both)
  fetch "$1" "$PK8" "${3:-}" && fetch "$2" "$PEM" "${3:-}" && GOT_KEY=1
}

try_pair \
  "https://raw.githubusercontent.com/aosp-mirror/platform_build/master/target/product/security/testkey.pk8" \
  "https://raw.githubusercontent.com/aosp-mirror/platform_build/master/target/product/security/testkey.x509.pem" "" \
|| try_pair \
  "https://android.googlesource.com/platform/build/+/refs/heads/main/target/product/security/testkey.pk8?format=TEXT" \
  "https://android.googlesource.com/platform/build/+/refs/heads/main/target/product/security/testkey.x509.pem?format=TEXT" "b64" \
|| try_pair \
  "https://github.com/aosp-mirror/platform_build/raw/master/target/product/security/testkey.pk8" \
  "https://github.com/aosp-mirror/platform_build/raw/master/target/product/security/testkey.x509.pem" "" \
|| true

FINGERPRINT=""
if [[ "$GOT_KEY" == "1" ]]; then
  FINGERPRINT="$(openssl x509 -in "$PEM" -noout -fingerprint -sha256 2>/dev/null \
    | sed 's/.*=//; s/://g' | tr 'A-Z' 'a-z')"
  echo "==> fetched AOSP testkey, sha256=$FINGERPRINT"
fi

if [[ "$FINGERPRINT" == "$EXPECTED" ]]; then
  echo "==> testkey matches the analysed APK signature — API headers will be identical"
  openssl pkcs8 -inform DER -nocrypt -in "$PK8" -out "$TMP/testkey.pem" 2>/dev/null
  openssl pkcs12 -export -inkey "$TMP/testkey.pem" -in "$PEM" \
    -name testkey -out "$OUT_DIR/keystore.p12" -passout pass:android >/dev/null 2>&1
  {
    echo "storeFile=signing/keystore.p12"
    echo "storePassword=android"
    echo "keyAlias=testkey"
    echo "keyPassword=android"
  } > "$OUT_DIR/keystore.properties"
  echo "testkey (AOSP, sha256=$EXPECTED)" > "$OUT_DIR/SIGNING_INFO.txt"
  exit 0
fi

echo "!! AOSP testkey unavailable (fingerprint='${FINGERPRINT}') — generating a throw-away key" >&2
rm -f "$OUT_DIR/keystore.p12"
keytool -genkeypair -v -keystore "$OUT_DIR/keystore.p12" -storetype PKCS12 \
  -alias mvpn -keyalg RSA -keysize 2048 -validity 10000 \
  -storepass android -keypass android \
  -dname "CN=MVPN Trial, O=MVPN, C=IR" >/dev/null 2>&1
{
  echo "storeFile=signing/keystore.p12"
  echo "storePassword=android"
  echo "keyAlias=mvpn"
  echo "keyPassword=android"
} > "$OUT_DIR/keystore.properties"
echo "throw-away key (AOSP testkey could not be downloaded)" > "$OUT_DIR/SIGNING_INFO.txt"
exit 0
