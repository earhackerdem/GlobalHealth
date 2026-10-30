package mx.globalhealth.paciente.profile

import android.content.Context
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.assertCountEquals
import androidx.compose.ui.test.hasAnyAncestor
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasContentDescription
import androidx.compose.ui.test.hasSetTextAction
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.performClick
import java.time.LocalDate
import java.time.Period
import java.time.ZoneId
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import mockwebserver3.MockWebServer
import mx.globalhealth.paciente.AppContainer
import mx.globalhealth.paciente.GlobalHealthApp
import mx.globalhealth.paciente.testing.FakeApi
import mx.globalhealth.paciente.testing.FakeApi.Companion.TOKEN
import mx.globalhealth.paciente.testing.TestAead
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config

/**
 * Group 2 of android-base: «Mi perfil médico» in read-only (spec delta AB-4 and AB-7 on the profile; design.md Test
 * plan rows 5 and 9). The app runs from its root against MockWebServer with a saved session, so it opens straight on
 * the `profile` screen.
 *
 * The screen is tall: a tall window keeps every row composed even if the screen uses a lazy list.
 *
 * Contract additions of this group (the tester's, listed in the report): each of the six history rows carries the
 * `testTag` `history_<key>` (`chronic`, `past`, `surgeries`, `fractures`, `transfusions`, `habits`), the same keys
 * as the web's `history-card-<key>`, so a test can tell which state belongs to which section.
 */
@RunWith(RobolectricTestRunner::class)
@Config(qualifiers = "w411dp-h3000dp")
class ProfileScreenTest {

    @get:Rule
    val composeRule = createComposeRule()

    private lateinit var server: MockWebServer
    private lateinit var api: FakeApi
    private lateinit var context: Context
    private lateinit var container: AppContainer

    @Before
    fun setUp() {
        context = RuntimeEnvironment.getApplication()
        api = FakeApi()
        server = MockWebServer()
        server.dispatcher = api
        server.start()
        container = AppContainer(context, server.url("/api/v1/").toString(), TestAead.create())
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
    }

    @After
    fun tearDown() {
        runCatching { server.close() }
    }

    // --- AB-4 · row 5 -------------------------------------------------------------------------------------------

    /**
     * The age on screen comes from the real clock (the screen passes today in America/Mexico_City to
     * `ProfileFormat`, whose own test fixes 2026-10-29). Here the expected age is derived independently from the
     * same zone, before and after the wait, so the test holds on any date and across midnight.
     */
    @Test
    fun ab4_perfilConDatos_muestraLosDatosBasicosElTrabajoYLosAntecedentes() {
        api.serveAb4Profile()
        val ageBefore = ageToday()
        startApp()

        waitForText("Penicilina")
        val ageAfter = ageToday()

        val birthDates = setOf(ageBefore, ageAfter).map { "15/03/1990 · $it años" }
        assertTrue(
            "the birth date with the age (one of $birthDates) is shown",
            birthDates.any { exists(hasText(it, substring = true)) },
        )
        assertShown("Mujer")
        assertShown("Penicilina")
        assertShown("72 kg · 12/10/2026")
        assertShown("165 cm · 12/10/2026")
        assertShown("Chofer de transporte · rotativo · expuesto a ruido fuerte")
        assertShown("3 registrados")

        listOf("Datos básicos", "Antecedentes familiares", "Tu historial").forEach { assertShown(it) }
        listOf(
            "Fecha de nacimiento",
            "Sexo",
            "Alergias a medicamentos",
            "Peso",
            "Estatura",
            "Trabajo",
        ).forEach { assertShown(it) }
    }

    @Test
    fun ab4_perfilConDatos_lasSeisSeccionesConSuEstado() {
        api.serveAb4Profile()
        startApp()

        waitForText("Penicilina")

        assertSection("chronic", "Enfermedades crónicas", "Sin llenar")
        assertSection("past", "Enfermedades pasadas e infecciosas", "2 registros")
        assertSection("surgeries", "Cirugías y hospitalizaciones", "Sin llenar")
        assertSection("fractures", "Fracturas y lesiones", "Sin llenar")
        assertSection("transfusions", "Transfusiones y grupo sanguíneo", "Ninguna")
        assertSection("habits", "Hábitos", "Sin llenar")
    }

    @Test
    fun ab4_perfil_esSoloLecturaSinNingunControlDeEdicion() {
        api.serveAb4Profile()
        startApp()

        waitForText("Penicilina")

        composeRule.onAllNodes(hasSetTextAction(), useUnmergedTree = true).assertCountEquals(0)
        listOf("Editar", "Agregar", "Guardar", "Registrar medición").forEach { word ->
            composeRule.onAllNodes(
                hasText(word, substring = true, ignoreCase = true) or
                    hasContentDescription(word, substring = true, ignoreCase = true),
                useUnmergedTree = true,
            ).assertCountEquals(0)
        }
        // The only action on the profile is «Cerrar sesión».
        val actions = composeRule.onAllNodes(hasClickAction() and !cerrarSesion).fetchSemanticsNodes()
        assertEquals("clickable nodes other than «Cerrar sesión»: $actions", 0, actions.size)
    }

