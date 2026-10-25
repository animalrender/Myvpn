package co.asiven.vixentvpn.trial.data

import org.json.JSONArray
import org.json.JSONObject

/** Ping state of a single row. */
enum class PingState { IDLE, RUNNING, OK, FAILED }

/**
 * One server as returned by `GET /api/protocols` (model `Protocol` in the analysed APK:
 * `{id, name, serverId, flag, value, price, usage}`), kept **completely unmodified**:
 * nothing is filtered out, nothing is gated, every original attribute is preserved so the
 * trial build can show exactly what the real client showed.
 */
data class Server(
    val key: String,
    val protocolId: Int?,
    val serverId: Int?,
    val name: String,
    val flag: String,
    val typeHint: String,
    val price: Int?,
    val rawConfig: String,
    val usage: Usage?,
    val extra: Map<String, String>,
    val rawJson: String,
) {
    @Volatile
    var pingMs: Long = -1L

    @Volatile
    var pingState: PingState = PingState.IDLE

    val isFree: Boolean get() = (price ?: 0) <= 0
    val hasConfig: Boolean get() = rawConfig.isNotBlank()
    val displayFlag: String get() = flag.ifBlank { "🌐" }
}

/** `co.dev.models.ProtocolUsage` — per-device accounting that the real app shows per row. */
data class Usage(
    val upload: Long? = null,
    val download: Long? = null,
    val total: Long? = null,
    val used: Long? = null,
    val expire: String? = null,
    val deviceId: String? = null,
    val raw: String? = null,
) {
    fun summary(): String {
        val parts = mutableListOf<String>()
        upload?.let { parts += "↑ " + human(it) }
        download?.let { parts += "↓ " + human(it) }
        used?.let { parts += "مصرف " + human(it) }
        total?.let { parts += "سهمیه " + human(it) }
        expire?.takeIf { it.isNotBlank() && it != "null" }?.let { parts += "انقضا $it" }
        deviceId?.takeIf { it.isNotBlank() }?.let { parts += "دستگاه ${it.take(8)}" }
        return parts.joinToString(" · ")
    }

    companion object {
        fun human(bytes: Long): String {
            if (bytes <= 0) return "0"
            val units = arrayOf("B", "KB", "MB", "GB", "TB")
            var value = bytes.toDouble()
            var i = 0
            while (value >= 1024 && i < units.size - 1) {
                value /= 1024
                i++
            }
            return if (i == 0) "$bytes B" else String.format(java.util.Locale.US, "%.1f %s", value, units[i])
        }
    }
}

/** `co.dev.models.Setting` — only the fields the trial client actually consumes. */
data class AppSetting(
    val raw: JSONObject,
    val testUrl: String?,
    val apiUrl: String?,
    val privacyUrl: String?,
    val connectionTimeLimit: Long?,
    val connectedUntil: Long?,
) {
    companion object {
        fun from(json: JSONObject): AppSetting {
            val flat = flatten(json)

            fun pick(vararg keys: String): String? {
                for (k in keys) {
                    val value = flat[Json.norm(k)]
                    if (value != null && value.isNotBlank() && value != "null") return value
                }
                return null
            }

            return AppSetting(
                raw = json,
                testUrl = pick("testUrl", "test_url", "delayTestUrl"),
                apiUrl = pick("apiUrl", "api_url", "api"),
                privacyUrl = pick("privacyUrl", "privacy_url"),
                connectionTimeLimit = pick("connectionTimeLimit", "connection_time_limit")?.toLongOrNull(),
                connectedUntil = pick("connectedUntil", "connected_until")?.toLongOrNull(),
            )
        }

        /** Case/underscore-insensitive flattening of nested objects. */
        fun flatten(json: JSONObject, prefix: String = ""): Map<String, String> {
            val out = mutableMapOf<String, String>()
            json.keys().forEach { key ->
                when (val value = json.opt(key)) {
                    is JSONObject -> out.putAll(flatten(value, prefix))
                    is JSONArray -> out[Json.norm(prefix + key)] = value.toString()
                    null -> {}
                    else -> out[Json.norm(prefix + key)] = value.toString()
                }
            }
            return out
        }
    }
}

object Json {
    fun norm(key: String): String = key.lowercase().replace("_", "").replace("-", "").replace(" ", "")
}

/** Top-level (so they are usable as extensions from any file in this package). */
internal fun Any?.scalarString(): String? = when (this) {
    null, JSONObject.NULL -> null
    is String -> this
    is Number, is Boolean -> toString()
    else -> null
}

internal fun JSONObject.scalarMap(): Map<String, Any?> {
    val map = mutableMapOf<String, Any?>()
    keys().forEach { key -> map[Json.norm(key)] = opt(key) }
    return map
}

object ServerParser {

    private val NAME_KEYS = listOf("name", "title", "remarks", "remark", "label", "alias", "servername", "ps")
    private val FLAG_KEYS = listOf("flag", "country", "countrycode", "cc", "location", "region", "emoji", "code", "nation")
    private val PRICE_KEYS = listOf("price", "coin", "coins", "cost", "amount", "diamond", "diamonds", "fee")
    private val CONFIG_KEYS = listOf(
        "value", "config", "content", "link", "url", "uri", "connection", "data",
        "serverconfig", "configstr", "configcontent", "outbound", "body",
    )
    private val ID_KEYS = listOf("id", "protocolid", "pid")
    private val SERVER_ID_KEYS = listOf("serverid", "sid", "server")
    private val TYPE_KEYS = listOf("type", "protocol", "protocoltype", "proto", "scheme", "kind")
    private val USAGE_KEYS = listOf("usage", "usages", "usageinfo", "protocolusage")
    private val IGNORED_IN_EXTRA = NAME_KEYS + CONFIG_KEYS + USAGE_KEYS

