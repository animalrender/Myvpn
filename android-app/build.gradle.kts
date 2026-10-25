// MVPN Trial — trial client reproducing the API/core stack of the analysed APK.
// No ads, no accounts, no purchase gating.
plugins {
    id("com.android.application") version "8.7.3" apply false
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
    // Firebase (same project/app id as the analysed APK; values extracted from its resources)
    id("com.google.gms.google-services") version "4.4.2" apply false
}
