package co.asiven.vixentvpn.trial.core

import android.util.Base64
import android.util.Log
import co.asiven.vixentvpn.trial.data.Server
import org.json.JSONArray
import org.json.JSONObject
import java.net.URLDecoder

/**
 * Turns a backend `Protocol.value` (a share link such as `vmess://…`, `vless://…`,
 * `trojan://…`, `ss://…` or a ready-made Xray outbound) into an Xray-core outbound object,
 * and wraps it into full runtime / delay-test configurations.
 *
 * The JSON shapes are the ones the original client (v2rayNG based, `AngConfigManager`
 * import path) produces, so the same core can run the same servers.
 */
object ConfigBuilder {

    const val SOCKS_PORT = 10808
    const val HTTP_PORT = 10809
    const val PROXY_TAG = "proxy"

    data class Parsed(val outbound: JSONObject?, val kind: String, val error: String? = null)

    // ------------------------------------------------------------------ public

    /**
     * Outbound protocols this core can actually dial. Everything else (`hysteria`, `tuic`, …) can
     * appear in a decrypted payload but would only make the tunnel fail, so those rows say so
     * instead of pretending to connect.
     */
    private val SUPPORTED = setOf(
        "vmess", "vless", "trojan", "shadowsocks", "ss", "socks", "socks5", "http", "freedom",
    )

    fun parse(server: Server): Parsed {
        val raw = server.rawConfig.trim()
        if (raw.isEmpty()) return Parsed(null, server.typeHint, "سرور هیچ مقدار اتصالی ندارد")
        val parsed = if (raw.startsWith("{")) {
            parseJson(raw)
        } else {
            val scheme = raw.substringBefore("://", "").lowercase()
            when (scheme) {
                "vmess" -> parseVmess(raw)
                "vless" -> parseVless(raw)
                "trojan" -> parseTrojan(raw)
                "ss" -> parseShadowsocks(raw)
                "socks", "socks5" -> parseSocks(raw)
                "http" -> parseHttpProxy(raw)
                else -> Parsed(null, scheme.ifBlank { server.typeHint }, "پروتکل پشتیبانی‌نشده: $scheme")
            }
        }
        if (parsed.outbound != null && parsed.kind.lowercase() !in SUPPORTED) {
            return Parsed(null, parsed.kind, "هستهٔ Xray پروتکل ${parsed.kind} را اجرا نمی‌کند")
        }
        parsed.outbound?.let { outbound ->
            coreRejection(outbound)?.let { reason -> return Parsed(null, parsed.kind, reason) }
        }
        return parsed
    }

    /**
     * xray-core (the version inside `libv2ray.aar`) refuses plaintext VLESS/VMess/Trojan to a
     * **public IP literal** ("vless without TLS or other encryption is prohibited"), which some
     * rows of this backend use. Such a row cannot be dialled by this core, so it is reported as
     * unusable instead of failing halfway through «اتصال».
     */
    private fun coreRejection(outbound: JSONObject): String? {
        val protocol = outbound.optString("protocol").lowercase()
        if (protocol !in setOf("vless", "vmess", "trojan")) return null
        val stream = outbound.optJSONObject("streamSettings")
        val security = stream?.optString("security").orEmpty().lowercase()
        if (security == "tls" || security == "reality" || security == "xtls") return null
        val settings = outbound.optJSONObject("settings")
        val address = settings?.optJSONArray("vnext")?.optJSONObject(0)?.optString("address")
            ?: settings?.optJSONArray("servers")?.optJSONObject(0)?.optString("address")
            ?: ""
        if (!isPublicIpLiteral(address)) return null
        return "هستهٔ Xray اتصال $protocol بدون TLS به IP عمومی ($address) را رد می‌کند؛ " +
            "این ردیف با این هسته قابل استفاده نیست"
    }

    private fun isPublicIpLiteral(host: String): Boolean {
        if (!Regex("^\\d{1,3}(\\.\\d{1,3}){3}$").matches(host)) return false
        val parts = host.split(".").map { it.toIntOrNull() ?: return false }
        val a = parts[0]
        val b = parts[1]
        val private = a == 0 || a == 10 || a == 127 ||
            (a == 192 && b == 168) || (a == 172 && b in 16..31) || (a == 169 && b == 254)
        return !private
    }

