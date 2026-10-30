package mx.globalhealth.paciente.core.session

import android.content.Context
import com.google.crypto.tink.Aead
import com.google.crypto.tink.KeyTemplates
import com.google.crypto.tink.RegistryConfiguration
import com.google.crypto.tink.aead.AeadConfig
import com.google.crypto.tink.integration.android.AndroidKeysetManager

/**
 * The production AEAD for [SessionStore] (design.md, Decision 2): a Tink AES256-GCM keyset kept in its own
 * SharedPreferences file, itself encrypted by a master key that never leaves the Android Keystore. Robolectric has no
 * Keystore, so tests build their own AEAD; this one is checked by hand on the emulator.
 */
object KeystoreAead {
    private const val KEYSET_NAME = "session_keyset"
    private const val KEYSET_PREFS = "mx.globalhealth.paciente.session_keyset"
    private const val MASTER_KEY_URI = "android-keystore://mx.globalhealth.paciente.session_master_key"

    fun create(context: Context): Aead {
        AeadConfig.register()
        return AndroidKeysetManager.Builder()
            .withSharedPref(context.applicationContext, KEYSET_NAME, KEYSET_PREFS)
            .withKeyTemplate(KeyTemplates.get("AES256_GCM"))
            .withMasterKeyUri(MASTER_KEY_URI)
            .build()
            .keysetHandle
            .getPrimitive(RegistryConfiguration.get(), Aead::class.java)
    }
}
