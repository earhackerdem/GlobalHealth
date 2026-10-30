package mx.globalhealth.paciente.profile

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import mx.globalhealth.paciente.core.net.ApiResult
import mx.globalhealth.paciente.core.net.GlobalHealthApi
import mx.globalhealth.paciente.core.net.Profile
import mx.globalhealth.paciente.core.net.apiCall

sealed interface ProfileUiState {
    data object Loading : ProfileUiState
    data class Loaded(val profile: Profile) : ProfileUiState
    data class Error(val offline: Boolean) : ProfileUiState
    data object ConsentRequired : ProfileUiState
}

/**
 * Loads `GET profile` and keeps it in memory only (design.md, Decision 6). A 403 `CONSENT_REQUIRED` sends the
 * patient to the consent screen (AB-3); a connection failure shows «Reintentar» and keeps the session (AB-7); a 401
 * is handled by the interceptor and the app root (AB-5).
 */
class ProfileViewModel(private val api: GlobalHealthApi) : ViewModel() {

    private val _state = MutableStateFlow<ProfileUiState>(ProfileUiState.Loading)
    val state: StateFlow<ProfileUiState> = _state.asStateFlow()

    init {
        load()
    }

    fun load() {
        _state.value = ProfileUiState.Loading
        viewModelScope.launch {
            when (val result = apiCall { api.profile() }) {
                is ApiResult.Ok -> _state.value = ProfileUiState.Loaded(result.value)
                ApiResult.ConsentRequired -> _state.value = ProfileUiState.ConsentRequired
                ApiResult.Unauthorized -> Unit
                ApiResult.Offline -> _state.value = ProfileUiState.Error(offline = true)
                else -> _state.value = ProfileUiState.Error(offline = false)
            }
        }
    }
}
