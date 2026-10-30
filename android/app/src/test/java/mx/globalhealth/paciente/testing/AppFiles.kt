package mx.globalhealth.paciente.testing

import android.content.Context
import java.io.File

/**
 * Every file the app can write: its data dir holds files, cache, no_backup, databases and shared_prefs; the external
 * files and cache dirs live elsewhere (AB-6).
 */
fun appFiles(context: Context): List<File> =
    listOfNotNull(
        context.dataDir,
        context.filesDir,
        context.cacheDir,
        context.noBackupFilesDir,
        context.getExternalFilesDir(null),
        context.externalCacheDir,
    )
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
