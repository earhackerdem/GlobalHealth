package mx.globalhealth.paciente

import android.app.Application
import mx.globalhealth.paciente.core.session.KeystoreAead

/**
 * Holds the one [AppContainer] of the process. Building it in [MainActivity] would create a second DataStore over the
 * session file on every rotation, which DataStore rejects. Lazy, so JVM tests (which build their own container with
 * a test AEAD) never touch the Android Keystore.
 */
class GlobalHealthApplication : Application() {
    val container: AppContainer by lazy {
        AppContainer(this, BuildConfig.API_BASE_URL, KeystoreAead.create(this))
    }
}
