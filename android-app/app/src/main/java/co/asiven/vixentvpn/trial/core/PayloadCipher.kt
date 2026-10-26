package co.asiven.vixentvpn.trial.core

import android.util.Base64
import javax.crypto.Cipher
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec

/**
 * Decrypts the backend's `Protocol.value` payload.
 *
 * The management backend does not hand out share links: every row carries a base64 blob that is
 * `AES/CBC/PKCS5Padding` over the real config, where
 *
 *   * the passphrase is the row id rendered as `"key_<id>"`, right-padded with `0x00` to 16 bytes
 *     (key size is AES-128, so ids up to 11 characters fit — negative ids are part of the
 *     reported id and must be used verbatim, e.g. `key_-16068`),
 *   * the IV is byte-identical to the key.
 *
 * The plaintext is either a share link (`vless://`, `vmess://`, `trojan://`, `ss://`, …) or a
 * ready-made Xray configuration (a JSON object with `inbounds`/`outbounds`/`routing`).
 *
 * This is the exact scheme the vendor's own tooling uses (`DecryptValue(value, protoID)` in the
 * panel source), which is why the trial build can now dial every row with zero user input.
 */
object PayloadCipher {

    const val KEY_PREFIX = "key_"
    private const val BLOCK = 16

    /** `"key_<id>"` zero-padded on the right up to one AES block. */
    fun keyFor(protocolId: Int): ByteArray {
        val material = (KEY_PREFIX + protocolId).toByteArray(Charsets.US_ASCII)
        val key = ByteArray(BLOCK)
        System.arraycopy(material, 0, key, 0, minOf(material.size, BLOCK))
        return key
    }

    /** Raw AES-CBC decrypt; `null` when the input is not a well-formed blob. */
    fun decrypt(payload: String, protocolId: Int): String? {
        val clean = payload.trim()
        if (clean.isEmpty()) return null
        val data = runCatching { Base64.decode(clean, Base64.DEFAULT) }.getOrNull() ?: return null
        if (data.isEmpty() || data.size % BLOCK != 0) return null
        val key = keyFor(protocolId)
        val cipher = runCatching { Cipher.getInstance("AES/CBC/PKCS5Padding") }.getOrNull() ?: return null
        val plain = runCatching {
            cipher.init(Cipher.DECRYPT_MODE, SecretKeySpec(key, "AES"), IvParameterSpec(key))
            cipher.doFinal(data)
        }.getOrNull() ?: return null
        return String(plain, Charsets.UTF_8)
    }

    /**
     * Turns whatever `value` holds into a dialable config.
     *
     * Already-readable payloads (share links, JSON) are returned untouched, so the same code path
     * keeps working if the backend ever ships plaintext again and the import-from-clipboard flow
     * stays intact.
     */
    fun unwrap(payload: String, protocolId: Int?): String {
        val raw = payload.trim()
        if (raw.isEmpty() || protocolId == null) return payload
        if (isReadable(raw)) return payload
        val plain = decrypt(raw, protocolId)?.trim().orEmpty()
        return if (isReadable(plain)) plain else payload
    }

    /** True when the text already is a share link or a JSON config. */
    fun isReadable(text: String): Boolean {
        val raw = text.trim()
        if (raw.isEmpty()) return false
        if (raw.startsWith("{") || raw.startsWith("[")) {
            return runCatching { org.json.JSONObject(raw).length() > 0 }.getOrDefault(false) ||
                runCatching { org.json.JSONArray(raw).length() > 0 }.getOrDefault(false)
        }
        val scheme = raw.substringBefore("://", "").lowercase()
        return scheme.isNotEmpty() && scheme.all { it.isLetterOrDigit() || it == '+' || it == '-' || it == '.' }
    }

    /** True when the text looks like an encrypted blob (used only for diagnostics/UI labels). */
    fun looksEncrypted(text: String): Boolean {
        val raw = text.trim()
        if (raw.length < 24 || isReadable(raw)) return false
        val body = raw.filterNot { it == '=' || it == '\n' || it == '\r' }
        return body.isNotEmpty() && body.all { it.isLetterOrDigit() || it == '+' || it == '/' || it == '-' || it == '_' }
    }
}
