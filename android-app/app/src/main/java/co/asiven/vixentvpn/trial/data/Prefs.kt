package co.asiven.vixentvpn.trial.data

import android.content.Context
import android.provider.Settings

/**
 * Plain SharedPreferences store — intentional replacement for the original MMKV layer
 * (no MMKV/Firebase native code in the trial build). Key names follow the original app
 * so the semantics stay recognisable: token, deviceId, apiUrl, testUrl, pref_mode.
 */
class Prefs(context: Context) {

    private val sp = context.getSharedPreferences("mvpn_trial", Context.MODE_PRIVATE)
    private val androidId: String by lazy {
        runCatching {
            Settings.Secure.getString(context.contentResolver, Settings.Secure.ANDROID_ID)
        }.getOrNull().orEmpty().ifBlank { "unknown-device" }
    }

    var token: String
        get() = sp.getString(KEY_TOKEN, "").orEmpty()
        set(value) = sp.edit().putString(KEY_TOKEN, value).apply()

    var apiUrl: String
        get() = sp.getString(KEY_API_URL, "").orEmpty()
        set(value) = sp.edit().putString(KEY_API_URL, value).apply()

    var testUrl: String
        get() = sp.getString(KEY_TEST_URL, "").orEmpty()
        set(value) = sp.edit().putString(KEY_TEST_URL, value).apply()

    /** `pref_mode` in the original APK: VPN (default) or PROXY. */
    var mode: String
        get() = sp.getString(KEY_MODE, MODE_VPN).orEmpty()
        set(value) = sp.edit().putString(KEY_MODE, value).apply()

    var protocolsCache: String
        get() = sp.getString(KEY_PROTOCOLS, "").orEmpty()
        set(value) = sp.edit().putString(KEY_PROTOCOLS, value).apply()

    var settingsCache: String
        get() = sp.getString(KEY_SETTINGS, "").orEmpty()
        set(value) = sp.edit().putString(KEY_SETTINGS, value).apply()

    var selectedKey: String
        get() = sp.getString(KEY_SELECTED, "").orEmpty()
        set(value) = sp.edit().putString(KEY_SELECTED, value).apply()

    /** Stable device identifier: the original client uses `Settings.Secure.ANDROID_ID`. */
    val deviceId: String get() = androidId

    companion object {
        const val MODE_VPN = "VPN"
        const val MODE_PROXY = "PROXY"
        private const val KEY_TOKEN = "token"
        private const val KEY_API_URL = "apiUrl"
        private const val KEY_TEST_URL = "testUrl"
        private const val KEY_MODE = "pref_mode"
        private const val KEY_PROTOCOLS = "protocolsCache"
        private const val KEY_SETTINGS = "settingCache"
        private const val KEY_SELECTED = "selectedServer"
    }
}
