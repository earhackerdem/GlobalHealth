package mx.globalhealth.paciente

import android.content.Context
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.hasAnyAncestor
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasContentDescription
import androidx.compose.ui.test.hasSetTextAction
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.isEnabled
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.performClick
import androidx.compose.ui.test.performImeAction
import androidx.compose.ui.test.performTextClearance
import androidx.compose.ui.test.performTextInput
import androidx.datastore.dataStoreFile
import java.security.GeneralSecurityException
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import mockwebserver3.MockResponse
import mockwebserver3.MockWebServer
import mx.globalhealth.paciente.core.session.SessionStore
import mx.globalhealth.paciente.testing.FailableAead
import mx.globalhealth.paciente.testing.FakeApi
import mx.globalhealth.paciente.testing.FakeApi.Companion.CONSENT_TEXT
import mx.globalhealth.paciente.testing.FakeApi.Companion.EMAIL
import mx.globalhealth.paciente.testing.FakeApi.Companion.INVALID_CREDENTIALS
import mx.globalhealth.paciente.testing.FakeApi.Companion.NO_CONSENT_EMAIL
import mx.globalhealth.paciente.testing.FakeApi.Companion.PASSWORD
import mx.globalhealth.paciente.testing.FakeApi.Companion.PROFILE_MARKER
import mx.globalhealth.paciente.testing.FakeApi.Companion.TOKEN
import mx.globalhealth.paciente.testing.FakeApi.Companion.json
import mx.globalhealth.paciente.testing.TestAead
import mx.globalhealth.paciente.testing.appFiles
import mx.globalhealth.paciente.testing.containsSequence
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config

/**
 * Group 1 of android-base: session, login and consent (spec delta AB-1, AB-2, AB-3, AB-5, AB-6, AB-7; design.md
 * Test plan rows 1, 2, 3, 4, 6, 7, 8 and 9). The whole app runs from its root, `GlobalHealthApp(container)`, against
 * MockWebServer; never a real service.
 */
@RunWith(RobolectricTestRunner::class)
class SessionLoginConsentTest {

    @get:Rule
    val composeRule = createComposeRule()

    private lateinit var server: MockWebServer
    private lateinit var api: FakeApi
    private lateinit var context: Context
    private lateinit var aead: FailableAead
    private lateinit var container: AppContainer

    @Before
    fun setUp() {
        context = RuntimeEnvironment.getApplication()
        api = FakeApi()
        server = MockWebServer()
        server.dispatcher = api
        server.start()
        aead = FailableAead()
        container = AppContainer(context, server.url("/api/v1/").toString(), aead)
    }

    @After
    fun tearDown() {
        runCatching { server.close() }
    }

    // --- AB-1 · row 1 -------------------------------------------------------------------------------------------

    /** Also on API 29, the minSdk (Android 10 in the spec); the rest of the suite runs on the default 35. */
    @Test
    @Config(sdk = [29, 35])
    fun ab1_sinToken_laPrimeraPantallaEsLaEntradaConCorreoContrasenaYEntrar() {
        startApp()

        waitForTag(LOGIN)
        composeRule.onNode(emailField).assertExists()
        composeRule.onNode(passwordField).assertExists()
        composeRule.onNode(entrarButton).assertExists()
        assertEquals("no request carries a session before login", 0, api.requests.count { it.headers["Authorization"] != null })
    }

    // --- AB-2 · row 2 -------------------------------------------------------------------------------------------

    @Test
    fun ab2_loginCorrecto_guardaElTokenYLlegaAlPerfilConBearer() {
        startApp()

        login(EMAIL, PASSWORD)

        waitForTag(PROFILE)
        composeRule.onAllNodesWithTagUnmerged(LOGIN).assertCountEquals(0)

        val loginRequest = api.requestsTo("POST login/access-token").single()
        assertTrue(
            "login is form-encoded",
            loginRequest.headers["Content-Type"].orEmpty().startsWith("application/x-www-form-urlencoded"),
        )
        val form = FakeApi.formOf(loginRequest)
        assertEquals(EMAIL, form["username"])
        assertEquals(PASSWORD, form["password"])

        waitUntil("the token is saved") { savedToken() == TOKEN }

        waitUntil("the app asks for GET profile") { api.requestsTo("GET profile").isNotEmpty() }
        api.requestsTo("GET profile").forEach { request ->
            assertEquals("Bearer $TOKEN", request.headers["Authorization"])
        }
    }

