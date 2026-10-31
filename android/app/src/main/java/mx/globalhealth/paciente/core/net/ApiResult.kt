package mx.globalhealth.paciente.core.net

import java.io.IOException
import kotlinx.serialization.SerializationException
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.jsonObject
import retrofit2.HttpException

/** What the screens need to know about an API call (design.md, Interface contract). */
sealed interface ApiResult<out T> {
    data class Ok<T>(val value: T) : ApiResult<T>

    /** No network, the API is down or dropped the connection, or a gateway answers 502/503/504 (AB-7). The session is kept. */
    data object Offline : ApiResult<Nothing>

    /**
     * A 401, or a 403 other than `CONSENT_REQUIRED` (the API's answer to an expired or invalid token,
     * `backend/app/api/deps.py:38-42`): [SessionInterceptor] already cleared the session, and the app goes back to
     * the login screen (AB-5).
     */
    data object Unauthorized : ApiResult<Nothing>

    /** A 403 with detail `CONSENT_REQUIRED` (AB-3, design.md Decision 3). */
    data object ConsentRequired : ApiResult<Nothing>

    /** A 400, with the API's `detail` text when it is a string (e.g. «Correo o contraseña incorrectos», AB-2). */
    data class Rejected(val detail: String?) : ApiResult<Nothing>

    /** Anything else: another status, or a body the app cannot read. */
    data class Failed(val code: Int?) : ApiResult<Nothing>
}

private const val CONSENT_REQUIRED = "CONSENT_REQUIRED"

/** Whether an error status ends the session: 401, or 403 without `CONSENT_REQUIRED` (shared with [SessionInterceptor]). */
internal fun endsSession(code: Int, detail: String?): Boolean =
    code == 401 || (code == 403 && detail != CONSENT_REQUIRED)

/** Runs one Retrofit call and maps its outcome; coroutine cancellation is not caught. */
suspend fun <T> apiCall(block: suspend () -> T): ApiResult<T> =
    try {
        ApiResult.Ok(block())
    } catch (e: HttpException) {
        val detail = e.detail()
        when {
            e.code() == 403 && detail == CONSENT_REQUIRED -> ApiResult.ConsentRequired
            endsSession(e.code(), detail) -> ApiResult.Unauthorized
            e.code() == 400 -> ApiResult.Rejected(detail)
            // A proxy or load balancer in front of a stopped API: the same «sin conexión» as no answer (AB-7).
            e.code() in 502..504 -> ApiResult.Offline
            else -> ApiResult.Failed(e.code())
        }
    } catch (e: IOException) {
        ApiResult.Offline
    } catch (e: SerializationException) {
        ApiResult.Failed(null)
    }

// Retrofit buffers error bodies, so reading it here does no I/O.
private fun HttpException.detail(): String? =
    runCatching { response()?.errorBody()?.string() }.getOrNull()?.let(::errorDetail)

/** FastAPI errors are `{"detail": "..."}`; validation errors carry a list instead, which yields null. */
internal fun errorDetail(body: String): String? =
    runCatching {
        val detail = Json.parseToJsonElement(body).jsonObject["detail"] as? JsonPrimitive
        detail?.takeIf { it.isString }?.content
    }.getOrNull()
