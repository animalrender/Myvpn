package co.asiven.vixentvpn.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.net.VpnService
import android.os.Build
import android.os.ParcelFileDescriptor
import co.asiven.vixentvpn.trial.BuildConfig
import co.asiven.vixentvpn.trial.R
import co.asiven.vixentvpn.trial.core.ConfigBuilder
import co.asiven.vixentvpn.trial.core.XrayCore
import co.asiven.vixentvpn.trial.data.Prefs
import co.asiven.vixentvpn.trial.data.Server
import co.asiven.vixentvpn.trial.data.ServerParser
import co.asiven.vixentvpn.trial.ui.MainActivity
import co.asiven.vixentvpn.trial.util.AppLog
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.launch
import org.json.JSONObject

/**
 * Owns the whole tunnel, mirroring the analysed APK's `V2RayVpnService`:
 *
 *   VpnService.Builder → TUN fd
 *        ├── Xray core (libv2ray, SOCKS 10808 + HTTP 10809 inbounds)
 *        └── hev-socks5-tunnel (TUN ⇄ 127.0.0.1:10808), started with the same fd
 *
 * `pref_mode` selects the behaviour:
 *   VPN   — everything on the device goes through the tunnel (default)
 *   PROXY — no TUN at all, only the local SOCKS/HTTP endpoints (v2rayNG's proxy-only mode)
 */
class VpnTunnelService : VpnService() {

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var tunInterface: ParcelFileDescriptor? = null
    private var tProxy: HevTunnel? = null
    private var prefs: Prefs? = null
    private var activeKey: String = ""

    override fun onCreate() {
        super.onCreate()
        AppLog.attach(applicationContext)
        prefs = Prefs(applicationContext)
        createChannel()
        AppLog.i("VpnTunnelService ایجاد شد")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == ACTION_STOP) {
            stopTunnel(getString(R.string.status_disconnected))
            return START_NOT_STICKY
        }

        val rawConfig = intent?.getStringExtra(EXTRA_SERVER).orEmpty()
        val displayName = intent?.getStringExtra(EXTRA_NAME).orEmpty()
        val mode = intent?.getStringExtra(EXTRA_MODE) ?: prefs?.mode ?: Prefs.MODE_VPN
        startForeground(NOTIF_ID, buildNotification(getString(R.string.status_connecting)))

        // The config travels as the raw share link / JSON config itself: `Server.rawJson` is the
        // same text for imported rows but NOT for rows parsed from `/api/protocols`, and sending
        // the wrong one made the service start without a server at all.
        val server = parseServer(rawConfig, displayName)
        val announcedKey = intent?.getStringExtra(EXTRA_KEY).orEmpty()
        activeKey = announcedKey.ifBlank { server?.key.orEmpty() }
        if (server == null) {
            AppLog.e("سروری برای اتصال ارسال نشده است")
            publish(false, getString(R.string.status_error, "سروری انتخاب نشده"))
            stopTunnel(getString(R.string.status_error, "سروری انتخاب نشده"))
            return START_NOT_STICKY
        }