    /** Full runtime config: local SOCKS+HTTP inbounds, the server outbound, direct/block. */
    fun runtimeConfig(
        outbound: JSONObject,
        socksPort: Int = SOCKS_PORT,
        httpPort: Int = HTTP_PORT,
    ): String {
        val proxy = JSONObject(outbound.toString()).apply { put("tag", PROXY_TAG) }
        val inbounds = JSONArray()
            .put(
                JSONObject()
                    .put("tag", "socks-in")
                    .put("port", socksPort)
                    .put("listen", "127.0.0.1")
                    .put("protocol", "socks")
                    .put(
                        "settings",
                        JSONObject().put("auth", "noauth").put("udp", true).put("userLevel", 8),
                    )
                    .put(
                        "sniffing",
                        JSONObject().put("enabled", true).put("destOverride", JSONArray().put("http").put("tls")),
                    ),
            )
            .put(
                JSONObject()
                    .put("tag", "http-in")
                    .put("port", httpPort)
                    .put("listen", "127.0.0.1")
                    .put("protocol", "http")
                    .put("settings", JSONObject().put("userLevel", 8)),
            )

        val outbounds = JSONArray().put(proxy).put(
            JSONObject().put("tag", "direct").put("protocol", "freedom").put("settings", JSONObject()),
        ).put(
            JSONObject().put("tag", "block").put("protocol", "blackhole").put("settings", JSONObject()),
        )

        val rules = JSONArray().put(
            JSONObject()
                .put("type", "field")
                .put("outboundTag", "direct")
                .put(
                    "ip",
                    JSONArray()
                        .put("127.0.0.0/8").put("10.0.0.0/8").put("172.16.0.0/12")
                        .put("192.168.0.0/16").put("169.254.0.0/16").put("::1/128")
                        .put("fc00::/7").put("fe80::/10"),
                ),
        )

        return JSONObject()
            .put("log", JSONObject().put("loglevel", "warning"))
            .put("inbounds", inbounds)
            .put("outbounds", outbounds)
            .put(
                "routing",
                JSONObject().put("domainStrategy", "AsIs").put("rules", rules),
            )
            .put("dns", JSONObject().put("servers", JSONArray().put("1.1.1.1").put("8.8.8.8")))
            .toString(2)
    }

    /** Config used only for `Libv2ray.measureOutboundDelay` (single outbound, no inbounds). */
    fun pingConfig(outbound: JSONObject): String = JSONObject()
        .put("log", JSONObject().put("loglevel", "error"))
        .put("outbounds", JSONArray().put(JSONObject(outbound.toString()).apply { put("tag", PROXY_TAG) }))
        .toString()

    // ------------------------------------------------------------------ JSON passthrough

    private fun parseJson(raw: String): Parsed {
        val json = runCatching { JSONObject(raw) }.getOrNull()
            ?: return Parsed(null, "json", "JSON نامعتبر")
        json.optJSONArray("outbounds")?.let { array ->
            val first = array.optJSONObject(0) ?: return Parsed(null, "json", "outbounds خالی")
            return Parsed(first, first.optString("protocol", "json"))
        }
        if (json.has("protocol")) return Parsed(json, json.optString("protocol", "json"))
        // nested {server_config:{...}} or {config:{...}}
        for (key in json.keys()) {
            val nested = json.optJSONObject(key) ?: continue
            if (nested.has("protocol")) return Parsed(nested, nested.optString("protocol", "json"))
        }
        return Parsed(null, "json", "کلید protocol پیدا نشد")
    }

    // ------------------------------------------------------------------ vmess

    private fun parseVmess(raw: String): Parsed {
        val payload = raw.removePrefix("vmess://").trim()
        val json = decodeBase64(payload)?.let { runCatching { JSONObject(it) }.getOrNull() }
        if (json != null) return vmessFromJson(json)

        // Kitsunebi style: base64(security:uuid@host:port)?remarks=
        val decoded = decodeBase64(payload.substringBefore("#")) ?: return Parsed(null, "vmess", "base64 نامعتبر")
        val main = decoded.substringBefore("?")
        val remarks = raw.substringAfter("#", "")
        val at = main.substringAfterLast("@", "")
        if (at.isBlank()) return Parsed(null, "vmess", "قالب vmess ناشناخته")
        val security = main.substringBefore(":", "auto")
        val uuid = main.substringBeforeLast("@").substringAfterLast(":")
        val host = at.substringBeforeLast(":")
        val port = at.substringAfterLast(":").toIntOrNull() ?: return Parsed(null, "vmess", "پورت نامعتبر")
        val json2 = JSONObject()
            .put("v", "2").put("ps", remarks).put("add", host).put("port", port.toString())
            .put("id", uuid).put("aid", "0").put("scy", security).put("net", "tcp").put("tls", "")
        return vmessFromJson(json2)
    }

