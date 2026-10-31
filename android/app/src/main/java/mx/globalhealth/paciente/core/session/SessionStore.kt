package mx.globalhealth.paciente.core.session

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.core.DataStoreFactory
import androidx.datastore.core.Serializer
import androidx.datastore.core.handlers.ReplaceFileCorruptionHandler
import androidx.datastore.dataStoreFile
import androidx.datastore.tink.AeadSerializer
import com.google.crypto.tink.Aead
import java.io.InputStream
import java.io.OutputStream
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

/**
 * The session token, and nothing else, persisted in `filesDir/datastore/<fileName>` (AB-5, AB-6).
 *
 * The file content is encrypted with [aead] through datastore-tink's [AeadSerializer]: in production the AEAD comes
 * from [KeystoreAead] (keyset under an Android Keystore master key); tests pass an in-memory Tink AEAD. The
 * `datastore/` folder is excluded from backups (`backup_rules.xml`, `data_extraction_rules.xml`), since the Keystore key does not survive a
 * restore. A file that cannot be decrypted is replaced by "no session": the patient just signs in again.
 *
 * Without an [aead] (no usable Keystore: [KeystoreAead.create] gives null) nothing is written to disk and the session
 * lasts while the process lives (spec AB-6).
 *
 * DataStore allows one instance per file per process, so the app keeps a single [SessionStore] (in [AppContainer],
 * which lives in the Application).
 */
class SessionStore(context: Context, aead: Aead?, fileName: String = DEFAULT_FILE_NAME) {

    private val dataStore: DataStore<String> =
        if (aead == null) {
            InMemoryStore()
        } else {
            DataStoreFactory.create(
                serializer = AeadSerializer(aead, TokenSerializer, fileName.encodeToByteArray()),
                corruptionHandler = ReplaceFileCorruptionHandler { NO_TOKEN },
                produceFile = { context.applicationContext.dataStoreFile(fileName) },
            )
        }

    /** The saved token, or null without a session. */
    val token: Flow<String?> = dataStore.data.map { it.ifEmpty { null } }

    suspend fun save(token: String) {
        dataStore.updateData { token }
    }

    suspend fun clear() {
        dataStore.updateData { NO_TOKEN }
    }

    /** Clears the session only if it still holds [token]: a late 401 for an old token must not end a newer one. */
    suspend fun clearIfCurrent(token: String) {
        dataStore.updateData { current -> if (current == token) NO_TOKEN else current }
    }

    /** The session without a file: same contract as the DataStore, kept in this process only. */
    private class InMemoryStore : DataStore<String> {
        private val state = MutableStateFlow(NO_TOKEN)
        private val mutex = Mutex()

        override val data: Flow<String> = state

        override suspend fun updateData(transform: suspend (t: String) -> String): String =
            mutex.withLock { transform(state.value).also { state.value = it } }
    }

    private object TokenSerializer : Serializer<String> {
        override val defaultValue: String = NO_TOKEN

        override suspend fun readFrom(input: InputStream): String = input.readBytes().decodeToString()

        override suspend fun writeTo(t: String, output: OutputStream) {
            output.write(t.encodeToByteArray())
        }
    }

    companion object {
        const val DEFAULT_FILE_NAME = "session.pb"
        private const val NO_TOKEN = ""
    }
}
