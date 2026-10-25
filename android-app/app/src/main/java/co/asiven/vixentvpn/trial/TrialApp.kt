package co.asiven.vixentvpn.trial

import android.app.Application
import co.asiven.vixentvpn.trial.core.XrayCore
import co.asiven.vixentvpn.trial.push.TrialMessagingService
import co.asiven.vixentvpn.trial.util.AppLog

/** Application entry point: initialises logging and the Xray core environment once. */
class TrialApp : Application() {
    override fun onCreate() {
        super.onCreate()
        AppLog.attach(this)
        AppLog.i("MVPN Trial ${BuildConfig.VERSION_NAME} (${BuildConfig.APPLICATION_ID}) راه‌اندازی شد")
        XrayCore.init(this)
        TrialMessagingService.refresh(this)
    }
}
