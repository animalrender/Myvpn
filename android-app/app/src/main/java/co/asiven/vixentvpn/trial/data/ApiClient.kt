package co.asiven.vixentvpn.trial.data

import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import android.util.Base64
import co.asiven.vixentvpn.trial.BuildConfig
import co.asiven.vixentvpn.trial.util.AppLog
import org.json.JSONObject
import java.io.BufferedReader
import java.net.HttpURLConnection
import java.net.URL
import java.security.MessageDigest
import java.util.Locale

/**
 * Client for the backend of the analysed APK — byte-for-byte the same request contract.
 *
 * Endpoints:
 *   GET  {api}/api/token?deviceId=…[&firebase_token=…]
 *   GET  {api}/api/setting
 *   GET  {api}/api/protocols            (+ /api/protocols/ and /api/v2/protocols as fallbacks)
 *   GET  {api}/api/configs?deviceId=…&serverId=…&protocolId=…
 *
 * Headers, exactly as `VolleyHelper.initHeaders()` builds them:
 *   Content-Type      application/json
 *   app_name          co.asiven.vixentvpn (the id the backend knows; this build ships as
 *                     co.asiven.vixentvpn.trial so it can live next to the original app)
 *   version_code      <versionCode>            (1004220)
 *   seen              <admobSeen int>          (0)
 *   token             only when a real token exists
 *   sign              Base64(MD5(certificate DER))          ← MUST be MD5, not SHA-256
 *   sha_hexadecimal   hex(SHA-256(SHA-256(certificate DER)))  (several certs joined by ",")
 *   Authorization     "bearer <token>" only when a real token exists
 *
 * Every response is an envelope `{statusCode, status, data}` and the backend reports logical
 * errors with **HTTP 200** (`{"statusCode":400,"status":false,"data":"Internal server error."}`),
 * so an HTTP 200 alone is never treated as success.
 */
class ApiClient(private val context: Context, private val prefs: Prefs) {

    data class Result(val code: Int, val body: String, val url: String) {
        val httpOk: Boolean get() = code in 200..299 && body.isNotBlank()

        /** Envelope-aware success check: `statusCode == 200 && status == true` (or a bare payload). */
        val ok: Boolean
            get() {
                if (!httpOk) return false
                val json = parseObject(body) ?: return !body.trimStart().startsWith("{")
                return envelopeOk(json)
            }

        /** Human readable error text (`data`/`message`) for logs and dialogs. */
        val errorText: String
            get() {
                if (!httpOk) return "HTTP $code"
                val json = parseObject(body)
                if (json == null) return body.take(200)
                val data = json.opt("data")
                return when {
                    data is String && data.isNotBlank() && data != "null" -> data
                    json.has("message") -> json.optString("message")
                    else -> body.take(200)
                }
            }
    }

    private val signing: Signing.Info? by lazy { Signing.info(context.packageName, context) }

    val baseUrl: String get() = normalise(prefs.apiUrl.ifBlank { BuildConfig.API_BASE })

    // ---------------------------------------------------------------- public API

    /**
     * `GET /api/token`. This backend currently answers `{"statusCode":0,"data":"The app token is
     * disabled"}`, which is a valid state, not a failure: the client then simply works without a
     * token (the baseline puts the header only when the value is non-empty).
     */
    fun fetchToken(): String? {
        val deviceId = prefs.deviceId
        val firebase = prefs.firebaseToken
        val firebaseQuery =
            if (firebase.isBlank()) "" else "&firebase_token=" + java.net.URLEncoder.encode(firebase, "UTF-8")

        val attempts = listOf(
            "/api/token?deviceId=$deviceId$firebaseQuery",
            "/api/token/?deviceId=$deviceId$firebaseQuery",
        )
        for (path in attempts) {
            val result = request("GET", path)
            if (!result.httpOk) {
                AppLog.w("توکن: ${result.url} → ${result.code}")
                continue
            }
            val token = extractToken(result.body)
            if (token != null) {
                prefs.token = token
                AppLog.i("token دریافت شد (${token.take(6)}…)")
                return token
            }
            if (result.body.contains("disabled", ignoreCase = true)) {
                prefs.token = ""
                AppLog.i("توکن سمت سرور غیرفعال است؛ بدون هدر token ادامه می‌دهیم")
                return null
            }
            AppLog.w("پاسخ توکن قابل استفاده نبود: ${result.body.take(200)}")
        }
        prefs.token = ""
        return null
    }

