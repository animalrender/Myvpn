package co.asiven.vixentvpn.trial.core

import android.content.Context
import android.provider.Settings
import android.util.Base64
import co.asiven.vixentvpn.trial.util.AppLog
import go.Seq
import libv2ray.CoreCallbackHandler
import libv2ray.CoreController
import libv2ray.Libv2ray

/**
 * Thin wrapper around `libv2ray.aar` (AndroidLibXrayLite — the same gomobile build of
 * `xtls/xray-core` that v2rayNG 2.x and the analysed APK ship as `libgojni.so`).
 *
 * Runtime contract used here:
 *   Libv2ray.initCoreEnv(assetPath, xudpBaseKey)
 *   Libv2ray.newCoreController(handler) -> controller.startLoop(config, tunFd) / stopLoop()
 *   Libv2ray.measureOutboundDelay(config, url) -> latency in ms (or -1)
 *   Libv2ray.checkVersionX()
 */
object XrayCore : CoreCallbackHandler {

    @Volatile private var controller: CoreController? = null
    @Volatile private var initialised = false
    @Volatile private var running = false

    /** Must be called once, before any other core call (Application.onCreate). */
    fun init(context: Context) {
        if (initialised) return
        synchronized(this) {
            if (initialised) return
            try {
                Seq.setContext(context.applicationContext)
                val assetPath = context.getDir("assets", Context.MODE_PRIVATE).absolutePath
                Libv2ray.initCoreEnv(assetPath, xudpBaseKey(context))
                initialised = true
                AppLog.i("هستهٔ Xray آماده شد: ${version()}")
            } catch (t: Throwable) {
                AppLog.e("راه‌اندازی اولیهٔ هستهٔ Xray ناموفق", t)
            }
        }
    }

    fun version(): String = runCatching { Libv2ray.checkVersionX() }.getOrDefault("نامشخص")

    val isRunning: Boolean get() = running && (controller?.isRunning ?: false)

    /** Starts the core with the given full config. [tunFd] = 0 when no TUN device is used. */
    @Synchronized
    fun start(config: String, tunFd: Int): Boolean {
        if (isRunning) {
            AppLog.w("هسته در حال اجراست؛ درخواست شروع نادیده گرفته شد")
            return true
        }
        return try {
            val ctrl = controller ?: Libv2ray.newCoreController(this).also { controller = it }
            ctrl.startLoop(config, tunFd)
            running = ctrl.isRunning
            AppLog.i("هستهٔ Xray شروع شد (tunFd=$tunFd، running=$running)")
            running
        } catch (t: Throwable) {
            running = false
            AppLog.e("شروع هستهٔ Xray ناموفق", t)
            false
        }
    }

    @Synchronized
    fun stop() {
        try {
            controller?.stopLoop()
        } catch (t: Throwable) {
            AppLog.e("توقف هستهٔ Xray با خطا مواجه شد", t)
        }
        running = false
    }

    /** Latency of one outbound, measured by the core itself (same call the original app pings with). */
    fun measureDelay(config: String, url: String): Long = try {
        Libv2ray.measureOutboundDelay(config, url)
    } catch (t: Throwable) {
        AppLog.e("سنجش تأخیر ناموفق", t)
        -1L
    }

    private fun xudpBaseKey(context: Context): String = try {
        val androidId = Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
            .orEmpty().toByteArray(Charsets.UTF_8)
        Base64.encodeToString(androidId.copyOf(32), Base64.NO_PADDING or Base64.URL_SAFE)
    } catch (t: Throwable) {
        AppLog.w("تولید کلید XUDP ناموفق: ${t.message}")
        ""
    }

    // ------------------------------------------------------- CoreCallbackHandler

    override fun startup(): Long {
        running = true
        AppLog.i("CoreCallback: startup")
        return 0
    }

    override fun shutdown(): Long {
        running = false
        AppLog.i("CoreCallback: shutdown")
        return 0
    }

    override fun onEmitStatus(l: Long, s: String?): Long {
        AppLog.d("CoreCallback: $l ${s.orEmpty()}")
        return 0
    }
}
