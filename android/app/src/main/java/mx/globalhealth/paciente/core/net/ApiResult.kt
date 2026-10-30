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

    /** No network, the API is down or dropped the connection (AB-7). The session is kept. */
    data object Offline : ApiResult<Nothing>

    /** A 401: [SessionInterceptor] already cleared the session, and the app goes back to the login screen (AB-5). */
    data object Unauthorized : ApiResult<Nothing>

    /** A 403 with detail `CONSENT_REQUIRED` (AB-3, design.md Decision 3). */
    data object ConsentRequired : ApiResult<Nothing>

    /** A 400, with the API's `detail` text when it is a string (e.g. «Correo o contraseña incorrectos», AB-2). */
    data class Rejected(val detail: String?) : ApiResult<Nothing>

    /** Anything else: another status, or a body the app cannot read. */
    data class Failed(val code: Int?) : ApiResult<Nothing>
}

private const val CONSENT_REQUIRED = "CONSENT_REQUIRED"

/** Runs one Retrofit call and maps its outcome; coroutine cancellation is not caught. */
suspend fun <T> apiCall(block: suspend () -> T): ApiResult<T> =
    try {
        ApiResult.Ok(block())
    } catch (e: HttpException) {
        val detail = e.detail()
        when {
            e.code() == 401 -> ApiResult.Unauthorized
            e.code() == 403 && detail == CONSENT_REQUIRED -> ApiResult.ConsentRequired
            e.code() == 400 -> ApiResult.Rejected(detail)
            else -> ApiResult.Failed(e.code())
        }
    } catch (e: IOException) {
        ApiResult.Offline
    } catch (e: SerializationException) {
        ApiResult.Failed(null)
    }

/** FastAPI errors are `{"detail": "..."}`; validation errors carry a list instead, which yields null. */
private fun HttpException.detail(): String? =
    runCatching {
        // Retrofit buffers error bodies, so reading it here does no I/O.
        val body = response()?.errorBody()?.string().orEmpty()
        val detail = Json.parseToJsonElement(body).jsonObject["detail"] as? JsonPrimitive
        detail?.takeIf { it.isString }?.content
    }.getOrNull()
