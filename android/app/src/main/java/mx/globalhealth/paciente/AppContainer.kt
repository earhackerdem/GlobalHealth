package mx.globalhealth.paciente

import android.content.Context
import com.google.crypto.tink.Aead
import java.util.concurrent.TimeUnit
import kotlinx.serialization.json.Json
import mx.globalhealth.paciente.core.net.GlobalHealthApi
import mx.globalhealth.paciente.core.net.SessionInterceptor
import mx.globalhealth.paciente.core.session.SessionStore
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory

/**
 * Manual dependency injection (design.md, Decision 4): everything the screens use, built once.
 *
 * Create one per process (the app keeps it in [GlobalHealthApplication]): [SessionStore] wraps a DataStore, and
 * DataStore refuses two live instances over the same file.
 */
class AppContainer(context: Context, baseUrl: String, aead: Aead) {

    val sessionStore: SessionStore = SessionStore(context.applicationContext, aead)

    private val json = Json { ignoreUnknownKeys = true }

    // No OkHttp cache: no response (health data included) is ever written to disk (AB-6, Decision 6).
    private val httpClient: OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(SessionInterceptor(sessionStore))
        .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        .build()

    val api: GlobalHealthApi = Retrofit.Builder()
        .baseUrl(baseUrl)
        .client(httpClient)
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build()
        .create(GlobalHealthApi::class.java)

    private companion object {
        const val TIMEOUT_SECONDS = 15L
    }
}
