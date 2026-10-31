package mx.globalhealth.paciente.core.session

import android.content.Context
import androidx.datastore.dataStoreFile
import java.security.GeneralSecurityException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.cancelAndJoin
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import mx.globalhealth.paciente.testing.FakeApi.Companion.TOKEN
import mx.globalhealth.paciente.testing.TestAead
import mx.globalhealth.paciente.testing.appFiles
import mx.globalhealth.paciente.testing.containsSequence
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertThrows
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
        val aead = TestAead.create()
        val store = SessionStore(context, aead, fileName)

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

        // Not merely unreadable (Base64 would pass the scan above): the file is the token sealed with this AEAD,
        // bound to the file name, and another key does not open it.
        val sealed = context.dataStoreFile(fileName).readBytes()
        val associatedData = fileName.encodeToByteArray()
        assertEquals("the same AEAD opens the file", TOKEN, aead.decrypt(sealed, associatedData).decodeToString())
        assertThrows(GeneralSecurityException::class.java) { TestAead.create().decrypt(sealed, associatedData) }
    }

    @Test
    fun ab5_clear_borraElTokenGuardado() {
        val store = SessionStore(context, TestAead.create(), "session_ab5.pb")
        runBlocking<Unit> { store.save(TOKEN) }

        runBlocking<Unit> { store.clear() }

        assertNull(runBlocking { store.token.first() })
    }

    /** A late 401/403 for an old token must not end a newer session. */
    @Test
    fun ab5_clearIfCurrent_soloBorraSiElTokenGuardadoEsEse() {
        val store = SessionStore(context, TestAead.create(), "session_clear_if_current.pb")
        runBlocking<Unit> { store.save(TOKEN_B) }

        runBlocking<Unit> { store.clearIfCurrent(TOKEN_A) }
        assertEquals("another token keeps the session", TOKEN_B, runBlocking { store.token.first() })

        runBlocking<Unit> { store.clearIfCurrent(TOKEN_B) }
        assertNull("its own token clears it", runBlocking { store.token.first() })
    }

    /** AB-5 «Volver a abrir la app»: what one instance saved, a new one over the same file reads back. */
    @Test
    fun ab5_unaInstanciaNuevaSobreElMismoArchivo_leeElTokenGuardado() {
        val fileName = "session_reopen.pb"
        val aead = TestAead.create()
        val first = SessionStore(context, aead, fileName)
        runBlocking<Unit> { first.save(TOKEN) }
        close(first)

        val reopened = SessionStore(context, aead, fileName)

        assertEquals(TOKEN, runBlocking { reopened.token.first() })
    }

    /** A file the current key cannot open (a lost Keystore key) reads as "no session", without failing. */
    @Test
    fun ab5_conOtraLlave_elArchivoGuardadoSeLeeComoSinSesion() {
        val fileName = "session_other_key.pb"
        val first = SessionStore(context, TestAead.create(), fileName)
        runBlocking<Unit> { first.save(TOKEN) }
        close(first)

        val withOtherKey = SessionStore(context, TestAead.create(), fileName)

        assertNull(runBlocking { withOtherKey.token.first() })
    }

    /**
     * DataStore refuses two live instances over one file in a process; a new process is what releases it. Here the
     * first instance's DataStore scope is cancelled instead, reached by reflection (test only: production code keeps
     * one store per process and needs no way to close it).
     */
    private fun close(store: SessionStore) {
        val dataStore = SessionStore::class.java.getDeclaredField("dataStore").apply { isAccessible = true }.get(store)
        val scopeField = generateSequence<Class<*>>(dataStore.javaClass) { it.superclass }
            .flatMap { it.declaredFields.asSequence() }
            .first { CoroutineScope::class.java.isAssignableFrom(it.type) }
            .apply { isAccessible = true }
        val job = checkNotNull((scopeField.get(dataStore) as CoroutineScope).coroutineContext[Job])
        runBlocking { job.cancelAndJoin() }
    }

    private companion object {
        const val TOKEN_A = "token-a-anterior"
        const val TOKEN_B = "token-b-vigente"
    }
}
