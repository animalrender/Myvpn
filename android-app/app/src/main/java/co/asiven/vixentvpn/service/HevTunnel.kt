package co.asiven.vixentvpn.service

import android.content.Context
import co.asiven.vixentvpn.trial.util.AppLog
import java.io.File

/**
 * Writes the hev YAML config and drives [TProxyService].
 * Config keys/values mirror v2rayNG's `buildConfig()` (tunnel mtu/ipv4, socks5 port/udp, misc).
 */
class HevTunnel(
    private val context: Context,
    private val tunFd: Int,
    private val socksPort: Int = 10808,
    private val mtu: Int = 1500,
    private val ipv4Client: String = "10.10.10.2",
) {

    fun isLibraryAvailable(): Boolean = try {
        TProxyService.TProxyIsRunning()
        true
    } catch (t: Throwable) {
        AppLog.e("کتابخانهٔ hev-socks5-tunnel در دسترس نیست", t)
        false
    }

    fun start(): Boolean = try {
        val configFile = File(context.filesDir, "hev-socks5-tunnel.yaml")
        configFile.writeText(buildYaml())
        AppLog.i("hev: شروع (fd=$tunFd، socks=$socksPort، mtu=$mtu)")
        TProxyService.TProxyStartService(configFile.absolutePath, tunFd)
    } catch (t: Throwable) {
        AppLog.e("hev: شروع ناموفق", t)
        false
    }

    fun stop() {
        try {
            TProxyService.TProxyStopService()
            AppLog.i("hev: متوقف شد")
        } catch (t: Throwable) {
            AppLog.e("hev: توقف ناموفق", t)
        }
    }

    fun isRunning(): Boolean = try {
        TProxyService.TProxyIsRunning()
    } catch (t: Throwable) {
        false
    }

    fun stats(): LongArray? = try {
        TProxyService.TProxyGetStats()
    } catch (t: Throwable) {
        null
    }

    private fun buildYaml(): String = buildString {
        appendLine("tunnel:")
        appendLine("  mtu: $mtu")
        appendLine("  ipv4: '$ipv4Client'")
        appendLine("  icmp: 'off'")
        appendLine("socks5:")
        appendLine("  port: $socksPort")
        appendLine("  address: '127.0.0.1'")
        appendLine("  udp: 'udp'")
        appendLine("misc:")
        appendLine("  task-stack-size: 86016")
        appendLine("  connect-timeout: 10000")
        appendLine("  tcp-read-write-timeout: 300000")
        appendLine("  udp-read-write-timeout: 60000")
        appendLine("  log-level: warn")
    }
}