    fun fetchSetting(): AppSetting? {
        val result = request("GET", "/api/setting")
        if (!result.ok) {
            AppLog.w("setting: ${result.code} ${result.errorText}")
            return null
        }
        val json = parseObject(result.body) ?: return null
        val payload = unwrap(json) as? JSONObject ?: JSONObject()
        if (payload.length() == 0) {
            AppLog.i("setting خالی است (data=null) — پیش‌فرض‌های برنامه استفاده می‌شوند")
            return null
        }
        val setting = AppSetting.from(payload)
        prefs.settingsCache = payload.toString()
        setting.apiUrl?.takeIf { it.startsWith("http") && it != prefs.apiUrl }?.let {
            AppLog.i("apiUrl از راه دور به‌روزرسانی شد: $it")
            prefs.apiUrl = it.trimEnd('/')
        }
        setting.testUrl?.takeIf { it.startsWith("http") }?.let { prefs.testUrl = it }
        return setting
    }

    /** The full server list — `/api/protocols`, with `/api/v2/protocols` as a richer fallback. */
    fun fetchProtocols(): List<Server> {
        val paths = listOf("/api/protocols", "/api/protocols/", "/api/v2/protocols")
        val errors = mutableListOf<String>()
        for (path in paths) {
            val result = request("GET", path)
            if (!result.ok) {
                errors += "$path → ${result.code} ${result.errorText}"
                AppLog.w("protocols: $path → ${result.code} | ${result.errorText}")
                continue
            }
            val json = parseObject(result.body) ?: continue
            val servers = ServerParser.parseList(json)
            if (servers.isEmpty()) {
                errors += "$path → پاسخ بدون سرور"
                continue
            }
            prefs.protocolsCache = json.toString()
            prefs.protocolsSource = path
            AppLog.i("${servers.size} سرور از $path دریافت شد")
            return servers
        }
        lastError = errors.joinToString("\n")
        AppLog.e("دریافت فهرست سرورها شکست خورد:\n$lastError")
        return emptyList()
    }

    var lastError: String = ""
        private set

    /**
     * On-device contract test: runs every endpoint with the real headers and returns a readable
     * report. Shown from the overflow menu so a failing build can be diagnosed without a PC.
     */
    fun selfTest(): String {
        val sb = StringBuilder()
        val sign = signing
        sb.appendLine("BASE: $baseUrl")
        sb.appendLine("app_name: ${BuildConfig.HEADER_APP_NAME}   version_code: ${BuildConfig.HEADER_VERSION_CODE}")
        if (sign == null) {
            sb.appendLine("!! گواهی امضا خوانده نشد → هدرهای sign/sha ارسال نمی‌شوند")
        } else {
            sb.appendLine("sign = ${sign.signBase64}")
            sb.appendLine("sha_hexadecimal = ${sign.shaHex}")
        }
        sb.appendLine("deviceId: ${prefs.deviceId}")
        sb.appendLine("token (ذخیره‌شده): ${prefs.token.ifBlank { "—" }}")
        sb.appendLine("firebase_token: ${prefs.firebaseToken.ifBlank { "—" }}")
        sb.appendLine()
        for (path in listOf(
            "/api/token?deviceId=${prefs.deviceId}",
            "/api/setting",
            "/api/protocols",
            "/api/v2/protocols",
            "/api/configs?deviceId=${prefs.deviceId}",
        )) {
            val r = request("GET", path)
            val items = runCatching { (parseObject(r.body)?.opt("data") as? org.json.JSONArray)?.length() }.getOrNull()
            sb.appendLine("$path")
            sb.appendLine("  HTTP ${r.code} · ${r.body.length}B · ok=${r.ok}${items?.let { " · items=$it" } ?: ""}")
            sb.appendLine("  ${r.body.take(220).replace("\n", " ")}")
        }
        return sb.toString()
    }

    // ---------------------------------------------------------------- HTTP layer

    private fun request(method: String, path: String, body: String? = null): Result {
        val url = baseUrl + path
        var connection: HttpURLConnection? = null
        return try {
            connection = (URL(url).openConnection() as HttpURLConnection).apply {
                requestMethod = method
                connectTimeout = 20_000
                readTimeout = 25_000
                instanceFollowRedirects = true
                doInput = true
                headers().forEach { (k, v) -> setRequestProperty(k, v) }
                if (body != null) {
                    doOutput = true
                    outputStream.use { it.write(body.toByteArray(Charsets.UTF_8)) }
                }
            }
            val code = connection.responseCode
            val stream = if (code in 200..299) connection.inputStream else connection.errorStream
            val text = stream?.bufferedReader()?.use(BufferedReader::readText).orEmpty()
            AppLog.d("$method $url → $code (${text.length} بایت)")
            Result(code, text, url)
        } catch (t: Throwable) {
            AppLog.e("$method $url ناموفق", t)
            Result(-1, "", url)
        } finally {
            runCatching { connection?.disconnect() }
        }
    }

