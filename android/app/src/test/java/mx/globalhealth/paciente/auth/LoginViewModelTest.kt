package mx.globalhealth.paciente.auth

import java.util.concurrent.atomic.AtomicInteger
import kotlinx.coroutines.CompletableDeferred
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.setMain
import kotlinx.serialization.json.JsonObject
import mx.globalhealth.paciente.core.net.ConsentGrant
import mx.globalhealth.paciente.core.net.ConsentRecord
import mx.globalhealth.paciente.core.net.ConsentText
import mx.globalhealth.paciente.core.net.FamilyHistoryEntries
import mx.globalhealth.paciente.core.net.GlobalHealthApi
import mx.globalhealth.paciente.core.net.HistoryEntries
import mx.globalhealth.paciente.core.net.Profile
import mx.globalhealth.paciente.core.net.Token
import mx.globalhealth.paciente.core.net.Work
import mx.globalhealth.paciente.core.session.SessionStore
import mx.globalhealth.paciente.testing.FakeApi.Companion.EMAIL
import mx.globalhealth.paciente.testing.FakeApi.Companion.PASSWORD
import mx.globalhealth.paciente.testing.TestAead
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.RuntimeEnvironment

/** D20 in the ViewModel itself: a second «Entrar» while the first is in flight sends nothing. */
@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(RobolectricTestRunner::class)
class LoginViewModelTest {

    private val api = HeldLoginApi()

    @Before
    fun setUp() {
        Dispatchers.setMain(UnconfinedTestDispatcher())
    }

    @After
    fun tearDown() {
        api.answer.cancel()
        Dispatchers.resetMain()
    }

    @Test
    fun d20_dosEntrarSeguidos_mandanUnSoloPedido() {
        val store = SessionStore(RuntimeEnvironment.getApplication(), TestAead.create(), "session_login_vm.pb")
        val viewModel = LoginViewModel(api, store)
        viewModel.onEmailChange(EMAIL)
        viewModel.onPasswordChange(PASSWORD)

        viewModel.submit()
        viewModel.submit()

        assertTrue("sending", viewModel.state.value.sending)
        assertEquals("login requests", 1, api.logins.get())
    }

    /** Holds every login until [answer] completes; the other routes are not used by the login screen. */
    private class HeldLoginApi : GlobalHealthApi {
        val logins = AtomicInteger()
        val answer = CompletableDeferred<Token>()

        override suspend fun login(email: String, password: String): Token {
            logins.incrementAndGet()
            return answer.await()
        }

        override suspend fun consentText(): ConsentText = unused()
        override suspend fun grantConsent(grant: ConsentGrant): ConsentRecord = unused()
        override suspend fun profile(): Profile = unused()
        override suspend fun work(): Work = unused()
        override suspend fun history(): HistoryEntries = unused()
        override suspend fun habits(): JsonObject = unused()
        override suspend fun familyHistory(): FamilyHistoryEntries = unused()

        private fun unused(): Nothing = throw AssertionError("not used by the login screen")
    }
}
