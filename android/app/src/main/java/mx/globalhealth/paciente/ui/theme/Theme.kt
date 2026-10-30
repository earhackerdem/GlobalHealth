package mx.globalhealth.paciente.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

// Palette B · Azul clínico (D22), the same tokens as frontend/src/index.css.
private val Light = lightColorScheme(
    primary = Color(0xFF005EB8),
    onPrimary = Color(0xFFFFFFFF),
    background = Color(0xFFF0F4F5),
    onBackground = Color(0xFF212B32),
    surface = Color(0xFFFFFFFF),
    onSurface = Color(0xFF212B32),
    surfaceVariant = Color(0xFFE8EDEE),
    onSurfaceVariant = Color(0xFF4C6272),
    outline = Color(0xFF4C6272),
    outlineVariant = Color(0xFFD8DDE0),
    error = Color(0xFFD5281B),
    onError = Color(0xFFFFFFFF),
)

private val Dark = darkColorScheme(
    primary = Color(0xFF5AA9F0),
    onPrimary = Color(0xFF0B1A26),
    background = Color(0xFF0F1A22),
    onBackground = Color(0xFFE8EEF1),
    surface = Color(0xFF172630),
    onSurface = Color(0xFFE8EEF1),
    surfaceVariant = Color(0xFF223644),
    onSurfaceVariant = Color(0xFFA3B4BF),
    outline = Color(0xFF7A92A1),
    outlineVariant = Color(0xFF2A3B47),
    error = Color(0xFFFF8A80),
    onError = Color(0xFF0B1A26),
)

@Composable
fun GlobalHealthTheme(darkTheme: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = if (darkTheme) Dark else Light, content = content)
}
