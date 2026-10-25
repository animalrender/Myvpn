import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.gms.google-services")
}

// Signing material is injected by CI (see tools/fetch-testkey.sh); no key lives in the repo.
val keystorePropsFile = rootProject.file("signing/keystore.properties")
val keystoreProps = Properties().apply {
    if (keystorePropsFile.exists()) keystorePropsFile.inputStream().use { load(it) }
}
fun signingValue(env: String, key: String, fallback: String = ""): String =
    (System.getenv(env) ?: keystoreProps.getProperty(key) ?: fallback)

android {
    namespace = "co.asiven.vixentvpn.trial"
    compileSdk = 35

    defaultConfig {
        // Same identity as the analysed APK: the backend fingerprints app_name + APK signature.
        applicationId = "co.asiven.vixentvpn"
        minSdk = 24
        targetSdk = 35
        versionCode = 1004220
        versionName = "3.2.0-trial"

        ndk {
            abiFilters += listOf("arm64-v8a")
        }
        buildConfigField("String", "API_BASE", "\"https://managev1.xyz\"")
        buildConfigField("String", "TEST_URL", "\"https://www.gstatic.com/generate_204\"")
        // Header values reproducing the original client verbatim.
        buildConfigField("String", "HEADER_APP_NAME", "\"co.asiven.vixentvpn\"")
        buildConfigField("int", "HEADER_VERSION_CODE", "1004220")
    }

    signingConfigs {
        create("release") {
            // paths in signing/keystore.properties are relative to the android-app root
            val storePath = signingValue("MVPN_KEYSTORE", "storeFile")
            val candidate = if (storePath.isBlank()) null else rootProject.file(storePath)
            if (candidate != null && candidate.exists()) {
                storeFile = candidate
                storePassword = signingValue("MVPN_KEYSTORE_PASSWORD", "storePassword", "android")
                keyAlias = signingValue("MVPN_KEY_ALIAS", "keyAlias", "testkey")
                keyPassword = signingValue("MVPN_KEY_PASSWORD", "keyPassword", "android")
            }
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            isShrinkResources = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
            val cfg = signingConfigs.getByName("release")
            if (cfg.storeFile != null) signingConfig = cfg
        }
        debug {
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        buildConfig = true
        viewBinding = true
    }
    packaging {
        resources.excludes += setOf("META-INF/*.kotlin_module", "META-INF/DEPENDENCIES")
        jniLibs.useLegacyPackaging = false
    }
    lint {
        abortOnError = false
        checkReleaseBuilds = false
    }
}

dependencies {
    // Xray core (gomobile build of xtls/xray-core) — fetched by CI into app/libs.
    implementation(fileTree(mapOf("dir" to "libs", "include" to listOf("*.aar", "*.jar"))))
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("com.google.android.material:material:1.12.0")
    implementation("androidx.recyclerview:recyclerview:1.3.2")
    implementation("androidx.cardview:cardview:1.0.0")
    implementation("androidx.constraintlayout:constraintlayout:2.1.4")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.4")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
    // Firebase Messaging — the baseline app registers a push token and sends it with the
    // token request; same project/app id (see app/google-services.json).
    implementation("com.google.firebase:firebase-messaging:24.0.2")
}
