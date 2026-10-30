package mx.globalhealth.paciente.ui.theme

import android.content.Context
import android.view.ContextThemeWrapper
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.test.junit4.createComposeRule
import org.junit.Assert.assertEquals
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment
import org.robolectric.annotation.Config

/**
 * D22 everywhere the app paints: the Material 3 container roles (a filled `Card` uses `surfaceContainerHighest`) are
 * the D22 card colour, not the Material defaults, and the window behind Compose is the D22 background in light and
 * dark, so starting in dark mode does not flash white.
 */
@RunWith(RobolectricTestRunner::class)
class ThemeTest {

    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun d22_losContenedoresSonElColorDeTarjetaDeD22() {
        lateinit var light: ColorScheme
        lateinit var dark: ColorScheme
        composeRule.setContent {
            GlobalHealthTheme(darkTheme = false) { light = MaterialTheme.colorScheme }
            GlobalHealthTheme(darkTheme = true) { dark = MaterialTheme.colorScheme }
        }
        composeRule.waitForIdle()

        assertContainers("light", light, Color(0xFFFFFFFF))
        assertContainers("dark", dark, Color(0xFF172630))
    }

    @Test
    fun d22_laVentanaEnClaroTieneElFondoDeD22() {
        assertEquals(0xFFF0F4F5.toInt(), windowBackground())
    }

    @Test
    @Config(qualifiers = "night")
    fun d22_laVentanaEnOscuroTieneElFondoDeD22() {
        assertEquals(0xFF0F1A22.toInt(), windowBackground())
    }

    private fun assertContainers(mode: String, scheme: ColorScheme, card: Color) {
        mapOf(
            "surfaceContainerLowest" to scheme.surfaceContainerLowest,
            "surfaceContainerLow" to scheme.surfaceContainerLow,
            "surfaceContainer" to scheme.surfaceContainer,
            "surfaceContainerHigh" to scheme.surfaceContainerHigh,
            "surfaceContainerHighest" to scheme.surfaceContainerHighest,
        ).forEach { (role, color) -> assertEquals("$mode $role", card, color) }
    }

    /** The window background of the app's manifest theme (MainActivity sets none of its own). */
    private fun windowBackground(): Int {
        val context: Context = RuntimeEnvironment.getApplication()
        val themed = ContextThemeWrapper(context, context.applicationInfo.theme)
        val attrs = themed.obtainStyledAttributes(intArrayOf(android.R.attr.windowBackground))
        return try {
            attrs.getColor(0, 0)
        } finally {
            attrs.recycle()
        }
    }
}