    /** The exact `VolleyHelper.initHeaders()` set. */
    private fun headers(): Map<String, String> {
        val map = linkedMapOf(
            "Content-Type" to "application/json",
            "Accept" to "application/json",
            "User-Agent" to userAgent(),
            "app_name" to BuildConfig.HEADER_APP_NAME,
            "version_code" to BuildConfig.HEADER_VERSION_CODE.toString(),
            "seen" to prefs.admobSeen.toString(),
        )
        val token = prefs.token.trim()
        if (token.isNotEmpty()) map["token"] = token
        signing?.let { info ->
            map["sign"] = info.signBase64
            map["sha_hexadecimal"] = info.shaHex
        }
        // `Authorization: bearer …` is only added when the backend actually issued a token
        // (`Lo4/c.c` is empty otherwise — sending a placeholder breaks the request).
        if (token.isNotEmpty()) map["Authorization"] = "bearer $token"
        return map
    }

    private fun userAgent(): String =
        "Dalvik/2.1.0 (Linux; U; Android ${Build.VERSION.RELEASE}; ${Build.MODEL} Build/${Build.ID})"

    private fun normalise(url: String): String = url.trim().trimEnd('/').ifBlank { BuildConfig.API_BASE }

    companion object {

        /** `statusCode`/`status` of an envelope, tolerant to strings and missing fields. */
        fun envelopeOk(json: JSONObject): Boolean {
            val statusCode = coerceInt(json.opt("statusCode")) ?: 200
            val status = coerceBool(json.opt("status")) ?: true
            return statusCode == 200 && status
        }

        fun coerceInt(value: Any?): Int? = when (value) {
            null, JSONObject.NULL -> null
            is Number -> value.toInt()
            is String -> value.trim().toIntOrNull()
            is Boolean -> if (value) 1 else 0
            else -> null
        }

        fun coerceBool(value: Any?): Boolean? = when (value) {
            null, JSONObject.NULL -> null
            is Boolean -> value
            is Number -> value.toInt() != 0
            is String -> when (value.trim().lowercase(Locale.US)) {
                "true", "1", "yes" -> true
                "false", "0", "no" -> false
                else -> null
            }
            else -> null
        }

        fun parseObject(text: String): JSONObject? =
            runCatching { JSONObject(text.trim()) }.getOrNull()?.takeIf { it.length() > 0 }

        /** Unwraps the `data`/`result` field; returns the whole object when there is none. */
        fun unwrap(json: JSONObject): Any? {
            val lower = json.keys().asSequence().associateBy { it.lowercase() }
            val dataKey = lower["data"] ?: lower["result"] ?: return json
            return json.opt(dataKey)
        }

        /**
         * Extracts a token from a success envelope only. Anything that looks like an error message
         * (`Internal server error.`, `… disabled`, JSON punctuation) is rejected — storing such a
         * body as the token was the reason every following request failed on build 25.
         */
        fun extractToken(body: String): String? {
            val trimmed = body.trim()
            if (trimmed.isEmpty()) return null
            if (!trimmed.startsWith("{") && !trimmed.startsWith("[")) {
                return trimmed.takeIf { it.length in 8..512 && !it.contains(' ') }
            }
            val json = parseObject(trimmed) ?: return null
            if (!envelopeOk(json)) return null
            val data = json.opt("data") ?: json.opt("token") ?: return null
            val candidate = when (data) {
                is String -> data
                is JSONObject -> data.optString("token", data.optString("access_token"))
                else -> null
            }?.trim().orEmpty()
            if (candidate.isEmpty() || candidate.length < 8) return null
            if (candidate.contains(' ') || candidate.endsWith(".")) return null
            return candidate
        }
    }
}

/** Signing-certificate fingerprints used by the `sign` / `sha_hexadecimal` headers. */
object Signing {

    data class Info(val der: ByteArray) {
        /** `Base64(MD5(DER))` — `VolleyHelper.getSign("MD5")`. */
        val signBase64: String
            get() = Base64.encodeToString(MessageDigest.getInstance("MD5").digest(der), Base64.NO_WRAP)

        /** `hex(SHA-256(SHA-256(DER)))` — `Ld0/h.w(Signature)`. */
        val shaHex: String
            get() {
                val doubled = MessageDigest.getInstance("SHA-256")
                    .digest(MessageDigest.getInstance("SHA-256").digest(der))
                return doubled.joinToString("") { String.format(Locale.US, "%02x", it.toInt() and 0xFF) }
            }
    }

    fun info(packageName: String, context: Context): Info? = runCatching {
        val pm = context.packageManager
        val signature = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            val pkg = pm.getPackageInfo(packageName, PackageManager.GET_SIGNING_CERTIFICATES)
            val signingInfo = pkg.signingInfo ?: return null
            (signingInfo.apkContentsSigners ?: signingInfo.signingCertificateHistory)?.firstOrNull()
        } else {
            @Suppress("DEPRECATION")
            pm.getPackageInfo(packageName, PackageManager.GET_SIGNATURES).signatures?.firstOrNull()
        } ?: return null
        Info(signature.toByteArray())
    }.onFailure { AppLog.e("محاسبهٔ هدر امضا ناموفق", it) }.getOrNull()
}