    private fun vmessFromJson(json: JSONObject): Parsed {
        val host = json.optString("add").ifBlank { return Parsed(null, "vmess", "آدرس خالی") }
        val port = json.optString("port").toIntOrNull() ?: return Parsed(null, "vmess", "پورت نامعتبر")
        val uuid = json.optString("id").ifBlank { return Parsed(null, "vmess", "uuid خالی") }
        val alterId = json.optString("aid", "0").toIntOrNull() ?: 0
        val security = json.optString("scy", json.optString("security", "auto")).ifBlank { "auto" }

        val stream = streamSettings(
            network = json.optString("net", "tcp"),
            headerType = json.optString("type", "none"),
            security = json.optString("tls", ""),
            sni = json.optString("sni", ""),
            alpn = json.optString("alpn", ""),
            fingerprint = json.optString("fp", ""),
            host = json.optString("host", ""),
            path = json.optString("path", ""),
            serviceName = json.optString("path", ""),
            publicKey = "",
            shortId = "",
            spiderX = "",
        )

        val outbound = JSONObject()
            .put("protocol", "vmess")
            .put(
                "settings",
                JSONObject().put(
                    "vnext",
                    JSONArray().put(
                        JSONObject()
                            .put("address", host)
                            .put("port", port)
                            .put(
                                "users",
                                JSONArray().put(
                                    JSONObject()
                                        .put("id", uuid)
                                        .put("alterId", alterId)
                                        .put("security", security)
                                        .put("level", 0),
                                ),
                            ),
                    ),
                ),
            )
            .put("streamSettings", stream)
        return Parsed(outbound, "vmess")
    }

    // ------------------------------------------------------------------ vless

    private fun parseVless(raw: String): Parsed {
        val body = raw.removePrefix("vless://")
        val (main, params, _) = splitUri(body)
        val uuid = main.substringBefore("@")
        val hostPort = main.substringAfter("@")
        if (uuid.isBlank() || hostPort.isBlank()) return Parsed(null, "vless", "قالب vless نامعتبر")
        val host = hostPort.substringBeforeLast(":")
        val port = hostPort.substringAfterLast(":").toIntOrNull()
            ?: return Parsed(null, "vless", "پورت نامعتبر")

        val security = params["security"] ?: params["tls"] ?: "none"
        val network = params["type"] ?: params["net"] ?: "tcp"
        val flow = params["flow"].orEmpty()

        val stream = streamSettings(
            network = network,
            headerType = params["headerType"] ?: "none",
            security = security,
            sni = params["sni"] ?: params["peer"] ?: params["servername"] ?: "",
            alpn = params["alpn"].orEmpty(),
            fingerprint = params["fp"] ?: params["fingerprint"] ?: "",
            host = params["host"].orEmpty(),
            path = params["path"].orEmpty(),
            serviceName = params["serviceName"] ?: params["path"].orEmpty(),
            publicKey = params["pbk"] ?: params["publicKey"] ?: "",
            shortId = params["sid"] ?: params["shortId"] ?: "",
            spiderX = params["spx"] ?: params["spiderX"] ?: "",
            insecure = (params["allowInsecure"] ?: params["insecure"]) == "1",
        )

        val user = JSONObject()
            .put("id", uuid)
            .put("encryption", params["encryption"] ?: "none")
            .put("flow", flow)
            .put("level", 0)

        val outbound = JSONObject()
            .put("protocol", "vless")
            .put(
                "settings",
                JSONObject().put(
                    "vnext",
                    JSONArray().put(
                        JSONObject().put("address", host).put("port", port).put("users", JSONArray().put(user)),
                    ),
                ),
            )
            .put("streamSettings", stream)
        return Parsed(outbound, "vless")
    }

