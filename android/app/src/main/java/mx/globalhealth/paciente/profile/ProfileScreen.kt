package mx.globalhealth.paciente.profile

import androidx.annotation.StringRes
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedCard
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.semantics.heading
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import java.time.LocalDate
import mx.globalhealth.paciente.R
import mx.globalhealth.paciente.ui.components.LoadingContent
import mx.globalhealth.paciente.ui.components.RetryContent
import mx.globalhealth.paciente.ui.components.SignOutButton

const val PROFILE_TAG = "profile"

/** The six history rows, in the web's order; each carries the `testTag` `history_<key>` (`history-card-<key>`). */
private val HISTORY_SECTIONS = listOf(
    "chronic" to R.string.profile_section_chronic,
    "past" to R.string.profile_section_past,
    "surgeries" to R.string.profile_section_surgeries,
    "fractures" to R.string.profile_section_fractures,
    "transfusions" to R.string.profile_section_transfusions,
)
private const val HABITS_KEY = "habits"

/**
 * «Mi perfil médico» in read-only (AB-4), with «Cerrar sesión» in its top bar as the only control. The `profile` tag
 * marks the loaded profile only, so while loading, on error or before consent no node claims to be the profile.
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
            is ProfileUiState.Loaded -> ProfileContent(current.medicalProfile, Modifier.padding(padding))
        }
    }
}

@Composable
private fun ProfileContent(medicalProfile: MedicalProfile, modifier: Modifier = Modifier) {
    // Today in America/Mexico_City, for the age (the API's «today»).
    val today: LocalDate = remember { ProfileFormat.today() }
    val (profile, work, history, habits, familyHistory) = medicalProfile

    Column(
        modifier = modifier
            .fillMaxSize()
            .testTag(PROFILE_TAG)
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        ProfileCard(R.string.profile_basic_heading) {
            Field(R.string.profile_birth_date, ProfileFormat.birthDate(profile.birthDate, today))
            Field(R.string.profile_sex, ProfileFormat.sex(profile.sex))
            Field(R.string.profile_allergies, ProfileFormat.allergies(profile.allergies))
            Field(
                R.string.profile_weight,
                ProfileFormat.measurement(profile.latestWeight?.value, "kg", profile.latestWeight?.measuredOn),
            )
            Field(
                R.string.profile_height,
                ProfileFormat.measurement(profile.latestHeight?.value, "cm", profile.latestHeight?.measuredOn),
            )
            Field(
                R.string.profile_work,
                ProfileFormat.workSummary(
                    status = work.status,
                    occupation = work.occupation,
                    longestJob = work.longestJob,
                    exposures = work.exposures,
                    shift = work.shift,
                ),
            )
        }

        ProfileCard(R.string.profile_family_heading) {
            Text(
                text = ProfileFormat.familyHistory(familyHistory.data.size),
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        ProfileCard(R.string.profile_history_heading) {
            HISTORY_SECTIONS.forEach { (key, name) ->
                val count = history.data.count { it.section == key }
                val none = key in profile.sectionsNone
                SectionRow(
                    key = key,
                    name = name,
                    status = ProfileFormat.sectionStatus(count = count, none = none),
                    filled = count > 0 || none,
                )
            }
            SectionRow(
                key = HABITS_KEY,
                name = R.string.profile_section_habits,
                status = ProfileFormat.habitsStatus(habits),
                filled = ProfileFormat.hasHabits(habits),
            )
        }

        Text(
            text = stringResource(R.string.profile_read_only),
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
private fun ProfileCard(@StringRes title: Int, content: @Composable ColumnScope.() -> Unit) {
    OutlinedCard(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(
                text = stringResource(title),
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.semantics { heading() },
            )
            content()
        }
    }
}

/** A label over its value; read together by TalkBack. */
@Composable
private fun Field(@StringRes label: Int, value: String) {
    Column(
        modifier = Modifier.fillMaxWidth().semantics(mergeDescendants = true) {},
        verticalArrangement = Arrangement.spacedBy(2.dp),
    ) {
        Text(
            text = stringResource(label),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        Text(text = value, style = MaterialTheme.typography.bodyMedium)
    }
}

/** A history section with its status in a pill, as the web's card badge (filled: secondary; empty: outline). */
@Composable
private fun SectionRow(key: String, @StringRes name: Int, status: String, filled: Boolean) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .testTag("history_$key")
            .semantics(mergeDescendants = true) {},
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text(
            text = stringResource(name),
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.weight(1f),
        )
        Surface(
            shape = RoundedCornerShape(percent = 50),
            color = if (filled) MaterialTheme.colorScheme.surfaceVariant else MaterialTheme.colorScheme.surface,
            contentColor = MaterialTheme.colorScheme.onSurface,
            border = if (filled) null else BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        ) {
            Text(
                text = status,
                style = MaterialTheme.typography.labelMedium,
                modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp),
            )
        }
    }
}
