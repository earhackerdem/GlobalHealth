package mx.globalhealth.paciente.core.session

import android.content.Context
import androidx.datastore.dataStoreFile
import com.google.crypto.tink.KeysetHandle
import com.google.crypto.tink.TinkProtoKeysetFormat
import com.google.crypto.tink.aead.AeadConfig
import com.google.crypto.tink.aead.PredefinedAeadParameters
import com.google.crypto.tink.subtle.Hex
import java.io.File
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import mx.globalhealth.paciente.AppContainer
import mx.globalhealth.paciente.testing.FakeApi.Companion.TOKEN
import mx.globalhealth.paciente.testing.TestAead
import mx.globalhealth.paciente.testing.appFiles
import mx.globalhealth.paciente.testing.containsSequence
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment

/**
 * The production AEAD where the Keystore fails (spec AB-5/AB-6, «Sesión guardada sin datos de salud en el teléfono»).
 * Robolectric has no Android Keystore, which is exactly the phone whose Keystore cannot be used: Tink 1.20 would
 * then keep the keyset in clear in the shared prefs without failing.
 */
@RunWith(RobolectricTestRunner::class)
class KeystoreAeadTest {

    private val context: Context = RuntimeEnvironment.getApplication()

    @Test
    fun ab6_sinKeystoreUsable_ningunKeysetQuedaEnDiscoYElTokenNoSeEscribe() {
        val container = AppContainer(context, BASE_URL, KeystoreAead.create(context))

        runBlocking<Unit> { container.sessionStore.save(TOKEN) }

        assertEquals("the session lasts while the app is open", TOKEN, runBlocking { container.sessionStore.token.first() })
        assertNoKeysetOnDisk()
        assertFalse("no session file", context.dataStoreFile(SESSION_FILE).exists())
        appFiles(context).forEach { file ->
            assertFalse("token in ${file.path}", file.readBytes().containsSequence(TOKEN.toByteArray()))
        }
    }

    @Test
    fun ab5_unKeysetIlegible_noCierraLaAppYDescartaLaSesionGuardada() {
        keysetPrefs().edit().putString(KEYSET_NAME, "esto no es hex").commit()
        writeOldSessionFile()

        // Built as the Application builds it: this used to throw on every start.
        val container = AppContainer(context, BASE_URL, KeystoreAead.create(context))

        assertFalse("the session it encrypted is discarded", context.dataStoreFile(SESSION_FILE).exists())
        assertNoKeysetOnDisk()
        assertSignInWorks(container)
    }

    @Test
    fun ab5_unKeysetCifradoSinSuLlaveMaestra_noCierraLaAppYDescartaLaSesionGuardada() {
        AeadConfig.register()
        val keyset = KeysetHandle.generateNew(PredefinedAeadParameters.AES256_GCM)
        // Sealed by a master key this phone no longer has.
        val sealed = TinkProtoKeysetFormat.serializeEncryptedKeyset(keyset, TestAead.create(), ByteArray(0))
        keysetPrefs().edit().putString(KEYSET_NAME, Hex.encode(sealed)).commit()
        writeOldSessionFile()

        // Built as the Application builds it: this used to throw on every start.
        val container = AppContainer(context, BASE_URL, KeystoreAead.create(context))

        assertFalse("the session it encrypted is discarded", context.dataStoreFile(SESSION_FILE).exists())
        assertNoKeysetOnDisk()
        assertSignInWorks(container)
    }

    /** The patient can sign in again. */
    private fun assertSignInWorks(container: AppContainer) {
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
        assertEquals(TOKEN, runBlocking { container.sessionStore.token.first() })
    }

    private fun assertNoKeysetOnDisk() {
        assertFalse("no keyset in the prefs", keysetPrefs().contains(KEYSET_NAME))
        val prefsFiles = File(context.dataDir, "shared_prefs").listFiles().orEmpty()
        prefsFiles.forEach { file ->
            assertFalse("a keyset in ${file.path}", file.readText().contains(KEYSET_NAME))
        }
        assertTrue("checked the shared_prefs folder", prefsFiles.none { it.name == "$KEYSET_PREFS.xml" })
    }

    private fun writeOldSessionFile() {
        context.dataStoreFile(SESSION_FILE).apply {
            parentFile?.mkdirs()
            writeBytes(byteArrayOf(0x0a, 0x01, 0x02, 0x03))
        }
    }

    private fun keysetPrefs() = context.getSharedPreferences(KEYSET_PREFS, Context.MODE_PRIVATE)

    private companion object {
        const val BASE_URL = "http://localhost/api/v1/"
        const val SESSION_FILE = "session.pb"

        // The names KeystoreAead gives the keyset (BackupRulesTest checks the same file is left out of backups).
        const val KEYSET_NAME = "session_keyset"
        const val KEYSET_PREFS = "mx.globalhealth.paciente.session_keyset"
    }
}
