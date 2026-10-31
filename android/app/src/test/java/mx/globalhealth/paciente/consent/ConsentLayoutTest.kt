package mx.globalhealth.paciente.consent

import android.content.Context
import androidx.compose.ui.test.SemanticsMatcher
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.hasClickAction
import androidx.compose.ui.test.hasTestTag
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.test.performScrollTo
import kotlinx.coroutines.runBlocking
import mockwebserver3.MockWebServer
import mx.globalhealth.paciente.AppContainer
import mx.globalhealth.paciente.GlobalHealthApp
import mx.globalhealth.paciente.testing.FakeApi
import mx.globalhealth.paciente.testing.FakeApi.Companion.TOKEN
import mx.globalhealth.paciente.testing.TestAead
import org.junit.After
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/**
 * AB-3 on a phone held sideways with the largest font (200 %): the consent text must be readable before «Acepto»,
 * however little height is left. A phone of 915 × 412 dp in landscape, like the S26 Ultra. Native graphics, so text
 * is measured as on a phone (the default fake one gives every line the same tiny size).
 */
@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(qualifiers = "w915dp-h412dp-land", fontScale = 2.0f)
class ConsentLayoutTest {

    @get:Rule
    val composeRule = createComposeRule()

    private lateinit var server: MockWebServer
    private lateinit var api: FakeApi
    private lateinit var container: AppContainer

    @Before
    fun setUp() {
        val context: Context = RuntimeEnvironment.getApplication()
        api = FakeApi(consentGranted = false)
        server = MockWebServer()
        server.dispatcher = api
        server.start()
        api.respond("GET consent/text") { FakeApi.json(200, """{"version":"v1","text":"$LONG_TEXT"}""") }
        container = AppContainer(context, server.url("/api/v1/").toString(), TestAead.create())
        runBlocking<Unit> { container.sessionStore.save(TOKEN) }
    }

    @After
    fun tearDown() {
        runCatching { server.close() }
    }

    @Test
    fun ab3_horizontalConFuenteGrande_elTextoSePuedeLeer() {
        composeRule.setContent { GlobalHealthApp(container) }
        val text = hasText(LONG_TEXT.take(40), substring = true)
        composeRule.waitUntil(TIMEOUT_MS) {
            composeRule.onAllNodes(text, useUnmergedTree = true).fetchSemanticsNodes().isNotEmpty()
        }
        val windowHeight = composeRule.onRoot().fetchSemanticsNode().size.height

        composeRule.onNode(hasText("Versión v1", substring = true), useUnmergedTree = true).performScrollTo()
        assertReadable(hasText("Versión v1", substring = true), windowHeight)
        composeRule.onNode(text, useUnmergedTree = true).performScrollTo()
        assertReadable(text, windowHeight)
        composeRule.onNode(hasText("Acepto") and hasClickAction()).performScrollTo().assertIsDisplayed()
        composeRule.onNode(hasTestTag("consent")).assertExists()
    }

    /**
     * Scrolled to, the node is all on screen, or (when taller than the window) it fills at least half the window: not
     * a sliver of a card squeezed between the intro and the buttons.
     */
    private fun assertReadable(matcher: SemanticsMatcher, windowHeight: Int) {
        val node = composeRule.onNode(matcher, useUnmergedTree = true).fetchSemanticsNode()
        val visible = node.boundsInRoot.height
        val needed = minOf(node.size.height.toFloat(), windowHeight / 2f)
        assertTrue(
            "${matcher.description}: $visible px visible of ${node.size.height} px (window $windowHeight px)",
            visible >= needed - 1f,
        )
    }

    private companion object {
        const val TIMEOUT_MS = 10_000L

        /** As long as the real v1 text (`backend/app/core/consent_text.py`), which needs scrolling sideways. */
        val LONG_TEXT = "Consentimiento expreso de prueba para la app de Android. " +
            "Al aceptar, otorgas tu consentimiento expreso para que esta aplicación almacene y procese los datos " +
            "de salud que tú mismo captures (notas, diagnósticos, estudios y recordatorios) con el único fin de " +
            "mostrártelos y ayudarte a gestionarlos. Tus datos se guardan cifrados, no se comparten con terceros " +
            "sin tu autorización y puedes solicitar su eliminación cuando quieras. Este texto es de prueba " +
            "y tiene el largo del texto vigente."
    }
}