    // ------------------------------------------------------------------ trojan

    private fun parseTrojan(raw: String): Parsed {
        val body = raw.removePrefix("trojan://")
        val (main, params, _) = splitUri(body)
        val password = main.substringBefore("@")
        val hostPort = main.substringAfter("@")
        if (password.isBlank() || hostPort.isBlank()) return Parsed(null, "trojan", "قالب trojan نامعتبر")
        val host = hostPort.substringBeforeLast(":")
        val port = hostPort.substringAfterLast(":").toIntOrNull()
            ?: return Parsed(null, "trojan", "پورت نامعتبر")

        val network = params["type"] ?: params["net"] ?: "tcp"
        val stream = streamSettings(
            network = network,
            headerType = params["headerType"] ?: "none",
            security = params["security"] ?: "tls",
            sni = params["sni"] ?: params["peer"] ?: params["servername"] ?: "",
            alpn = params["alpn"].orEmpty(),
            fingerprint = params["fp"] ?: "",
            host = params["host"].orEmpty(),
            path = params["path"].orEmpty(),
            serviceName = params["serviceName"] ?: params["path"].orEmpty(),
            publicKey = params["pbk"] ?: "",
            shortId = params["sid"] ?: "",
            spiderX = "",
            insecure = (params["allowInsecure"] ?: params["insecure"]) == "1",
        )

        val outbound = JSONObject()
            .put("protocol", "trojan")
            .put(
                "settings",
                JSONObject().put(
                    "servers",
                    JSONArray().put(
                        JSONObject()
                            .put("address", host).put("port", port)
                            .put("password", password).put("level", 0),
                    ),
                ),
            )
            .put("streamSettings", stream)
        return Parsed(outbound, "trojan")
    }

    // ------------------------------------------------------------------ shadowsocks

    private fun parseShadowsocks(raw: String): Parsed {
        var body = raw.removePrefix("ss://")
        body = body.substringBefore("#")

        var method = ""
        var password = ""
        var host: String
        var port: Int

        if (body.contains("@")) {
            val userInfo = body.substringBefore("@")
            val hostPort = body.substringAfter("@").substringBefore("?")
            val decodedUser = decodeBase64(userInfo)?.takeIf { it.contains(":") } ?: urlDecode(userInfo)
            method = decodedUser.substringBefore(":")
            password = decodedUser.substringAfter(":", "")
            host = hostPort.substringBeforeLast(":")
            port = hostPort.substringAfterLast(":").toIntOrNull() ?: return Parsed(null, "ss", "پورت نامعتبر")
        } else {
            val decoded = decodeBase64(body.substringBefore("?")) ?: return Parsed(null, "ss", "base64 نامعتبر")
            val at = decoded.substringAfterLast("@", "")
            if (at.isBlank()) return Parsed(null, "ss", "قالب ss نامعتبر")
            val userInfo = decoded.substringBeforeLast("@")
            method = userInfo.substringBefore(":")
            password = userInfo.substringAfter(":", "")
            host = at.substringBeforeLast(":")
            port = at.substringAfterLast(":").toIntOrNull() ?: return Parsed(null, "ss", "پورت نامعتبر")
        }

        val outbound = JSONObject()
            .put("protocol", "shadowsocks")
            .put(
                "settings",
                JSONObject().put(
                    "servers",
                    JSONArray().put(
                        JSONObject()
                            .put("address", host).put("port", port)
                            .put("method", method).put("password", password)
                            .put("level", 0),
                    ),
                ),
            )
        return Parsed(outbound, "ss")
    }

    // ------------------------------------------------------------------ socks / http

    private fun parseSocks(raw: String): Parsed {
        val body = raw.substringAfter("://")
        val main = body.substringBefore("?").substringBefore("#")
        val auth = main.substringBeforeLast("@", "")
        val hostPort = main.substringAfterLast("@")
        val host = hostPort.substringBeforeLast(":")
        val port = hostPort.substringAfterLast(":").toIntOrNull() ?: return Parsed(null, "socks", "پورت نامعتبر")
        val user = if (auth.isBlank()) "" else urlDecode(auth.substringBefore(":"))
        val pass = if (auth.isBlank()) "" else urlDecode(auth.substringAfter(":", ""))
        val servers = JSONArray().put(
            JSONObject()
                .put("address", host).put("port", port)
                .put("users", if (user.isBlank()) JSONArray() else JSONArray().put(
                    JSONObject().put("user", user).put("pass", pass).put("level", 0),
                )),
        )
        val outbound = JSONObject().put("protocol", "socks")
            .put("settings", JSONObject().put("servers", servers))
        return Parsed(outbound, "socks")
    }

