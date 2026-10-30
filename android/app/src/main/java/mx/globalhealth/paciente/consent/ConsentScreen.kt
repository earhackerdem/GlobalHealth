package mx.globalhealth.paciente.consent

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import mx.globalhealth.paciente.R
import mx.globalhealth.paciente.ui.components.LoadingContent
import mx.globalhealth.paciente.ui.components.PrimaryButton
import mx.globalhealth.paciente.ui.components.RetryContent
import mx.globalhealth.paciente.ui.components.SignOutButton

const val CONSENT_TAG = "consent"

/** Consentimiento (AB-3): the text of `consent/text` with its version, «Acepto» and «Cerrar sesión». No profile data. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ConsentScreen(
    viewModel: ConsentViewModel,
    onAccepted: () -> Unit,
    onSignOut: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    LaunchedEffect(state) {
        if (state == ConsentUiState.Accepted) onAccepted()
    }

    Scaffold(
        modifier = modifier.testTag(CONSENT_TAG),
        topBar = { TopAppBar(title = { Text(stringResource(R.string.consent_title)) }) },
    ) { padding ->
        when (val current = state) {
            ConsentUiState.Loading, ConsentUiState.Accepted -> LoadingContent(Modifier.padding(padding))
            is ConsentUiState.Error -> Column(Modifier.padding(padding)) {
                RetryContent(offline = current.offline, onRetry = viewModel::load, modifier = Modifier.weight(1f))
                SignOutButton(onClick = onSignOut, modifier = Modifier.align(Alignment.CenterHorizontally))
            }
            is ConsentUiState.Ready -> Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text(stringResource(R.string.consent_intro), style = MaterialTheme.typography.bodyLarge)
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f, fill = false),
                ) {
                    Column(
                        modifier = Modifier
                            .verticalScroll(rememberScrollState())
                            .padding(12.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp),
                    ) {
                        Text(
                            text = stringResource(R.string.consent_version, current.version),
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Bold,
                        )
                        Text(current.text, style = MaterialTheme.typography.bodyMedium)
                    }
                }
                PrimaryButton(
                    text = stringResource(R.string.consent_accept),
                    onClick = viewModel::accept,
                    enabled = !current.sending,
                )
                SignOutButton(onClick = onSignOut, modifier = Modifier.align(Alignment.CenterHorizontally))
            }
        }
    }
}
