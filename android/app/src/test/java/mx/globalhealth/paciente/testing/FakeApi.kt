package mx.globalhealth.paciente.testing

import java.net.URLDecoder
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.CopyOnWriteArrayList
import mockwebserver3.Dispatcher
import mockwebserver3.MockResponse
import mockwebserver3.RecordedRequest
import mockwebserver3.SocketEffect

/**
 * A stand-in for the GlobalHealth API (`/api/v1`) behind MockWebServer, shaped like the real FastAPI routes
 * (design.md, Interface contract): bearer auth on everything but login (401 without the header, 403 «No se pudieron
 * validar las credenciales» with an expired or invalid token, as `backend/app/api/deps.py:38-42`), 403
 * `CONSENT_REQUIRED` on the health-data routes (`profile*`) while consent is missing, `{"detail": "..."}` error
 * bodies. Routes are matched by "METHOD path" with the `/api/v1/` prefix and any trailing slash removed, so the order
 * in which the app calls them does not matter. A test overrides one route with [respond].
 */
class FakeApi(
    private val validToken: String = TOKEN,
    @Volatile var consentGranted: Boolean = true,
    /** The version `consent/text` serves and `consent/` records. */
    @Volatile var consentVersion: String = "v1",
) : Dispatcher() {

    val requests: MutableList<RecordedRequest> = CopyOnWriteArrayList()

    private val overrides = ConcurrentHashMap<String, () -> MockResponse>()

    /** Overrides one route, e.g. `respond("GET profile") { json(401, ...) }`. */
    fun respond(route: String, response: () -> MockResponse) {
        overrides[route] = response
    }

    fun restore(route: String) {
        overrides.remove(route)
    }

    fun requestsTo(route: String): List<RecordedRequest> = requests.filter { routeOf(it) == route }

    /**
     * The data of the spec scenario "Perfil con datos" (AB-4): born 1990-03-15, «Mujer», «Penicilina», 72 kg and
     * 165 cm measured on 2026-10-12, the rotating driver exposed to loud noise, two `past` entries, «Ninguna» in
     * transfusions, no habits and three family-history entries.
     */
    fun serveAb4Profile() {
        respond("GET profile") { json(200, AB4_PROFILE) }
        respond("GET profile/work") { json(200, AB4_WORK) }
        respond("GET profile/history") { json(200, AB4_HISTORY) }
        respond("GET profile/habits") { json(200, EMPTY_HABITS) }
        respond("GET profile/family-history") { json(200, AB4_FAMILY_HISTORY) }
    }

    /** A profile with nothing recorded: every basic-data row says «Sin registrar». */
    fun serveEmptyProfile() {
        respond("GET profile") { json(200, EMPTY_PROFILE) }
        respond("GET profile/work") { json(200, EMPTY_WORK) }
        respond("GET profile/history") { json(200, """{"data":[],"count":0}""") }
        respond("GET profile/habits") { json(200, EMPTY_HABITS) }
        respond("GET profile/family-history") { json(200, """{"data":[],"count":0}""") }
    }

    override fun dispatch(request: RecordedRequest): MockResponse {
        requests += request
        val route = routeOf(request)
        overrides[route]?.let { return it() }
        return default(route, request)
    }

    private fun default(route: String, request: RecordedRequest): MockResponse {
        if (route == "POST login/access-token") {
            return json(200, """{"access_token":"$validToken","token_type":"bearer"}""")
        }
        val auth = request.headers["Authorization"]
        if (auth == null) return json(401, """{"detail":"Not authenticated"}""")
        if (auth != "Bearer $validToken") return json(403, """{"detail":"$INVALID_CREDENTIALS"}""")

        val path = route.substringAfter(' ')
        if (path.startsWith("profile") && !consentGranted) {
            return json(403, """{"detail":"CONSENT_REQUIRED"}""")
        }
        return when (route) {
            "GET users/me" -> json(200, """{"email":"$EMAIL","full_name":"Paciente Android","is_active":true}""")
            "GET consent/text" -> json(200, """{"version":"$consentVersion","text":"$CONSENT_TEXT"}""")
            "GET consent" ->
                if (consentGranted) {
                    json(200, """{"version":"$consentVersion","granted_at":"2026-10-29T10:00:00Z"}""")
                } else {
                    json(404, """{"detail":"Consent not granted"}""")
                }
            "POST consent" -> grantConsent()
            "GET profile" -> json(200, PROFILE_BODY)
            "GET profile/work" ->
                json(
                    200,
                    """{"status":null,"occupation":null,"longest_job":null,"exposures":[],""" +
                        """"no_exposures":false,"shift":null}""",
                )
            "GET profile/history" -> json(200, """{"data":[],"count":0}""")
            "GET profile/habits" -> json(200, """{"smoking":null,"alcohol":null,"physical_activity":null}""")
            "GET profile/family-history" -> json(200, """{"data":[],"count":0}""")
            else -> json(404, """{"detail":"Not Found"}""")
        }
    }

    /** What `POST consent/` does: records the grant and answers 200. An override of that route can call it too. */
    fun grantConsent(): MockResponse {
        consentGranted = true
        return json(
            200,
            """{"version":"$consentVersion","granted_at":"2026-10-29T10:00:00Z","auth_method":"password"}""",
        )
    }

    companion object {
        /** The real API's 403 for an expired or invalid token (`backend/app/api/deps.py:38-42`). */
        const val INVALID_CREDENTIALS = "No se pudieron validar las credenciales"

        const val TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJwcnVlYmEifQ.prueba-android-base"
        const val EMAIL = "paciente.android@example.com"
        const val PASSWORD = "contrasena-de-prueba-1"
        const val NO_CONSENT_EMAIL = "sin.consentimiento@example.com"
        const val CONSENT_TEXT =
            "Autorizo a GlobalHealth a tratar mis datos de salud para llevar mi historial médico."

        /** A profile value no file on the phone may contain (AB-6). */
        const val PROFILE_MARKER = "Penicilina-marcador-AB6"

        val PROFILE_BODY =
            """{"birth_date":"1990-03-15","sex":"female","allergies":"$PROFILE_MARKER","onboarding":"completed",""" +
                """"latest_weight":null,"latest_height":null,"blood_type":null,"sections_none":[]}"""

        const val AB4_PROFILE =
            """{"birth_date":"1990-03-15","sex":"female","allergies":"Penicilina","onboarding":"completed",""" +
                """"latest_weight":{"value":72.0,"measured_on":"2026-10-12"},""" +
                """"latest_height":{"value":165.0,"measured_on":"2026-10-12"},""" +
                """"blood_type":null,"sections_none":["transfusions"]}"""

        const val AB4_WORK =
            """{"status":"employed","occupation":"Chofer de transporte","longest_job":null,""" +
                """"exposures":["loud_noise"],"no_exposures":false,"shift":"rotating"}"""

        const val AB4_HISTORY =
            """{"data":[""" +
                """{"id":"7d1f0c2e-0000-4000-8000-000000000001","section":"past","condition":"covid",""" +
                """"other_text":null,"hospitalized":false,"note":null},""" +
                """{"id":"7d1f0c2e-0000-4000-8000-000000000002","section":"past","condition":"dengue",""" +
                """"other_text":null,"hospitalized":true,"note":"2019"}""" +
                """],"count":2}"""

        const val AB4_FAMILY_HISTORY =
            """{"data":[""" +
                """{"id":"5a2b0c2e-0000-4000-8000-000000000001","condition":"diabetes","other_text":null,""" +
                """"relatives":["mother"],"note":null},""" +
                """{"id":"5a2b0c2e-0000-4000-8000-000000000002","condition":"hypertension","other_text":null,""" +
                """"relatives":["father","mother"],"note":null},""" +
                """{"id":"5a2b0c2e-0000-4000-8000-000000000003","condition":"cancer","other_text":null,""" +
                """"relatives":["grandparent"],"note":"mama"}""" +
                """],"count":3}"""

        const val EMPTY_PROFILE =
            """{"birth_date":null,"sex":null,"allergies":null,"onboarding":"pending",""" +
                """"latest_weight":null,"latest_height":null,"blood_type":null,"sections_none":[]}"""

        const val EMPTY_WORK =
            """{"status":null,"occupation":null,"longest_job":null,"exposures":[],""" +
                """"no_exposures":false,"shift":null}"""

        const val EMPTY_HABITS = """{"smoking":null,"alcohol":null,"physical_activity":null}"""

        fun json(code: Int, body: String): MockResponse =
            MockResponse.Builder()
                .code(code)
                .addHeader("Content-Type", "application/json")
                .body(body)
                .build()

        /** The server accepts the request and drops the connection without answering. */
        fun disconnect(): MockResponse =
            MockResponse.Builder()
                .onResponseStart(SocketEffect.CloseSocket())
                .build()

        fun routeOf(request: RecordedRequest): String {
            val path = request.url.encodedPath.removePrefix("/api/v1/").trimEnd('/')
            return "${request.method} $path"
        }

        fun formOf(request: RecordedRequest): Map<String, String> {
            val body = request.body?.utf8().orEmpty()
            if (body.isEmpty()) return emptyMap()
            return body.split('&').associate { pair ->
                val name = pair.substringBefore('=')
                val value = pair.substringAfter('=', "")
                URLDecoder.decode(name, "UTF-8") to URLDecoder.decode(value, "UTF-8")
            }
        }
    }
}
