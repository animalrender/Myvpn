package co.asiven.vixentvpn.trial.push

import android.content.Context
import co.asiven.vixentvpn.trial.data.Prefs
import co.asiven.vixentvpn.trial.util.AppLog
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

/**
 * Firebase Messaging, mirroring the baseline app: the registration token is kept in the local
 * store as `firebase_token` and is sent along with the `/api/token` request.
 *
 * The original client also used push messages for update/announcement notifications; here they are
 * only logged (no ads, no forced update flow).
 */
class TrialMessagingService : FirebaseMessagingService() {

    override fun onNewToken(token: String) {
        store(this, token)
    }

    override fun onMessageReceived(message: RemoteMessage) {
        val title = message.notification?.title ?: message.data["title"].orEmpty()
        val body = message.notification?.body ?: message.data["body"].orEmpty()
        AppLog.i("پیام Firebase دریافت شد: $title — $body")
    }

    companion object {
        /** Asks FCM for the current token; safe to call on every start (Firebase caches it). */
        fun refresh(context: Context) {
            runCatching {
                FirebaseMessaging.getInstance().token.addOnSuccessListener { token ->
                    store(context, token)
                }.addOnFailureListener { error ->
                    AppLog.w("دریافت توکن Firebase ناموفق: ${error.message}")
                }
            }.onFailure { AppLog.w("Firebase در دسترس نیست: ${it.message}") }
        }

        private fun store(context: Context, token: String) {
            if (token.isBlank()) return
            Prefs(context.applicationContext).firebaseToken = token
            AppLog.i("توکن Firebase ذخیره شد (${token.take(12)}…، ${token.length} کاراکتر)")
        }
    }
}
