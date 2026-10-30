package mx.globalhealth.paciente.testing

import com.google.crypto.tink.Aead
import com.google.crypto.tink.KeysetHandle
import com.google.crypto.tink.RegistryConfiguration
import com.google.crypto.tink.aead.AeadConfig
import com.google.crypto.tink.aead.PredefinedAeadParameters

/**
 * Robolectric has no Android Keystore (design.md, Contrato de Kotlin para las pruebas): the tests hand the
 * production code a Tink AEAD built from an in-memory keyset. The Keystore-backed key is checked by hand on the
 * emulator.
 */
object TestAead {
    fun create(): Aead {
        AeadConfig.register()
        val handle = KeysetHandle.generateNew(PredefinedAeadParameters.AES256_GCM)
        return handle.getPrimitive(RegistryConfiguration.get(), Aead::class.java)
    }
}
