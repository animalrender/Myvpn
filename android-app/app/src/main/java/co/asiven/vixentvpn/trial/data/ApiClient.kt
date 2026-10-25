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
 * Client for the backend used by the analysed APK.
 *
 * Endpoints (identical to the original):
 *   GET/POST  {api}/api/token      — device token
 *   GET       {api}/api/setting    — app settings (test URL, remote api switch, …)
 *   GET       {api}/api/protocols  — the full server list (free **and** paid)
 *
 * Headers (identical to the original `VolleyHelper`):
 *   Content-Type: application/json
 *   app_name: <package>
 *   version_code: <versionCode>
 *   admobSeen: false            (kept for wire compatibility; the trial build has no ads)
 *   token: <token>
 *   sha_hexadecimal: <package>,<sha256 of signing certificate>
 *   sign: Base64(sha256(signing certificate bytes))
 *   Authorization: bearer <token>   (only once a token is known)
 *
 * NOTE: no Firebase header is sent — the trial build has no Firebase at all. The token
 * request is retried with GET/POST and with both hex cases so a stricter backend does not
 * lock the client out on a technicality.
 */
class ApiClient(private val context: Context, private val prefs: Prefs) {

    data class Result(val code: Int, val body: String, val url: String) {
        val ok: Boolean get() = code in 200..299 && body.isNotBlank()
    }

    private val signing: Signing.Info? by lazy { Signing.info(context.packageName, context) }

    val baseUrl: String get() = normalise(prefs.apiUrl.ifBlank { BuildConfig.API_BASE })

    // ---------------------------------------------------------------- public API

    fun fetchToken(): String? {
        val deviceId = prefs.deviceId
        val body = JSONObject().apply {
            put("deviceId", deviceId)
            put("device_id", deviceId)
            put("name", "${Build.MANUFACTURER} ${Build.MODEL}")
            put("firebase_token", "")
        }.toString()

        val attempts = listOf(
            Attempt("POST", "/api/token", body, hexUpper = false),
            Attempt("POST", "/api/token/", body, hexUpper = false),
            Attempt("GET", "/api/token?deviceId=$deviceId", null, hexUpper = false),
            Attempt("POST", "/api/token", body, hexUpper = true),
            Attempt("GET", "/api/token/?deviceId=$deviceId", null, hexUpper = true),
        )
        for (attempt in attempts) {
            val result = execute(attempt) ?: continue
            val token = extractToken(result.body)
            if (token != null) {
                prefs.token = token
                AppLog.i("token دریافت شد (${token.take(6)}…) از ${result.url}")
                return token
            }
            AppLog.w("پاسخ توکن قابل تجزیه نبود: ${result.code} ${result.body.take(200)}")
        }
        AppLog.e("دریافت توکن از همهٔ حالت‌ها شکست خورد")
        return null
    }

    fun fetchSetting(): AppSetting? {
        val attempts = listOf(
            Attempt("GET", "/api/setting", null, false),
            Attempt("GET", "/api/setting/", null, false),
            Attempt("POST", "/api/setting/", "{}", false),
            Attempt("GET", "/api/setting", null, true),
        )
        for (attempt in attempts) {
            val result = execute(attempt) ?: continue
            val json = parseObject(result.body) ?: continue
            prefs.settingsCache = json.toString()
            val setting = AppSetting.from(unwrap(json) as? JSONObject ?: json)
            AppLog.i("setting دریافت شد از ${result.url}")
            // Remote api switch — the original app persists `apiUrl` from the settings payload.
            setting.apiUrl?.takeIf { it.startsWith("http") }?.let {
                if (it != prefs.apiUrl) AppLog.i("apiUrl از راه دور به‌روزرسانی شد: $it")
                prefs.apiUrl = it.trimEnd('/')
            }
            setting.testUrl?.takeIf { it.startsWith("http") }?.let { prefs.testUrl = it }
            return setting
        }
        AppLog.e("دریافت setting شکست خورد")
        return null
    }

    fun fetchProtocols(): List<Server> {
        val attempts = listOf(
            Attempt("GET", "/api/protocols", null, false),
            Attempt("GET", "/api/protocols/", null, false),
            Attempt("POST", "/api/protocols/", "{}", false),
            Attempt("GET", "/api/protocols", null, true),
        )
        for (attempt in attempts) {
            val result = execute(attempt) ?: continue
            val json = parseObject(result.body) ?: continue
            val servers = ServerParser.parseList(json)
            if (servers.isEmpty()) {
                AppLog.w("پاسخ protocols شامل سروری نبود: ${result.body.take(200)}")
                continue
            }
            prefs.protocolsCache = result.body
            AppLog.i("${servers.size} سرور از ${result.url} دریافت شد")
            return servers
        }
        AppLog.e("دریافت فهرست سرورها شکست خورد")
        return emptyList()
    }

    // ---------------------------------------------------------------- HTTP layer

    private data class Attempt(val method: String, val path: String, val body: String?, val hexUpper: Boolean)

