// AGP 9 builds Kotlin in (no org.jetbrains.kotlin.android plugin); Compose and serialization keep their plugins.
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.compose) apply false
    alias(libs.plugins.kotlin.serialization) apply false
}