    private fun parseHttpProxy(raw: String): Parsed {
        val body = raw.substringAfter("://")
        val main = body.substringBefore("?").substringBefore("#")
        val auth = main.substringBeforeLast("@", "")
        val hostPort = main.substringAfterLast("@")
        val host = hostPort.substringBeforeLast(":")
        val port = hostPort.substringAfterLast(":").toIntOrNull() ?: return Parsed(null, "http", "پورت نامعتبر")
        val user = if (auth.isBlank()) "" else urlDecode(auth.substringBefore(":"))
        val pass = if (auth.isBlank()) "" else urlDecode(auth.substringAfter(":", ""))
        val server = JSONObject().put("address", host).put("port", port)
        if (user.isNotBlank()) {
            server.put("users", JSONArray().put(JSONObject().put("user", user).put("pass", pass).put("level", 0)))
        }
        return Parsed(
            JSONObject().put("protocol", "http")
                .put("settings", JSONObject().put("servers", JSONArray().put(server))),
            "http",
        )
    }

    // ------------------------------------------------------------------ helpers

    private data class UriParts(val main: String, val params: Map<String, String>, val name: String)

    private fun splitUri(body: String): UriParts {
        val fragment = if (body.contains("#")) urlDecode(body.substringAfter("#")) else ""
        val withoutFragment = body.substringBefore("#")
        val main = withoutFragment.substringBefore("?")
        val query = withoutFragment.substringAfter("?", "")
        val params = mutableMapOf<String, String>()
        if (query.isNotBlank()) {
            query.split("&").forEach { pair ->
                val key = pair.substringBefore("=")
                val value = if (pair.contains("=")) urlDecode(pair.substringAfter("=")) else ""
                if (key.isNotBlank()) params[key] = value
            }
        }
        return UriParts(main, params, fragment)
    }

    private fun streamSettings(
        network: String,
        headerType: String,
        security: String,
        sni: String,
        alpn: String,
        fingerprint: String,
        host: String,
        path: String,
        serviceName: String,
        publicKey: String,
        shortId: String,
        spiderX: String,
        insecure: Boolean = false,
    ): JSONObject {
        val stream = JSONObject()
        val net = network.lowercase().ifBlank { "tcp" }
        stream.put("network", if (net == "h2" || net == "http") "h2" else net)

        when (net) {
            "ws", "websocket" -> stream.put(
                "wsSettings",
                JSONObject().put("path", path.ifBlank { "/" }).put(
                    "headers",
                    JSONObject().apply { if (host.isNotBlank()) put("Host", host) },
                ),
            )
            "grpc", "gun" -> stream.put(
                "grpcSettings",
                JSONObject().put("serviceName", serviceName.ifBlank { path.trimStart('/') }),
            )
            "h2", "http" -> stream.put(
                "httpSettings",
                JSONObject().put("path", path.ifBlank { "/" })
                    .put("host", JSONArray().apply { if (host.isNotBlank()) put(host) }),
            )
            "httpupgrade" -> stream.put(
                "httpupgradeSettings",
                JSONObject().put("path", path.ifBlank { "/" }).put("host", host),
            )
            "xhttp", "splithttp" -> stream.put(
                "xhttpSettings",
                JSONObject().put("path", path.ifBlank { "/" }).put("host", host).put("mode", "auto"),
            )
            "kcp", "mkcp" -> stream.put(
                "kcpSettings",
                JSONObject().put(
                    "header",
                    JSONObject().put("type", headerType.ifBlank { "none" }),
                ),
            )
            "tcp" -> if (headerType == "http") {
                stream.put(
                    "tcpSettings",
                    JSONObject().put(
                        "header",
                        JSONObject().put("type", "http").put(
                            "request",
                            JSONObject().put(
                                "path",
                                JSONArray().put(path.ifBlank { "/" }),
                            ).put(
                                "headers",
                                JSONObject().put("Host", JSONArray().apply { if (host.isNotBlank()) put(host) }),
                            ),
                        ),
                    ),
                )
            }
            else -> {}
        }

        val sec = security.lowercase()
        when {
            sec == "tls" || sec == "xtls" -> {
                stream.put("security", "tls")
                val tls = JSONObject()
                val serverName = sni.ifBlank { host }
                if (serverName.isNotBlank()) tls.put("serverName", serverName)
                if (alpn.isNotBlank()) {
                    tls.put("alpn", JSONArray().apply { alpn.split(",").forEach { put(it.trim()) } })
                }
                if (fingerprint.isNotBlank()) tls.put("fingerprint", fingerprint)
                if (insecure) tls.put("allowInsecure", true)
                stream.put("tlsSettings", tls)
            }
            sec == "reality" -> {
                stream.put("security", "reality")
                stream.put(
                    "realitySettings",
                    JSONObject()
                        .put("serverName", sni.ifBlank { host })
                        .put("fingerprint", fingerprint.ifBlank { "chrome" })
                        .put("publicKey", publicKey)
                        .put("shortId", shortId)
                        .put("spiderX", spiderX.ifBlank { "/" }),
                )
            }
            else -> stream.put("security", "none")
        }
        return stream
    }