    private fun execute(attempt: Attempt): Result? {
        val url = baseUrl + attempt.path
        val requestHeaders = headers(attempt.hexUpper)
        var connection: HttpURLConnection? = null
        return try {
            connection = (URL(url).openConnection() as HttpURLConnection).apply {
                requestMethod = attempt.method
                connectTimeout = 20_000
                readTimeout = 25_000
                instanceFollowRedirects = true
                doInput = true
                requestHeaders.forEach { (k, v) -> setRequestProperty(k, v) }
                if (attempt.body != null) {
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json")
                }
            }
            if (attempt.body != null) {
                connection.outputStream.use { it.write(attempt.body.toByteArray(Charsets.UTF_8)) }
            }
            val code = connection.responseCode
            val stream = if (code in 200..299) connection.inputStream else connection.errorStream
            val text = stream?.bufferedReader()?.use(BufferedReader::readText).orEmpty()
            AppLog.d("${attempt.method} $url → $code (${text.length} بایت)")
            if (code !in 200..299) {
                AppLog.w("پاسخ غیرموفق $code: ${text.take(300)}")
            }
            Result(code, text, url)
        } catch (t: Throwable) {
            AppLog.e("${attempt.method} $url ناموفق", t)
            null
        } finally {
            connection?.disconnect()
        }
    }

    private fun headers(hexUpper: Boolean = false): Map<String, String> {
        val map = linkedMapOf(
            "Accept" to "application/json",
            "User-Agent" to "okhttp/3.12.13",
            "app_name" to BuildConfig.HEADER_APP_NAME,
            "version_code" to BuildConfig.HEADER_VERSION_CODE.toString(),
            "admobSeen" to "false",
        )
        val token = prefs.token
        if (token.isNotBlank()) {
            map["token"] = token
            map["Authorization"] = "bearer $token"
        }
        signing?.let {
            map["sha_hexadecimal"] = "${BuildConfig.HEADER_APP_NAME},${it.sha256Hex(hexUpper)}"
            map["sign"] = it.signBase64
        }
        return map
    }

    private fun normalise(url: String): String = url.trim().trimEnd('/').ifBlank { BuildConfig.API_BASE }

    companion object {

        fun parseObject(text: String): JSONObject? = runCatching { JSONObject(text.trim()) }.getOrNull()

        /**
         * Backend responses are wrapped (`{status, message, data}`); unwrap `data` when present.
         */
        fun unwrap(json: JSONObject): Any? {
            val lower = json.keys().asSequence().associateBy { it.lowercase() }
            val dataKey = lower["data"] ?: lower["result"] ?: return json
            return json.opt(dataKey)
        }

        /** Digs a token out of any of the possible response shapes. */
        fun extractToken(body: String): String? {
            val trimmed = body.trim()
            if (trimmed.startsWith("\"") && trimmed.endsWith("\"")) {
                return trimmed.trim('"').takeIf { it.isNotBlank() }
            }
            val json = parseObject(trimmed) ?: return null
            // {token: "..."}
            json.optString("token").takeIf { it.isNotBlank() && it != "null" }?.let { return it }
            // {data: "..."} / {result: "..."}
            when (val data = unwrap(json)) {
                is String -> if (data.isNotBlank() && data != "null") return data
                is JSONObject -> data.optString("token").takeIf { it.isNotBlank() && it != "null" }
                    ?.let { return it }
                else -> {}
            }
            fun find(node: Any?): String? = when (node) {
                is JSONObject -> {
                    node.keys().asSequence()
                        .map { it to node.opt(it) }
                        .firstOrNull { it.first.equals("token", true) && it.second is String }
                        ?.second as? String
                        ?: node.keys().asSequence().map { find(node.opt(it)) }.firstOrNull { it != null }
                }
                is org.json.JSONArray -> (0 until node.length()).map { find(node.opt(it)) }.firstOrNull { it != null }
                else -> null
            }
            return find(json)?.takeIf { it.isNotBlank() }
        }
    }
}

/**
 * Reproduces the original `sign` / `sha_hexadecimal` headers: SHA-256 over the APK signing
 * certificate, hex for one header and Base64 for the other.
 * (`PackageManager` `GET_SIGNING_CERTIFICATES` on Android 9+, `GET_SIGNATURES` below.)
 */
object Signing {

    data class Info(val sha256: ByteArray) {
        fun sha256Hex(upper: Boolean = false): String {
            val hex = sha256.joinToString("") { String.format(Locale.US, "%02x", it.toInt() and 0xFF) }
            return if (upper) hex.uppercase(Locale.US) else hex
        }

        val signBase64: String
            get() = Base64.encodeToString(sha256, Base64.NO_WRAP)
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
        val digest = MessageDigest.getInstance("SHA-256").digest(signature.toByteArray())
        Info(digest)
    }.onFailure { AppLog.e("محاسبهٔ هدر امضا ناموفق", it) }.getOrNull()
}
