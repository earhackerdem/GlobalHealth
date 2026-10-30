package mx.globalhealth.paciente.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.LiveRegionMode
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.liveRegion
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import mx.globalhealth.paciente.R

/** Visible height of every button: the 48 dp touch target of the accessibility rules, not just its hit area. */
val MinTouchTarget = 48.dp

const val OFFLINE_TAG = "offline"

/** The main action of a screen, full width. */
@Composable
fun PrimaryButton(text: String, onClick: () -> Unit, modifier: Modifier = Modifier, enabled: Boolean = true) {
    Button(
        onClick = onClick,
        enabled = enabled,
        modifier = modifier.fillMaxWidth().heightIn(min = MinTouchTarget),
    ) {
        Text(text)
    }
}

/** «Cerrar sesión», as a text button (top bar of the profile, bottom of the consent). */
@Composable
fun SignOutButton(onClick: () -> Unit, modifier: Modifier = Modifier) {
    TextButton(onClick = onClick, modifier = modifier.heightIn(min = MinTouchTarget)) {
        Text(stringResource(R.string.sign_out))
    }
}

@Composable
fun LoadingContent(modifier: Modifier = Modifier) {
    val loading = stringResource(R.string.loading)
    Box(modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        CircularProgressIndicator(Modifier.semantics { contentDescription = loading })
    }
}

/**
 * A message with «Reintentar». For a connection failure ([offline] = true) it carries the `offline` tag and the
 * AB-7 text; the session is kept either way.
 */
@Composable
fun RetryContent(offline: Boolean, onRetry: () -> Unit, modifier: Modifier = Modifier) {
    val message = stringResource(if (offline) R.string.offline_message else R.string.error_generic)
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(24.dp)
            .then(if (offline) Modifier.testTag(OFFLINE_TAG) else Modifier),
        verticalArrangement = Arrangement.spacedBy(16.dp, Alignment.CenterVertically),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = message,
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            modifier = Modifier.semantics { liveRegion = LiveRegionMode.Polite },
        )
        PrimaryButton(text = stringResource(R.string.retry), onClick = onRetry)
    }
}