    // ------------------------------------------------------------------ share links

    /**
     * Rebuilds a v2rayNG-compatible share URI (`vmess://`, `vless://`, `trojan://`, `ss://`) for
     * one server, so the row can be copied to the clipboard and imported into any v2ray client.
     *
     * When the backend already delivered a share URI it is returned verbatim; otherwise the URI is
     * reconstructed from the Xray outbound that [parse] produced (so JSON configs stay exportable).
     */
    fun shareLink(server: Server): String? {
        val raw = server.rawConfig.trim()
        if (raw.isEmpty()) return null
        if (!raw.startsWith("{")) return raw
        val outbound = parseJson(raw).outbound ?: return null
        return outboundToLink(outbound, server.name)
    }

    private fun outboundToLink(outbound: JSONObject, rawName: String): String? {
        val name = encodeName(rawName)
        val stream = outbound.optJSONObject("streamSettings")
        val network = stream?.optString("network").orEmpty().ifBlank { "tcp" }
        val security = stream?.optString("security").orEmpty().ifBlank { "none" }
        val tls = stream?.optJSONObject("tlsSettings")
        val reality = stream?.optJSONObject("realitySettings")
        val ws = stream?.optJSONObject("wsSettings")
        val grpc = stream?.optJSONObject("grpcSettings")
        val tcp = stream?.optJSONObject("tcpSettings")?.optJSONObject("header")
        val http = stream?.optJSONObject("httpSettings")

        val params = linkedMapOf<String, String>()
        if (network != "tcp") params["type"] = network
        if (security != "none") params["security"] = security
        (reality?.optString("serverName")?.ifBlank { null } ?: tls?.optString("serverName")?.ifBlank { null })
            ?.let { params["sni"] = it }
        tls?.optString("fingerprint")?.ifBlank { null }?.let { params["fp"] = it }
        reality?.optString("fingerprint")?.ifBlank { null }?.let { params["fp"] = it }
        reality?.optString("publicKey")?.ifBlank { null }?.let { params["pbk"] = it }
        reality?.optString("shortId")?.ifBlank { null }?.let { params["sid"] = it }
        reality?.optString("spiderX")?.ifBlank { null }?.let { params["spx"] = it }
        tls?.optJSONArray("alpn")?.let { array -> joinArray(array).takeIf { it.isNotBlank() }?.let { params["alpn"] = it } }
        ws?.optString("path")?.ifBlank { null }?.let { params["path"] = it }
        ws?.optJSONObject("headers")?.optString("Host")?.ifBlank { null }?.let { params["host"] = it }
        grpc?.optString("serviceName")?.ifBlank { null }?.let { params["serviceName"] = it }
        http?.optString("path")?.ifBlank { null }?.let { params["path"] = it }
        http?.optJSONArray("host")?.let { array -> joinArray(array).takeIf { it.isNotBlank() }?.let { params["host"] = it } }
        tcp?.optString("request")?.ifBlank { null }?.let { params["headerType"] = "http" }
        if (stream?.optBoolean("allowInsecure") == true) params["allowInsecure"] = "1"

        val settings = outbound.optJSONObject("settings") ?: return null
        return when (outbound.optString("protocol")) {
            "vmess" -> {
                val vnext = settings.optJSONArray("vnext")?.optJSONObject(0) ?: return null
                val user = vnext.optJSONArray("users")?.optJSONObject(0) ?: return null
                val json = JSONObject()
                    .put("v", "2")
                    .put("ps", rawName)
                    .put("add", vnext.optString("address"))
                    .put("port", vnext.optInt("port").toString())
                    .put("id", user.optString("id"))
                    .put("aid", user.optInt("alterId").toString())
                    .put("scy", user.optString("security", "auto"))
                    .put("net", network)
                    .put("type", params["headerType"] ?: "none")
                    .put("host", params["host"].orEmpty())
                    .put("path", params["path"].orEmpty())
                    .put("tls", if (security == "tls") "tls" else "")
                    .put("sni", params["sni"].orEmpty())
                    .put("alpn", params["alpn"].orEmpty())
                    .put("fp", params["fp"].orEmpty())
                "vmess://" + Base64.encodeToString(
                    json.toString().toByteArray(Charsets.UTF_8),
                    Base64.NO_WRAP or Base64.NO_PADDING,
                )
            }
            "vless" -> {
                val vnext = settings.optJSONArray("vnext")?.optJSONObject(0) ?: return null
                val user = vnext.optJSONArray("users")?.optJSONObject(0) ?: return null
                user.optString("flow").ifBlank { null }?.let { params["flow"] = it }
                user.optString("encryption").ifBlank { null }?.let { params["encryption"] = it }
                buildUri(
                    "vless",
                    "${user.optString("id")}@${vnext.optString("address")}:${vnext.optInt("port")}",
                    params,
                    name,
                )
            }
            "trojan" -> {
                val server = settings.optJSONArray("servers")?.optJSONObject(0) ?: return null
                buildUri(
                    "trojan",
                    "${server.optString("password")}@${server.optString("address")}:${server.optInt("port")}",
                    params,
                    name,
                )
            }
            "shadowsocks" -> {
                val server = settings.optJSONArray("servers")?.optJSONObject(0) ?: return null
                val user = "ss://" + Base64.encodeToString(
                    "${server.optString("method")}:${server.optString("password")}".toByteArray(Charsets.UTF_8),
                    Base64.NO_WRAP or Base64.NO_PADDING or Base64.URL_SAFE,
                )
                "$user@${server.optString("address")}:${server.optInt("port")}#$name"
            }
            else -> null
        }
    }

