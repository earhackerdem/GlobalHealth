package mx.globalhealth.paciente.core.net

import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import mx.globalhealth.paciente.core.session.SessionStore
import okhttp3.Interceptor
import okhttp3.Response

/**
 * Adds `Authorization: Bearer <token>` when there is a session and, on any 401 or any 403 other than
 * `CONSENT_REQUIRED` (how the API answers an expired or invalid token, `backend/app/api/deps.py:38-42`), clears it
 * (AB-5): the app observes [SessionStore.token] and goes back to the login screen by itself, whatever screen made the
 * request.
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
        if (token != null && response.isSessionEnd()) {
            runBlocking { sessionStore.clearIfCurrent(token) }
        }
        return response
    }

    /** Peeks at a 403's `detail` (a copy: the body stays readable for [apiCall]). */
    private fun Response.isSessionEnd(): Boolean {
        val detail = if (code == HTTP_FORBIDDEN) errorDetail(peekBody(MAX_ERROR_BODY_BYTES).string()) else null
        return endsSession(code, detail)
    }

    private companion object {
        const val HTTP_FORBIDDEN = 403
        const val MAX_ERROR_BODY_BYTES = 4_096L
    }
}
