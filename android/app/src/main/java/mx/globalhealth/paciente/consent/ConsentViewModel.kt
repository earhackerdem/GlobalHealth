package mx.globalhealth.paciente.consent

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import mx.globalhealth.paciente.core.net.ApiResult
import mx.globalhealth.paciente.core.net.ConsentGrant
import mx.globalhealth.paciente.core.net.GlobalHealthApi
import mx.globalhealth.paciente.core.net.apiCall

sealed interface ConsentUiState {
    data object Loading : ConsentUiState
    data class Ready(val version: String, val text: String, val sending: Boolean = false) : ConsentUiState
    data class Error(val offline: Boolean) : ConsentUiState
    data object Accepted : ConsentUiState
}

/**
 * Shows the current consent text and records the grant with the version that was shown (AB-3). A 401 needs nothing
 * here: the interceptor clears the session and the app root goes back to the login screen.
 */
class ConsentViewModel(private val api: GlobalHealthApi) : ViewModel() {

    private val _state = MutableStateFlow<ConsentUiState>(ConsentUiState.Loading)
    val state: StateFlow<ConsentUiState> = _state.asStateFlow()

    init {
        load()
    }

    fun load() {
        _state.value = ConsentUiState.Loading
        viewModelScope.launch {
            when (val result = apiCall { api.consentText() }) {
                is ApiResult.Ok -> _state.value = ConsentUiState.Ready(result.value.version, result.value.text)
                else -> showError(result)
            }
        }
    }

    fun accept() {
        val ready = _state.value as? ConsentUiState.Ready ?: return
        if (ready.sending) return
        _state.value = ready.copy(sending = true)
        viewModelScope.launch {
            when (val result = apiCall { api.grantConsent(ConsentGrant(ready.version)) }) {
                is ApiResult.Ok -> _state.value = ConsentUiState.Accepted
                else -> showError(result)
            }
        }
    }

    private fun showError(result: ApiResult<*>) {
        if (result == ApiResult.Unauthorized) return
        _state.value = ConsentUiState.Error(offline = result == ApiResult.Offline)
    }
}
