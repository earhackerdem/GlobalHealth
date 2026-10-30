package mx.globalhealth.paciente.profile

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import mx.globalhealth.paciente.R
import mx.globalhealth.paciente.ui.components.LoadingContent
import mx.globalhealth.paciente.ui.components.RetryContent
import mx.globalhealth.paciente.ui.components.SignOutButton

const val PROFILE_TAG = "profile"

/**
 * «Mi perfil médico» with «Cerrar sesión» in its top bar. The `profile` tag marks the loaded profile only, so while
 * loading, on error or before consent no node claims to be the profile. Its content (basic data and the sections) is
 * group 2 of android-base.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel,
    onConsentRequired: () -> Unit,
    onSignOut: () -> Unit,
    modifier: Modifier = Modifier,
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    LaunchedEffect(state) {
        if (state == ProfileUiState.ConsentRequired) onConsentRequired()
    }

    Scaffold(
        modifier = modifier,
        topBar = {
            TopAppBar(
                title = { Text(stringResource(R.string.profile_title)) },
                actions = { SignOutButton(onClick = onSignOut) },
            )
        },
    ) { padding ->
        when (val current = state) {
            ProfileUiState.Loading, ProfileUiState.ConsentRequired -> LoadingContent(Modifier.padding(padding))
            is ProfileUiState.Error ->
                RetryContent(offline = current.offline, onRetry = viewModel::load, modifier = Modifier.padding(padding))
            is ProfileUiState.Loaded -> Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .testTag(PROFILE_TAG)
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                Text(
                    text = stringResource(R.string.profile_read_only),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}
