package mx.globalhealth.paciente

import java.io.File
import javax.xml.parsers.DocumentBuilderFactory
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import org.w3c.dom.Element

/**
 * AB-6: the session file and its keyset never leave the phone in a backup (their Keystore key does not survive a
 * restore). Reads the sources (Gradle runs unit tests from the module folder): the manifest must point at both rule
 * files, and each of cloud-backup, device-transfer (Android 12+) and full-backup-content (Android 10 and 11) must
 * exclude `datastore/session.pb` and the keyset's shared prefs.
 */
class BackupRulesTest {

    @Test
    fun ab6_elAndroidManifestUsaLasDosReglasDeRespaldo() {
        val application = parse("src/main/AndroidManifest.xml").getElementsByTagName("application").item(0) as Element

        assertEquals("@xml/data_extraction_rules", application.getAttributeNS(ANDROID, "dataExtractionRules"))
        assertEquals("@xml/backup_rules", application.getAttributeNS(ANDROID, "fullBackupContent"))
    }

    @Test
    fun ab6_laSesionYSuKeysetQuedanFueraDelRespaldoEnLaNubeYDeLaTransferencia() {
        val rules = parse("src/main/res/xml/data_extraction_rules.xml")
        listOf("cloud-backup", "device-transfer").forEach { section ->
            val element = rules.getElementsByTagName(section).item(0) as? Element
            assertTrue("<$section> exists", element != null)
            assertExcluded(section, element!!)
        }
    }

    @Test
    fun ab6_laSesionYSuKeysetQuedanFueraDelRespaldoCompleto() {
        assertExcluded("full-backup-content", parse("src/main/res/xml/backup_rules.xml").documentElement)
    }

    private fun assertExcluded(section: String, rules: Element) {
        val excludes = rules.getElementsByTagName("exclude").let { list -> (0 until list.length).map { list.item(it) as Element } }
        fun excluded(domain: String, target: String) = excludes.any { exclude ->
            val path = exclude.getAttribute("path").trimEnd('/')
            exclude.getAttribute("domain") == domain && (path == "." || target == path || target.startsWith("$path/"))
        }
        assertTrue("$section excludes the session file", excluded("file", SESSION_FILE))
        assertTrue("$section excludes the keyset prefs", excluded("sharedpref", KEYSET_PREFS_FILE))
    }

    private fun parse(path: String) =
        DocumentBuilderFactory.newInstance().apply { isNamespaceAware = true }.newDocumentBuilder().parse(File(path))

    private companion object {
        const val ANDROID = "http://schemas.android.com/apk/res/android"
        const val SESSION_FILE = "datastore/session.pb"

        // The prefs file KeystoreAead keeps the keyset in (KeystoreAeadTest uses the same name).
        const val KEYSET_PREFS_FILE = "mx.globalhealth.paciente.session_keyset.xml"
    }
}
