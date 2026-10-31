plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlin.serialization)
}

// Debug talks to the developer's Mac: 10.0.2.2 from the emulator; a phone over USB builds with
// -PapiBaseUrl=http://localhost:8000/api/v1/ after `adb reverse tcp:8000 tcp:8000` (design.md, Interface contract).
val debugApiBaseUrl = providers.gradleProperty("apiBaseUrl").getOrElse("http://10.0.2.2:8000/api/v1/")

android {
    namespace = "mx.globalhealth.paciente"
    compileSdk = 37

    defaultConfig {
        applicationId = "mx.globalhealth.paciente"
        minSdk = 29
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0"
    }

    buildTypes {
        debug {
            buildConfigField("String", "API_BASE_URL", "\"$debugApiBaseUrl\"")
        }
        release {
            // No backend online yet (D24): HTTPS placeholder until the first deployment.
            buildConfigField("String", "API_BASE_URL", "\"https://api.globalhealth.invalid/api/v1/\"")
            isMinifyEnabled = false
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    testOptions {
        unitTests {
            // Robolectric needs the merged resources to render Compose in JVM tests.
            isIncludeAndroidResources = true
        }
    }
}

dependencies {
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.activity.compose)
    implementation(libs.androidx.lifecycle.viewmodel.compose)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.navigation.compose)
    implementation(libs.androidx.datastore)
    implementation(libs.androidx.datastore.tink)
    implementation(libs.retrofit)
    implementation(libs.retrofit.kotlinx.serialization)
    implementation(libs.okhttp)
    implementation(libs.kotlinx.serialization.json)
    debugImplementation(libs.androidx.compose.ui.tooling)
    debugImplementation(libs.androidx.compose.ui.test.manifest)

    testImplementation(platform(libs.androidx.compose.bom))
    testImplementation(libs.junit)
    testImplementation(libs.robolectric)
    testImplementation(libs.androidx.compose.ui.test.junit4)
    testImplementation(libs.okhttp.mockwebserver)
    testImplementation(libs.kotlinx.coroutines.test)
}
