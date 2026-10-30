package mx.globalhealth.paciente.core.net

import kotlinx.coroutines.runBlocking
import mx.globalhealth.paciente.testing.FakeApi.Companion.INVALID_CREDENTIALS
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.ResponseBody.Companion.toResponseBody
import org.junit.Assert.assertEquals
import org.junit.Test
import retrofit2.HttpException
import retrofit2.Response

/** How [apiCall] maps the API's errors (design.md, Interface contract → API usada; AB-3, AB-5, AB-7). */
class ApiResultTest {

    @Test
    fun ab5_un401_terminaLaSesion() {
        assertEquals(ApiResult.Unauthorized, failWith(401, """{"detail":"Not authenticated"}"""))
    }

    @Test
    fun ab5_un403DeCredenciales_terminaLaSesion() {
        assertEquals(ApiResult.Unauthorized, failWith(403, """{"detail":"$INVALID_CREDENTIALS"}"""))
    }

    @Test
    fun ab5_un403SinDetalleLegible_terminaLaSesion() {
        assertEquals(ApiResult.Unauthorized, failWith(403, "Forbidden"))
    }

    @Test
    fun ab3_un403ConsentRequired_llevaAlConsentimiento() {
        assertEquals(ApiResult.ConsentRequired, failWith(403, """{"detail":"CONSENT_REQUIRED"}"""))
    }

    @Test
    fun ab7_502_503_y504_cuentanComoSinConexion() {
        listOf(502, 503, 504).forEach { code ->
            assertEquals("HTTP $code", ApiResult.Offline, failWith(code, """{"detail":"Bad Gateway"}"""))
        }
    }

    @Test
    fun otrosErrores_siguenSiendoFallasOConSuMensaje() {
        assertEquals(ApiResult.Failed(500), failWith(500, """{"detail":"Internal Server Error"}"""))
        assertEquals(ApiResult.Rejected("Correo o contraseña incorrectos"), failWith(400, """{"detail":"Correo o contraseña incorrectos"}"""))
    }

    private fun failWith(code: Int, body: String): ApiResult<Unit> = runBlocking {
        apiCall<Unit> {
            throw HttpException(Response.error<Unit>(code, body.toResponseBody("application/json".toMediaType())))
        }
    }
}
