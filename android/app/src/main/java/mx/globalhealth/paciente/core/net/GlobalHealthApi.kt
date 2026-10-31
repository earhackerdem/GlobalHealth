package mx.globalhealth.paciente.core.net

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonObject
import retrofit2.http.Body
import retrofit2.http.Field
import retrofit2.http.FormUrlEncoded
import retrofit2.http.GET
import retrofit2.http.POST

/**
 * The GlobalHealth API (`/api/v1`), written by hand (design.md, Decision 1). Paths are relative to the base URL and
 * keep the backend's trailing slashes (`consent/`), so FastAPI never answers with a redirect. The bearer token and the
 * 401/403 handling live in [SessionInterceptor], not here.
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

    @GET("profile/work")
    suspend fun work(): Work

    /** Every entry of the five event/chronic sections; the screen counts them per `section`. */
    @GET("profile/history")
    suspend fun history(): HistoryEntries

    /** Read as a raw object: the card only asks whether any top-level answer is not null (`hasHabits`). */
    @GET("profile/habits")
    suspend fun habits(): JsonObject

    @GET("profile/family-history")
    suspend fun familyHistory(): FamilyHistoryEntries
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

/*
 * The profile models carry only the fields «Mi perfil médico» shows; the client's `Json` ignores the rest. They are
 * kept in memory only (design.md, Decision 6): never written to disk.
 */

/** `GET profile`. */
@Serializable
data class Profile(
    @SerialName("birth_date") val birthDate: String? = null,
    val sex: String? = null,
    val allergies: String? = null,
    @SerialName("latest_weight") val latestWeight: Measurement? = null,
    @SerialName("latest_height") val latestHeight: Measurement? = null,
    /** The history sections the patient marked «Ninguna» (`chronic`, `past`, …). */
    @SerialName("sections_none") val sectionsNone: List<String> = emptyList(),
)

@Serializable
data class Measurement(val value: Double, @SerialName("measured_on") val measuredOn: String? = null)

/** `GET profile/work`. */
@Serializable
data class Work(
    val status: String? = null,
    val occupation: String? = null,
    @SerialName("longest_job") val longestJob: String? = null,
    val exposures: List<String> = emptyList(),
    val shift: String? = null,
)

/** `GET profile/history`. */
@Serializable
data class HistoryEntries(val data: List<HistoryEntry> = emptyList())

@Serializable
data class HistoryEntry(val section: String)

/** `GET profile/family-history`: the card only shows how many there are. */
@Serializable
data class FamilyHistoryEntries(val data: List<FamilyHistoryEntry> = emptyList())

@Serializable
data class FamilyHistoryEntry(val condition: String? = null)