    // --- AB-2 · row 3 -------------------------------------------------------------------------------------------

    @Test
    fun ab2_contrasenaEquivocada_muestraElMensajeDeLaApiYNoGuardaNada() {
        api.respond("POST login/access-token") {
            MockResponse.Builder()
                .code(400)
                .addHeader("Content-Type", "application/json")
                .body("""{"detail":"$WRONG_CREDENTIALS"}""")
                .headersDelay(1500, TimeUnit.MILLISECONDS)
                .build()
        }
        startApp()

        login(EMAIL, "contrasena-equivocada")

        // D20: while the request is in flight «Entrar» is not available.
        composeRule.onAllNodes(entrarButton and isEnabled()).assertCountEquals(0)
        // ...and the login button is still there but disabled, whether it keeps «Entrar» or reads «Entrando…» (a
        // relabelled button that stays enabled, or no button at all, would pass the line above).
        val sending = composeRule.onAllNodes(loginButtonWhileSending).fetchSemanticsNodes()
        assertTrue("the login button is shown while the request is held", sending.isNotEmpty())
        composeRule.onAllNodes(loginButtonWhileSending and isEnabled()).assertCountEquals(0)

        waitUntil("the login error is shown") {
            composeRule.onAllNodes(loginErrorWith(WRONG_CREDENTIALS), useUnmergedTree = true)
                .fetchSemanticsNodes().isNotEmpty()
        }
        composeRule.onNode(loginErrorWith(WRONG_CREDENTIALS), useUnmergedTree = true).assertExists()
        composeRule.onAllNodesWithTagUnmerged(LOGIN).fetchSemanticsNodes().let { assertTrue("still on login", it.isNotEmpty()) }
        composeRule.onAllNodesWithTagUnmerged(PROFILE).assertCountEquals(0)

        assertNull("no session saved", savedToken())
        assertEquals("only the login request was made", 0, api.requests.count { FakeApi.routeOf(it) != "POST login/access-token" })
    }

    @Test
    fun ab2_conCorreoOContrasenaVacios_entrarNoEstaDisponibleYNoSeMandaNada() {
        startApp()
        waitForTag(LOGIN)

        composeRule.onNode(entrarButton).assertExists()
        composeRule.onAllNodes(entrarButton and isEnabled()).assertCountEquals(0)

        // Only spaces in the email still count as empty, and «Listo» on the keyboard sends nothing either.
        composeRule.onNode(emailField).performTextInput("   ")
        composeRule.onNode(passwordField).performTextInput(PASSWORD)
        composeRule.onAllNodes(entrarButton and isEnabled()).assertCountEquals(0)
        composeRule.onNode(passwordField).performImeAction()

        composeRule.onNode(emailField).performTextClearance()
        composeRule.onNode(emailField).performTextInput(EMAIL)
        composeRule.onNode(passwordField).performTextClearance()
        composeRule.onAllNodes(entrarButton and isEnabled()).assertCountEquals(0)
        composeRule.onNode(passwordField).performImeAction()

        composeRule.waitForIdle()
        assertTrue("no login request with an empty field", api.requestsTo("POST login/access-token").isEmpty())

        composeRule.onNode(passwordField).performTextInput(PASSWORD)
        composeRule.onAllNodes(entrarButton and isEnabled()).assertCountEquals(1)
    }

