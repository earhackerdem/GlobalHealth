package mx.globalhealth.paciente.core.session

import android.content.Context
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import mx.globalhealth.paciente.testing.FakeApi.Companion.TOKEN
import mx.globalhealth.paciente.testing.TestAead
import mx.globalhealth.paciente.testing.appFiles
import mx.globalhealth.paciente.testing.containsSequence
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment

/**
 * AB-6 · design.md Test plan row 8: after saving a known token, no file under the app's data dir holds it in clear.
 * `SessionStore(context, aead, fileName)` per the Kotlin contract; the AEAD is an in-memory Tink keyset because
 * Robolectric has no Android Keystore.
 */
@RunWith(RobolectricTestRunner::class)
class SessionStoreEncryptionTest {

    private val context: Context = RuntimeEnvironment.getApplication()

    @Test
    fun ab6_trasGuardarElToken_ningunArchivoDeLaAppLoContieneEnClaro() {
        val fileName = "session_ab6.pb"
        val store = SessionStore(context, TestAead.create(), fileName)

        runBlocking<Unit> { store.save(TOKEN) }

        assertEquals("the store gives the token back", TOKEN, runBlocking { store.token.first() })
        val files = appFiles(context)
        assertTrue(
            "the session is persisted to a file named $fileName under the app's data dir",
            files.any { it.name == fileName && it.length() > 0 },
        )
        files.forEach { file ->
            assertFalse("token in clear in ${file.path}", file.readBytes().containsSequence(TOKEN.toByteArray()))
        }
    }

    @Test
    fun ab5_clear_borraElTokenGuardado() {
        val store = SessionStore(context, TestAead.create(), "session_ab5.pb")
        runBlocking<Unit> { store.save(TOKEN) }

        runBlocking<Unit> { store.clear() }

        assertNull(runBlocking { store.token.first() })
    }
}
