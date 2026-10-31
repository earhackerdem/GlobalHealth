package mx.globalhealth.paciente.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlin.coroutines.cancellation.CancellationException
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import mx.globalhealth.paciente.core.net.ApiResult
import mx.globalhealth.paciente.core.net.GlobalHealthApi
import mx.globalhealth.paciente.core.net.apiCall
import mx.globalhealth.paciente.core.session.SessionStore

data class LoginUiState(
    val email: String = "",
    val password: String = "",
    val sending: Boolean = false,
    val error: LoginError? = null,
) {
    /** «Entrar» is available only with both fields filled and nothing in flight (D20). */
    val canSubmit: Boolean get() = !sending && email.trim().isNotEmpty() && password.isNotEmpty()
}

sealed interface LoginError {
    /** The API's own message, shown as is (AB-2). */
    data class Api(val message: String) : LoginError
    data object Offline : LoginError
    data object Generic : LoginError
}

/**
 * Signs in with email and password (AB-2). On success it only saves the token: the app root observes the session and
 * moves on to the profile, so this screen never navigates by itself.
 */
class LoginViewModel(
    private val api: GlobalHealthApi,
    private val sessionStore: SessionStore,
) : ViewModel() {

    private val _state = MutableStateFlow(LoginUiState())
    val state: StateFlow<LoginUiState> = _state.asStateFlow()

    fun onEmailChange(email: String) = _state.update { it.copy(email = email) }

    fun onPasswordChange(password: String) = _state.update { it.copy(password = password) }

    fun submit() {
        val current = _state.value
        // D20: one request at a time, and none with an empty field (the keyboard's «Listo» also lands here).
        if (!current.canSubmit) return
        _state.update { it.copy(sending = true, error = null) }
        viewModelScope.launch {
            when (val result = apiCall { api.login(current.email.trim(), current.password) }) {
                // Stays "sending" until the root leaves this screen. A session that cannot be saved is an error
                // on this screen, not a crash.
                is ApiResult.Ok -> runCatching { sessionStore.save(result.value.accessToken) }.onFailure {
                    if (it is CancellationException) throw it
                    fail(LoginError.Generic)
                }
                is ApiResult.Rejected -> fail(result.detail?.let(LoginError::Api) ?: LoginError.Generic)
                ApiResult.Offline -> fail(LoginError.Offline)
                else -> fail(LoginError.Generic)
            }
        }
    }

    private fun fail(error: LoginError) = _state.update { it.copy(sending = false, error = error) }
}