    @Test
    fun ab2_siLaSesionNoSePuedeGuardar_laEntradaMuestraUnErrorYLaAppNoSeCierra() {
        aead.failWrites = true
        startApp()

        login(EMAIL, PASSWORD)

        waitUntil("the generic error is shown") {
            composeRule.onAllNodes(loginErrorWith(GENERIC_ERROR), useUnmergedTree = true)
                .fetchSemanticsNodes().isNotEmpty()
        }
        assertTrue("the login request was answered", api.requestsTo("POST login/access-token").isNotEmpty())
        composeRule.onAllNodesWithTagUnmerged(PROFILE).assertCountEquals(0)
        composeRule.onAllNodes(entrarButton and isEnabled()).assertCountEquals(1)
        assertNull("no session saved", savedToken())
    }

    // --- AB-3 · row 4 -------------------------------------------------------------------------------------------

    @Test
    fun ab3_sinConsentimiento_muestraElTextoV1SinDatosYAlAceptarLlegaAlPerfil() {
        api.consentGranted = false
        startApp()

        login(NO_CONSENT_EMAIL, PASSWORD)

        waitForTag(CONSENT)
        waitUntil("the consent text from consent/text is shown") {
            composeRule.onAllNodes(hasText(CONSENT_TEXT, substring = true), useUnmergedTree = true)
                .fetchSemanticsNodes().isNotEmpty()
        }
        composeRule.onNode(hasText("Versión v1", substring = true), useUnmergedTree = true).assertExists()
        composeRule.onNode(hasText("Acepto") and hasClickAction()).assertExists()
        composeRule.onNode(cerrarSesionButton).assertExists()

        // No profile data while consent is missing.
        composeRule.onAllNodesWithTagUnmerged(PROFILE).assertCountEquals(0)
        composeRule.onAllNodes(hasText(PROFILE_MARKER, substring = true), useUnmergedTree = true).assertCountEquals(0)
        // A 403 CONSENT_REQUIRED does not end the session.
        assertEquals("the session is kept", TOKEN, savedToken())

        composeRule.onNode(hasText("Acepto") and hasClickAction()).performClick()

        waitUntil("consent is registered") { api.requestsTo("POST consent").isNotEmpty() }
        val grant = api.requestsTo("POST consent").single()
        val body = Json.parseToJsonElement(grant.body?.utf8().orEmpty()).jsonObject
        assertEquals("v1", body["version"]?.jsonPrimitive?.content)
        assertEquals("Bearer $TOKEN", grant.headers["Authorization"])

        waitForTag(PROFILE)
        composeRule.onAllNodesWithTagUnmerged(CONSENT).assertCountEquals(0)
    }

    @Test
    fun ab3_conOtraVersionDelTexto_muestraEsaVersionYRegistraEsa() {
        api.consentGranted = false
        api.consentVersion = "v2"
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
        startApp()

        waitForConsentText()
        composeRule.onNode(hasText("Versión v2", substring = true), useUnmergedTree = true).assertExists()
        composeRule.onAllNodes(hasText("Versión v1", substring = true), useUnmergedTree = true).assertCountEquals(0)

        composeRule.onNode(hasText("Acepto") and hasClickAction()).performClick()

        waitUntil("consent is registered") { api.requestsTo("POST consent").isNotEmpty() }
        val body = Json.parseToJsonElement(api.requestsTo("POST consent").single().body?.utf8().orEmpty()).jsonObject
        assertEquals("v2", body["version"]?.jsonPrimitive?.content)
        waitForTag(PROFILE)
    }

