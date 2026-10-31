package mx.globalhealth.paciente.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.async
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.serialization.json.JsonObject
import mx.globalhealth.paciente.core.net.ApiResult
import mx.globalhealth.paciente.core.net.FamilyHistoryEntries
import mx.globalhealth.paciente.core.net.GlobalHealthApi
import mx.globalhealth.paciente.core.net.HistoryEntries
import mx.globalhealth.paciente.core.net.Profile
import mx.globalhealth.paciente.core.net.Work
import mx.globalhealth.paciente.core.net.apiCall

/** Everything «Mi perfil médico» shows, from its five endpoints. In memory only. */
data class MedicalProfile(
    val profile: Profile,
    val work: Work,
    val history: HistoryEntries,
    val habits: JsonObject,
    val familyHistory: FamilyHistoryEntries,
)

sealed interface ProfileUiState {
    data object Loading : ProfileUiState
    data class Loaded(val medicalProfile: MedicalProfile) : ProfileUiState
    data class Error(val offline: Boolean) : ProfileUiState
    data object ConsentRequired : ProfileUiState
}

/**
 * Loads `GET profile`, `profile/work`, `profile/history`, `profile/habits` and `profile/family-history` in parallel and
 * keeps them in memory only (design.md, Decision 6). The profile is shown only when all five answer: a 403
 * `CONSENT_REQUIRED` sends the patient to the consent screen (AB-3); a connection failure on any of them shows
 * «Reintentar» and keeps the session (AB-7); a 401, or a 403 that ends the session, is handled by the interceptor and
 * the app root (AB-5).
 */
class ProfileViewModel(private val api: GlobalHealthApi) : ViewModel() {

    private val _state = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val state: StateFlow<ProfileUiState> = _state.asStateFlow()

    private var loading: Job? = null

    init {
        load()
    }

    fun load() {
        loading?.cancel()
        _state.value = ProfileUiState.Loading
        loading = viewModelScope.launch {
            val profile = async { apiCall { api.profile() } }
            val work = async { apiCall { api.work() } }
            val history = async { apiCall { api.history() } }
            val habits = async { apiCall { api.habits() } }
            val familyHistory = async { apiCall { api.familyHistory() } }
            val results = listOf(profile, work, history, habits, familyHistory).map { it.await() }

            val loaded = results.all { it is ApiResult.Ok }
            _state.value = when {
                loaded -> ProfileUiState.Loaded(
                    MedicalProfile(
                        profile = profile.await().value(),
                        work = work.await().value(),
                        history = history.await().value(),
                        habits = habits.await().value(),
                        familyHistory = familyHistory.await().value(),
                    ),
                )
                ApiResult.Unauthorized in results -> return@launch
                ApiResult.ConsentRequired in results -> ProfileUiState.ConsentRequired
                ApiResult.Offline in results -> ProfileUiState.Error(offline = true)
                else -> ProfileUiState.Error(offline = false)
            }
        }
    }

    private fun <T> ApiResult<T>.value(): T = (this as ApiResult.Ok<T>).value
}