    private fun joinArray(array: JSONArray): String =
        (0 until array.length()).mapNotNull { array.optString(it).takeIf(String::isNotBlank) }.joinToString(",")

    private fun buildUri(scheme: String, authority: String, params: Map<String, String>, name: String): String {
        val query = params.entries
            .filter { it.value.isNotBlank() }
            .joinToString("&") { "${it.key}=${java.net.URLEncoder.encode(it.value, "UTF-8")}" }
        val suffix = if (query.isBlank()) "" else "?$query"
        return "$scheme://$authority$suffix#$name"
    }

    private fun encodeName(name: String): String =
        runCatching { java.net.URLEncoder.encode(name, "UTF-8") }.getOrDefault("mvpn")

    fun decodeBase64(value: String): String? {
        val cleaned = value.trim().replace("\n", "").replace(" ", "")
        val candidates = listOf(
            cleaned, cleaned.replace('-', '+').replace('_', '/'),
        )
        for (candidate in candidates) {
            for (flags in intArrayOf(Base64.NO_WRAP or Base64.URL_SAFE, Base64.NO_WRAP)) {
                try {
                    val padded = candidate + "=".repeat((4 - candidate.length % 4) % 4)
                    val decoded = Base64.decode(padded, flags)
                    if (decoded.isNotEmpty()) {
                        val text = String(decoded, Charsets.UTF_8)
                        if (text.all { it.code in 32..0x10FFFF }) return text
                    }
                } catch (t: Throwable) {
                    Log.d("MvpnTrial", "base64 decode failed: ${t.message}")
                }
            }
        }
        return null
    }

    private fun urlDecode(value: String): String = runCatching { URLDecoder.decode(value, "UTF-8") }.getOrDefault(value)
}
