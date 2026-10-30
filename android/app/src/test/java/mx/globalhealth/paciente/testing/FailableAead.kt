package mx.globalhealth.paciente.testing

import com.google.crypto.tink.Aead
import java.security.GeneralSecurityException

/**
 * Wraps a test AEAD so a test can make the session file unwritable: with [failWrites] on, every encrypt throws, so
 * `SessionStore.save` and `clear` fail as they would on a broken Keystore or a full disk.
 */
class FailableAead(private val delegate: Aead = TestAead.create()) : Aead {

    @Volatile var failWrites: Boolean = false

    /** How many writes failed, so a test can wait for the attempt. */
    @Volatile var failedWrites: Int = 0
        private set

    override fun encrypt(plaintext: ByteArray, associatedData: ByteArray): ByteArray {
        if (failWrites) {
            failedWrites++
            throw GeneralSecurityException("test: the session cannot be written")
        }
        return delegate.encrypt(plaintext, associatedData)
    }

    override fun decrypt(ciphertext: ByteArray, associatedData: ByteArray): ByteArray =
        delegate.decrypt(ciphertext, associatedData)
}