    @Test
    fun ab4_perfilSinDatos_cadaDatoBasicoDiceSinRegistrarYNadaEstaLleno() {
        api.serveEmptyProfile()
        startApp()

        waitForText("Sin registros")

        // Birth date, sex, allergies, weight, height and work.
        composeRule.onAllNodes(hasText("Sin registrar", substring = true), useUnmergedTree = true)
            .assertCountEquals(6)
        SECTIONS.forEach { (key, name) -> assertSection(key, name, "Sin llenar") }
    }

    // --- AB-7 · row 9 on the profile ----------------------------------------------------------------------------

    @Test
    fun ab7_unaParteDelPerfilNoResponde_muestraSinConexionYReintentarTraeElPerfilCompleto() {
        api.serveAb4Profile()
        api.respond("GET profile/history") { FakeApi.disconnect() }
        startApp()

        waitForTag(OFFLINE)
        composeRule.onNode(hasText(OFFLINE_MESSAGE), useUnmergedTree = true).assertExists()
        assertEquals("the session is kept", TOKEN, savedToken())

        api.respond("GET profile/history") { FakeApi.json(200, FakeApi.AB4_HISTORY) }
        composeRule.onNode(reintentar).performClick()

        waitUntil("the offline state is gone and the profile is shown") {
            composeRule.onAllNodes(hasTestTag(OFFLINE), useUnmergedTree = true).fetchSemanticsNodes().isEmpty() &&
                exists(hasText("Penicilina", substring = true))
        }
        assertShown("Chofer de transporte · rotativo · expuesto a ruido fuerte")
        assertShown("3 registrados")
        assertSection("past", "Enfermedades pasadas e infecciosas", "2 registros")
        assertSection("transfusions", "Transfusiones y grupo sanguíneo", "Ninguna")
        assertSection("habits", "Hábitos", "Sin llenar")
        assertEquals("the session is kept", TOKEN, savedToken())
    }

    // --- helpers ------------------------------------------------------------------------------------------------

    private fun startApp() {
        composeRule.setContent { GlobalHealthApp(container) }
    }

    private fun ageToday(): Int =
        Period.between(LocalDate.of(1990, 3, 15), LocalDate.now(ZoneId.of("America/Mexico_City"))).years

    private fun savedToken(): String? = runBlocking { container.sessionStore.token.first() }

    private fun exists(matcher: SemanticsMatcher): Boolean =
        composeRule.onAllNodes(matcher and hasAnyAncestor(hasTestTag(PROFILE)), useUnmergedTree = true)
            .fetchSemanticsNodes().isNotEmpty()

    private fun assertShown(text: String) {
        assertTrue("«$text» is shown on the profile", exists(hasText(text, substring = true)))
    }

    private fun assertSection(key: String, name: String, status: String) {
        val tag = "history_$key"
        val inRow = hasAnyAncestor(hasTestTag(tag)) or hasTestTag(tag)
        assertTrue(
            "the row '$tag' is on the profile",
            composeRule.onAllNodes(hasTestTag(tag) and hasAnyAncestor(hasTestTag(PROFILE)), useUnmergedTree = true)
                .fetchSemanticsNodes().isNotEmpty(),
        )
        assertTrue(
            "the row '$tag' names «$name»",
            composeRule.onAllNodes(hasText(name, substring = true) and inRow, useUnmergedTree = true)
                .fetchSemanticsNodes().isNotEmpty(),
        )
        assertTrue(
            "the row '$tag' says «$status»",
            composeRule.onAllNodes(hasText(status, substring = true) and inRow, useUnmergedTree = true)
                .fetchSemanticsNodes().isNotEmpty(),
        )
    }

    private fun waitForText(text: String) = waitUntil("«$text» is shown on the profile") { exists(hasText(text, substring = true)) }

    private fun waitForTag(tag: String) = waitUntil("the screen '$tag' is shown") {
        composeRule.onAllNodes(hasTestTag(tag), useUnmergedTree = true).fetchSemanticsNodes().isNotEmpty()
    }

    private fun waitUntil(what: String, condition: () -> Boolean) {
        try {
            composeRule.waitUntil(TIMEOUT_MS, condition)
        } catch (e: Throwable) {
            throw AssertionError("Timed out after $TIMEOUT_MS ms waiting until $what; requests: " +
                api.requests.joinToString { FakeApi.routeOf(it) }, e)
        }
    }

    private companion object {
        const val TIMEOUT_MS = 10_000L
        const val PROFILE = "profile"
        const val OFFLINE = "offline"
        const val OFFLINE_MESSAGE = "No pudimos conectar. Revisa tu conexión e intenta de nuevo."

        val SECTIONS = listOf(
            "chronic" to "Enfermedades crónicas",
            "past" to "Enfermedades pasadas e infecciosas",
            "surgeries" to "Cirugías y hospitalizaciones",
            "fractures" to "Fracturas y lesiones",
            "transfusions" to "Transfusiones y grupo sanguíneo",
            "habits" to "Hábitos",
        )

        val reintentar = hasText("Reintentar") and hasClickAction()
        val cerrarSesion = hasText("Cerrar sesión") or hasContentDescription("Cerrar sesión")
    }
}
