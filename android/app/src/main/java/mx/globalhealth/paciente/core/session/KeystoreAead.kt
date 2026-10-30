package mx.globalhealth.paciente.core.session

import android.content.Context
import androidx.datastore.dataStoreFile
import com.google.crypto.tink.Aead
import com.google.crypto.tink.KeyTemplates
import com.google.crypto.tink.RegistryConfiguration
import com.google.crypto.tink.aead.AeadConfig
import com.google.crypto.tink.integration.android.AndroidKeysetManager
import java.io.IOException
import java.security.GeneralSecurityException
import java.security.ProviderException

/**
 * The production AEAD for [SessionStore] (design.md, Decision 2): a Tink AES256-GCM keyset kept in its own
 * SharedPreferences file, itself encrypted by a master key that never leaves the Android Keystore. Robolectric has no
 * Keystore, so tests build their own AEAD; this one is checked by hand on the emulator.
 */
object KeystoreAead {
    private const val KEYSET_NAME = "session_keyset"
    private const val KEYSET_PREFS = "mx.globalhealth.paciente.session_keyset"
    private const val MASTER_KEY_URI = "android-keystore://mx.globalhealth.paciente.session_master_key"

    /**
     * The AEAD, or null when the Keystore cannot be used: then the session lives in memory only (spec AB-6), since
     * Tink would otherwise keep the keyset in clear in the prefs without failing. A keyset that cannot be read (master
     * key lost or unusable, corrupt pref) is discarded with the session file it encrypted and a new one is made: the
     * patient signs in again instead of the app closing on every start.
     */
    fun create(context: Context): Aead? {
        AeadConfig.register()
        val app = context.applicationContext
        return try {
            build(app)
        } catch (e: GeneralSecurityException) {
            rebuild(app)
        } catch (e: IOException) { // CharConversionException (not hex), InvalidProtocolBufferException
            rebuild(app)
        } catch (e: ProviderException) {
            rebuild(app)
        }
    }

    private fun rebuild(app: Context): Aead? {
        discard(app)
        return runCatching { build(app) }.getOrElse {
            discard(app)
            null
        }
    }

    private fun build(app: Context): Aead? {
        val manager = AndroidKeysetManager.Builder()
            .withSharedPref(app, KEYSET_NAME, KEYSET_PREFS)
            .withKeyTemplate(KeyTemplates.get("AES256_GCM"))
            .withMasterKeyUri(MASTER_KEY_URI)
            .build()
        if (!manager.isUsingKeystore) {
            discard(app)
            return null
        }
        return manager.keysetHandle.getPrimitive(RegistryConfiguration.get(), Aead::class.java)
    }

    /** Deletes the keyset and the session file it encrypted (unreadable without it). */
    private fun discard(app: Context) {
        app.deleteSharedPreferences(KEYSET_PREFS)
        app.dataStoreFile(SessionStore.DEFAULT_FILE_NAME).delete()
    }
}
