package mx.globalhealth.paciente.core.net

import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import mx.globalhealth.paciente.core.session.SessionStore
import okhttp3.Interceptor
import okhttp3.Response

/**
 * Adds `Authorization: Bearer <token>` when there is a session and, on any 401, clears it (AB-5): the app observes
 * [SessionStore.token] and goes back to the login screen by itself, whatever screen made the request.
 *
 * Interceptors run on OkHttp's threads, never on the main thread, so blocking on the store here is safe.
 */
class SessionInterceptor(private val sessionStore: SessionStore) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val token = runBlocking { sessionStore.token.first() }
        val request = chain.request().let { original ->
            if (token == null) original else original.newBuilder().header("Authorization", "Bearer $token").build()
        }
        val response = chain.proceed(request)
        if (response.code == HTTP_UNAUTHORIZED && token != null) {
            runBlocking { sessionStore.clearIfCurrent(token) }
        }
        return response
    }

    private companion object {
        const val HTTP_UNAUTHORIZED = 401
    }
}