    /** Parses a `/api/protocols` payload: accepts `{data:[...]}`, `{data:{data:[...]}}` or a bare array. */
    fun parseList(response: JSONObject?): List<Server> {
        if (response == null) return emptyList()
        val array = findArray(response) ?: return emptyList()
        val servers = mutableListOf<Server>()
        for (i in 0 until array.length()) {
            val obj = array.optJSONObject(i) ?: continue
            servers += fromJson(obj, i)
        }
        return servers
    }

    private fun findArray(response: JSONObject): JSONArray? {
        response.optJSONArray("data")?.let { return it }
        response.optJSONArray("result")?.let { return it }
        response.optJSONArray("protocols")?.let { return it }
        val keys = response.keys()
        while (keys.hasNext()) {
            when (val value = response.opt(keys.next())) {
                is JSONArray -> return value
                is JSONObject -> findArray(value)?.let { return it }
                else -> {}
            }
        }
        return null
    }

    fun fromJson(obj: JSONObject, index: Int): Server {
        val flat = obj.scalarMap()

        fun pick(keys: List<String>): Any? {
            for (k in keys) {
                val value = flat[Json.norm(k)]
                if (value != null && value != JSONObject.NULL) return value
            }
            return null
        }

        val protocolId = pick(ID_KEYS).scalarString()?.toIntOrNull()
        val serverId = pick(SERVER_ID_KEYS).scalarString()?.toIntOrNull()

        var rawConfig = pick(CONFIG_KEYS).scalarString().orEmpty()
        if (rawConfig.isBlank()) {
            val keys = obj.keys()
            while (keys.hasNext()) {
                val nested = obj.optJSONObject(keys.next()) ?: continue
                if (nested.has("protocol")) {
                    rawConfig = nested.toString()
                    break
                }
            }
        }

        val name = pick(NAME_KEYS).scalarString()?.takeIf { it.isNotBlank() } ?: "سرور ${index + 1}"
        val flag = pick(FLAG_KEYS).scalarString().orEmpty()
        val price = pick(PRICE_KEYS).scalarString()?.let { parsePrice(it) }
        val typeHint = detectType(rawConfig, pick(TYPE_KEYS).scalarString())
        val usage = parseUsage(obj, flat)

        val extra = linkedMapOf<String, String>()
        val keys = obj.keys()
        while (keys.hasNext()) {
            val key = keys.next()
            if (IGNORED_IN_EXTRA.any { Json.norm(it) == Json.norm(key) }) continue
            val value = obj.opt(key).scalarString() ?: if (obj.opt(key) is JSONObject) "(آبجکت)" else null
            if (value != null && value.isNotBlank()) extra[key] = value
        }

        val key = "$protocolId-${serverId ?: 0}-${name.hashCode()}"

        return Server(
            key = key,
            protocolId = protocolId,
            serverId = serverId,
            name = name,
            flag = flag,
            typeHint = typeHint,
            price = price,
            rawConfig = rawConfig,
            usage = usage,
            extra = extra,
            rawJson = obj.toString(),
        )
    }

    private fun parsePrice(value: String): Int? {
        val clean = value.trim().replace(",", "")
        clean.toIntOrNull()?.let { return it }
        clean.toDoubleOrNull()?.let { return it.toInt() }
        return null
    }

    private fun detectType(rawConfig: String, declared: String?): String {
        val fromConfig = Regex("^([a-zA-Z0-9+.-]+)://").find(rawConfig.trim())?.groupValues?.get(1)
        if (!fromConfig.isNullOrBlank()) return fromConfig.lowercase()
        val trimmed = rawConfig.trim()
        if (trimmed.startsWith("{")) {
            runCatching { JSONObject(trimmed).optString("protocol") }
                .getOrNull()?.takeIf { it.isNotBlank() }?.let { return it.lowercase() }
        }
        return declared?.lowercase().orEmpty().ifBlank { "?" }
    }

    private fun parseUsage(obj: JSONObject, flat: Map<String, Any?>): Usage? {
        var usageObj: JSONObject? = null
        val keys = obj.keys()
        while (keys.hasNext()) {
            val key = keys.next()
            if (USAGE_KEYS.any { Json.norm(it) == Json.norm(key) }) {
                usageObj = obj.optJSONObject(key)
                if (usageObj != null) break
            }
        }
        val usageFlat: Map<String, Any?> = usageObj?.let { AppSetting.flatten(it) } ?: flat

        fun num(vararg names: String): Long? {
            for (name in names) {
                val raw = usageFlat[Json.norm(name)] ?: continue
                val text = raw.toString()
                text.toLongOrNull()?.let { return it }
                text.toDoubleOrNull()?.let { return it.toLong() }
            }
            return null
        }

        fun str(vararg names: String): String? {
            for (name in names) {
                val text = usageFlat[Json.norm(name)]?.toString() ?: continue
                if (text.isNotBlank() && text != "null") return text
            }
            return null
        }

        val upload = num("upload", "uploaded", "up", "uploadusage")
        val download = num("download", "downloaded", "down", "downloadusage")
        val total = num("total", "totalusage", "traffic", "limit", "quota")
        val used = num("used", "usage", "usagecount", "usedtraffic", "currentusage")
        val expire = str("expire", "expiretime", "expireat", "expiredate", "expiration")
        val deviceId = str("deviceid", "device", "uuid")

        if (usageObj == null && upload == null && download == null && total == null && used == null &&
            expire == null && deviceId == null
        ) {
            return null
        }
        return Usage(
            upload = upload,
            download = download,
            total = total,
            used = used,
            expire = expire,
            deviceId = deviceId,
            raw = usageObj?.toString(),
        )
    }
}
