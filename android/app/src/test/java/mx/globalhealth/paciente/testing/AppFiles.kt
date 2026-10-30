package mx.globalhealth.paciente.testing

import android.content.Context
import java.io.File

/** Every file the app can write: its data dir holds files, cache, no_backup, databases and shared_prefs (AB-6). */
fun appFiles(context: Context): List<File> =
    listOf(context.dataDir, context.filesDir, context.cacheDir, context.noBackupFilesDir)
        .flatMap { root -> root.walkTopDown().filter { it.isFile }.toList() }
        .distinctBy { it.canonicalPath }

fun ByteArray.containsSequence(needle: ByteArray): Boolean {
    if (needle.isEmpty() || needle.size > size) return false
    outer@ for (i in 0..size - needle.size) {
        for (j in needle.indices) if (this[i + j] != needle[j]) continue@outer
        return true
    }
    return false
}