    @Test
    fun ab3_mientrasSeRegistra_aceptoMuestraEnviandoYCerrarSesionNoEstaDisponible() {
        api.consentGranted = false
        api.respond("POST consent") {
            api.grantConsent().newBuilder().headersDelay(1500, TimeUnit.MILLISECONDS).build()
        }
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
        startApp()
        waitForConsentText()

        composeRule.onNode(hasText("Acepto") and hasClickAction()).performClick()

        // D20: the screen shows it is sending, and neither «Acepto» nor «Cerrar sesión» can be used meanwhile.
        val sending = composeRule.onAllNodes(hasText("Enviando…") and hasClickAction()).fetchSemanticsNodes()
        assertTrue("«Acepto» reads «Enviando…» while the request is held", sending.isNotEmpty())
        composeRule.onAllNodes(hasText("Enviando…") and hasClickAction() and isEnabled()).assertCountEquals(0)
        composeRule.onAllNodes(hasText("Acepto") and hasClickAction() and isEnabled()).assertCountEquals(0)
        assertTrue(
            "«Cerrar sesión» is still shown",
            composeRule.onAllNodes(cerrarSesionButton).fetchSemanticsNodes().isNotEmpty(),
        )
        composeRule.onAllNodes(cerrarSesionButton and isEnabled()).assertCountEquals(0)

        waitForTag(PROFILE)
        assertEquals("one grant only", 1, api.requestsTo("POST consent").size)
        assertEquals("the session is kept", TOKEN, savedToken())
    }

    // --- AB-5 · row 6 -------------------------------------------------------------------------------------------

    @Test
    fun ab5_conTokenGuardado_elArranqueVaAlPerfilSinPasarPorLaEntrada() {
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }

        // Frame by frame from setContent (manual clock), so a login frame cannot slip between two samples.
        composeRule.mainClock.autoAdvance = false
        startApp()
        var frames = 0
        var loginFrames = 0
        val deadline = System.currentTimeMillis() + TIMEOUT_MS
        while (!isShown(PROFILE)) {
            if (isShown(LOGIN)) loginFrames++
            if (System.currentTimeMillis() > deadline) {
                throw AssertionError("no profile after $frames frames; requests: " +
                    api.requests.joinToString { FakeApi.routeOf(it) })
            }
            composeRule.mainClock.advanceTimeByFrame()
            frames++
        }
        composeRule.mainClock.autoAdvance = true

