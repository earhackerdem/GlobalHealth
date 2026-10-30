package mx.globalhealth.paciente.core.net

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import retrofit2.http.Body
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.GET
import retrofit2.http.POST

/**
 * The GlobalHealth API (`/api/v1`), written by hand (design.md, Decision 1). Paths are relative to the base URL and
 * keep the backend's trailing slashes (`consent/`), so FastAPI never answers with a redirect. The bearer token and the
 * 401 handling live in [SessionInterceptor], not here.
 */
interface GlobalHealthApi {

    @FormUrlEncoded
    @POST("login/access-token")
    suspend fun login(@Field("username") email: String, @Field("password") password: String): Token

    @GET("consent/text")
    suspend fun consentText(): ConsentText

    @POST("consent/")
    suspend fun grantConsent(@Body grant: ConsentGrant): ConsentRecord

    /** Answers 403 `CONSENT_REQUIRED` while consent is missing (design.md, Decision 3). */
    @GET("profile")
    suspend fun profile(): Profile
}

@Serializable
data class Token(
    @SerialName("access_token") val accessToken: String,
    @SerialName("token_type") val tokenType: String = "bearer",
)

@Serializable
data class ConsentText(val version: String, val text: String)

@Serializable
data class ConsentGrant(val version: String)

@Serializable
data class ConsentRecord(val version: String, @SerialName("granted_at") val grantedAt: String? = null)

/**
 * `GET profile`. Group 1 only needs the call to succeed; group 2 adds the fields it shows. Kept in memory only
 * (design.md, Decision 6): it is never written to disk.
 */
@Serializable
data class Profile(
    @SerialName("birth_date") val birthDate: String? = null,
    val sex: String? = null,
    val allergies: String? = null,
)