        scope.launch { connect(server, mode) }
        return START_STICKY
    }

    // ------------------------------------------------------------------ connect

    private fun connect(server: Server, mode: String) {
        try {
            publish(false, getString(R.string.status_connecting))

            val parsed = ConfigBuilder.parse(server)
            val outbound = parsed.outbound
            if (outbound == null) {
                val message = parsed.error ?: "پیکربندی سرور قابل خواندن نیست"
                AppLog.e("تجزیهٔ پیکربندی ناموفق: $message")
                fail(message)
                return
            }

            val config = ConfigBuilder.runtimeConfig(outbound)
            AppLog.i("پیکربندی هسته آماده شد (${parsed.kind}) برای ${server.name}")

            val useTun = mode != Prefs.MODE_PROXY
            var fd = 0
            if (useTun) {
                val descriptor = establishTun() ?: run {
                    fail("ساخت رابط VPN ناموفق بود")
                    return
                }
                tunInterface = descriptor
                fd = descriptor.fd
            }

            if (!XrayCore.start(config, fd)) {
                fail("هستهٔ Xray شروع نشد")
                return
            }

            if (useTun) {
                val tunnel = HevTunnel(applicationContext, fd)
                tProxy = tunnel
                if (!tunnel.start()) {
                    fail("hev-socks5-tunnel شروع نشد")
                    return
                }
            }

            val text = if (useTun) {
                getString(R.string.status_connected, server.name, "VPN")
            } else {
                getString(R.string.status_connected, server.name, "PROXY ${ConfigBuilder.SOCKS_PORT}/${ConfigBuilder.HTTP_PORT}")
            }
            updateNotification(text)
            prefs?.connectedKey = activeKey
            publish(true, text)
            AppLog.i("اتصال برقرار شد: $text")
        } catch (t: Throwable) {
            AppLog.e("خطا در اتصال", t)
            fail(t.message ?: t.javaClass.simpleName)
        }
    }

    private fun establishTun(): ParcelFileDescriptor? = try {
        val builder = Builder()
            .setSession(BuildConfig.HEADER_APP_NAME)
            .setMtu(TUN_MTU)
            .addAddress(TUN_ADDRESS, 24)
            .addRoute("0.0.0.0", 0)
            .addDnsServer("1.1.1.1")
            .addDnsServer("8.8.8.8")
        // Our own sockets (the Xray core → server) must never enter the tunnel.
        runCatching { builder.addDisallowedApplication(packageName) }
            .onFailure { AppLog.w("addDisallowedApplication ناموفق: ${it.message}") }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            builder.setMetered(false)
        }
        builder.establish().also { AppLog.i("رابط TUN ساخته شد: ${it?.fd}") }
    } catch (t: Throwable) {
        AppLog.e("ساخت رابط TUN ناموفق", t)
        null
    }

    private fun fail(message: String) {
        val text = getString(R.string.status_error, message)
        publish(false, text)
        updateNotification(text)
        stopTunnel(text)
    }

    // ------------------------------------------------------------------ teardown

    private fun stopTunnel(statusText: String) {
        try {
            tProxy?.stop()
            tProxy = null
            XrayCore.stop()
            tunInterface?.close()
            tunInterface = null
        } catch (t: Throwable) {
            AppLog.e("خطا در بستن تونل", t)
        }
        publish(false, statusText)
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    override fun onRevoke() {
        AppLog.w("دسترسی VPN لغو شد")
        stopTunnel(getString(R.string.status_disconnected))
        super.onRevoke()
    }

    override fun onDestroy() {
        scope.cancel()
        try {
            tProxy?.stop()
            XrayCore.stop()
            tunInterface?.close()
        } catch (_: Throwable) {
        }
        tProxy = null
        tunInterface = null
        publish(false, getString(R.string.status_disconnected))
        super.onDestroy()
    }

    // ------------------------------------------------------------------ state / notification

    private fun publish(running: Boolean, text: String) {
        // Mirrored into the prefs as well: broadcast is only received by activities that are
        // currently started, and the tunnel outlives them.
        prefs?.tunnelRunning = running
        if (!running) prefs?.connectedKey = ""
        val intent = Intent(ACTION_STATE).setPackage(packageName)
            .putExtra(EXTRA_RUNNING, running)
            .putExtra(EXTRA_TEXT, text)
        sendBroadcast(intent)
    }

    private fun createChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = getSystemService(NotificationManager::class.java)
            val channel = NotificationChannel(
                CHANNEL_ID,
                getString(R.string.notif_channel),
                NotificationManager.IMPORTANCE_LOW,
            )
            manager.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(text: String): Notification {
        val contentIntent = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE,
        )
        val builder = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            Notification.Builder(this, CHANNEL_ID)
        } else {
            @Suppress("DEPRECATION")
            Notification.Builder(this)
        }
        return builder
            .setContentTitle(getString(R.string.notif_title))
            .setContentText(text)
            .setSmallIcon(R.drawable.ic_stat_tunnel)
            .setContentIntent(contentIntent)
            .setOngoing(true)
            .build()
    }

    private fun updateNotification(text: String) {
        runCatching {
            val manager = getSystemService(NotificationManager::class.java)
            manager.notify(NOTIF_ID, buildNotification(text))
        }
    }

    private fun parseServer(rawConfig: String, displayName: String): Server? {
        if (rawConfig.isBlank()) return null
        return runCatching {
            val trimmed = rawConfig.trim()
            val parsed = if (trimmed.startsWith("{")) {
                ServerParser.fromJson(JSONObject(trimmed), 0).takeIf { it.rawConfig.isNotBlank() }
                    ?: ServerParser.fromRaw(trimmed, 0)
            } else {
                ServerParser.fromRaw(trimmed, 0)
            }
            if (displayName.isBlank()) parsed else parsed.copy(name = displayName)
        }.getOrNull()
    }

    companion object {
        const val ACTION_START = "co.asiven.vixentvpn.trial.START"
        const val ACTION_STOP = "co.asiven.vixentvpn.trial.STOP"
        const val ACTION_STATE = "co.asiven.vixentvpn.trial.STATE"
        const val EXTRA_SERVER = "server_config"
        const val EXTRA_NAME = "server_name"
        const val EXTRA_MODE = "mode"

        /**
         * Identity of the row as the **list** knows it. The service re-parses the config into its
         * own `Server` (whose key is content-derived), so without this the activity could never
         * recognise the row it is connected to and「قطع اتصال」kept behaving like「تغییر سرور」.
         */
        const val EXTRA_KEY = "server_key"
        const val EXTRA_RUNNING = "running"
        const val EXTRA_TEXT = "text"

        private const val CHANNEL_ID = "mvpn_tunnel"
        private const val NOTIF_ID = 1101
        private const val TUN_MTU = 1500
        private const val TUN_ADDRESS = "10.10.10.2"

        fun start(context: Context, server: Server, mode: String) {
            val intent = Intent(context, VpnTunnelService::class.java)
                .setAction(ACTION_START)
                .putExtra(EXTRA_SERVER, server.rawConfig.ifBlank { server.rawJson })
                .putExtra(EXTRA_NAME, server.name)
                .putExtra(EXTRA_KEY, server.key)
                .putExtra(EXTRA_MODE, mode)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }

        fun stop(context: Context) {
            context.startService(Intent(context, VpnTunnelService::class.java).setAction(ACTION_STOP))
        }
    }
}