        assertEquals("frames showing the login screen on the way to the profile (of $frames)", 0, loginFrames)
        assertTrue("no login request", api.requestsTo("POST login/access-token").isEmpty())
        assertEquals(TOKEN, savedToken())
    }

    // --- AB-5 · row 7 -------------------------------------------------------------------------------------------

    @Test
    fun ab5_cerrarSesion_borraElTokenYVuelveALaEntrada() {
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
        startApp()
        waitForTag(PROFILE)

        composeRule.onNode(cerrarSesionButton).performClick()

        waitForTag(LOGIN)
        waitUntil("the token is cleared") { savedToken() == null }
        composeRule.onAllNodesWithTagUnmerged(PROFILE).assertCountEquals(0)
    }

    @Test
    fun ab5_un401DelPerfil_borraElTokenYVuelveALaEntrada() {
        api.respond("GET profile") { json(401, """{"detail":"Could not validate credentials"}""") }
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
        startApp()

        waitForTag(LOGIN)
        waitUntil("the token is cleared") { savedToken() == null }
        composeRule.onAllNodesWithTagUnmerged(PROFILE).assertCountEquals(0)
    }

    @Test
    fun ab5_un401EnCualquierPedido_comoElTextoDelConsentimiento_borraElTokenYVuelveALaEntrada() {
        api.consentGranted = false
        api.respond("GET consent/text") { json(401, """{"detail":"Could not validate credentials"}""") }
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
        startApp()

        waitForTag(LOGIN)
        waitUntil("the token is cleared") { savedToken() == null }
        assertTrue("the app did ask for consent/text", api.requestsTo("GET consent/text").isNotEmpty())
    }

    /** The real API answers an expired or invalid token with 403 «No se pudieron validar las credenciales». */
    @Test
    fun ab5_unTokenVencido_laApiResponde403YLaAppBorraElTokenYVuelveALaEntrada() {
        runBlocking<Unit> { container.sessionStore.save(EXPIRED_TOKEN) }
        startApp()

        waitForTag(LOGIN)
        waitUntil("the token is cleared") { savedToken() == null }
        composeRule.onAllNodesWithTagUnmerged(PROFILE).assertCountEquals(0)
        val profileRequest = api.requestsTo("GET profile").first()
        assertEquals("Bearer $EXPIRED_TOKEN", profileRequest.headers["Authorization"])
    }

    @Test
    fun ab5_un403DeCredencialesEnCualquierPedido_comoElTextoDelConsentimiento_borraElTokenYVuelveALaEntrada() {
        api.consentGranted = false
        api.respond("GET consent/text") { json(403, """{"detail":"$INVALID_CREDENTIALS"}""") }
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
        startApp()

        waitForTag(LOGIN)
        waitUntil("the token is cleared") { savedToken() == null }
        assertTrue("the app did ask for consent/text", api.requestsTo("GET consent/text").isNotEmpty())
    }

    @Test
    fun ab5_siLaSesionNoSePuedeBorrar_cerrarSesionNoCierraLaApp() {
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
        startApp()
        waitForTag(PROFILE)
        aead.failWrites = true

        composeRule.onNode(cerrarSesionButton).performClick()

        waitUntil("the sign-out was attempted") { aead.failedWrites > 0 }
        composeRule.waitForIdle()
        assertTrue("the app is still up, on the profile", isShown(PROFILE))
        assertEquals("the session could not be cleared", TOKEN, savedToken())
    }

    // --- AB-6 · row 8 (app flow; the store on its own is in SessionStoreEncryptionTest) ---------------------

    @Test
    fun ab6_trasEntrarYVerElPerfil_ningunArchivoTieneElTokenNiDatosDelPerfilEnClaro() {
        startApp()
        login(EMAIL, PASSWORD)
        waitForTag(PROFILE)
        waitUntil("the token is saved") { savedToken() == TOKEN }
        waitUntil("the profile was fetched") { api.requestsTo("GET profile").isNotEmpty() }
        composeRule.waitForIdle()

        val files = appFiles(context)
        assertTrue("the session is persisted to a file", files.any { it.length() > 0 })
        files.forEach { file ->
            val content = file.readBytes()
            assertFalse("token in clear in ${file.path}", content.containsSequence(TOKEN.toByteArray()))
            assertFalse("profile data in ${file.path}", content.containsSequence(PROFILE_MARKER.toByteArray()))
        }

        // Not merely unreadable (Base64 would pass the scan above): the file is the token sealed with the app's key,
        // bound to the file name, and another key does not open it.
        val sessionFile = context.dataStoreFile(SessionStore.DEFAULT_FILE_NAME)
        val sealed = sessionFile.readBytes()
        val associatedData = SessionStore.DEFAULT_FILE_NAME.encodeToByteArray()
        assertEquals("the app's AEAD opens the session file", TOKEN, aead.decrypt(sealed, associatedData).decodeToString())
        assertThrows(GeneralSecurityException::class.java) { TestAead.create().decrypt(sealed, associatedData) }
    }

    // --- AB-7 · row 9 -------------------------------------------------------------------------------------------

    @Test
    fun ab7_laApiSeDesconecta_muestraElMensajeYReintentarYConLaApiDeVueltaMuestraElPerfil() {
        api.respond("GET profile") { FakeApi.disconnect() }
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
        startApp()

        waitForTag(OFFLINE)
        composeRule.onNode(hasText(OFFLINE_MESSAGE), useUnmergedTree = true).assertExists()
        composeRule.onNode(reintentarButton).assertExists()
        assertEquals("the session is kept", TOKEN, savedToken())

        api.restore("GET profile")
        composeRule.onNode(reintentarButton).performClick()

        waitForTag(PROFILE)
        composeRule.onAllNodesWithTagUnmerged(OFFLINE).assertCountEquals(0)
        assertEquals("the session is kept", TOKEN, savedToken())
    }

    /** A gateway in front of a stopped API (502, 503, 504) is the same «sin conexión» as no answer at all. */
    @Test
    fun ab7_unaPuertaDeEnlaceSinApi_503_muestraSinConexionYReintentarSinPerderLaSesion() {
        api.respond("GET profile") { json(503, """{"detail":"Service Unavailable"}""") }
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
        startApp()

        waitForTag(OFFLINE)
        composeRule.onNode(hasText(OFFLINE_MESSAGE), useUnmergedTree = true).assertExists()
        composeRule.onNode(reintentarButton).assertExists()
        assertEquals("the session is kept", TOKEN, savedToken())
    }

    @Test
    fun ab7_laApiApagada_muestraElMensajeYReintentarSinPerderLaSesion() {
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
        // The container points at this server's port: closing it leaves nothing listening there.
        server.close()
        startApp()

        waitForTag(OFFLINE)
        composeRule.onNode(hasText(OFFLINE_MESSAGE), useUnmergedTree = true).assertExists()
        composeRule.onNode(reintentarButton).assertExists()
        composeRule.onAllNodesWithTagUnmerged(LOGIN).assertCountEquals(0)
        assertEquals("the session is kept", TOKEN, savedToken())
    }

    // --- helpers ------------------------------------------------------------------------------------------------

    private fun startApp() {
        composeRule.setContent { GlobalHealthApp(container) }
    }

    private fun login(email: String, password: String) {
        waitForTag(LOGIN)
        composeRule.onNode(emailField).performTextInput(email)
        composeRule.onNode(passwordField).performTextInput(password)
        composeRule.onNode(entrarButton).performClick()
    }

    private fun savedToken(): String? = runBlocking { container.sessionStore.token.first() }

    private fun isShown(tag: String): Boolean = composeRule.onAllNodesWithTagUnmerged(tag).fetchSemanticsNodes().isNotEmpty()

    private fun waitForConsentText() {
        waitForTag(CONSENT)
        waitUntil("the consent text from consent/text is shown") {
            composeRule.onAllNodes(hasText(CONSENT_TEXT, substring = true), useUnmergedTree = true)
                .fetchSemanticsNodes().isNotEmpty()
        }
    }

    private fun waitForTag(tag: String) {
        waitUntil("the screen '$tag' is shown") {
            composeRule.onAllNodesWithTagUnmerged(tag).fetchSemanticsNodes().isNotEmpty()
        }
    }

    private fun waitUntil(what: String, condition: () -> Boolean) {
        try {
            composeRule.waitUntil(TIMEOUT_MS, condition)
        } catch (e: Throwable) {
            throw AssertionError("Timed out after $TIMEOUT_MS ms waiting until $what; requests: " +
                api.requests.joinToString { FakeApi.routeOf(it) }, e)
        }
    }

    private fun androidx.compose.ui.test.junit4.ComposeContentTestRule.onAllNodesWithTagUnmerged(tag: String) =
        onAllNodes(hasTestTag(tag), useUnmergedTree = true)

    private fun loginErrorWith(text: String): SemanticsMatcher =
        hasText(text) and (hasTestTag(LOGIN_ERROR) or hasAnyAncestor(hasTestTag(LOGIN_ERROR)))

    companion object {
        private const val TIMEOUT_MS = 10_000L

        const val LOGIN = "login"
        const val LOGIN_ERROR = "login_error"
        const val CONSENT = "consent"
        const val PROFILE = "profile"
        const val OFFLINE = "offline"

        const val WRONG_CREDENTIALS = "Correo o contraseña incorrectos"
        const val OFFLINE_MESSAGE = "No pudimos conectar. Revisa tu conexión e intenta de nuevo."
        const val GENERIC_ERROR = "Algo salió mal. Intenta de nuevo."

        /** A token the API no longer accepts (expired, or signed with another key). */
        const val EXPIRED_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ2ZW5jaWRvIn0.token-vencido"

        val emailField = hasText("Correo electrónico") and hasSetTextAction()
        val passwordField = hasText("Contraseña") and hasSetTextAction()
        val entrarButton = hasText("Entrar") and hasClickAction()
        val loginButtonWhileSending = (hasText("Entrar") or hasText("Entrando…")) and hasClickAction()
        val reintentarButton = hasText("Reintentar") and hasClickAction()
        val cerrarSesionButton =
            (hasText("Cerrar sesión") or hasContentDescription("Cerrar sesión")) and hasClickAction()
    }
}
