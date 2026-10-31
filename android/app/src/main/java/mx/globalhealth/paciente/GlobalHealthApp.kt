package mx.globalhealth.paciente

import androidx.compose.animation.EnterTransition
import androidx.compose.animation.ExitTransition
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavDestination.Companion.hasRoute
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import kotlinx.coroutines.flow.distinctUntilChanged
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.launch
import kotlinx.serialization.Serializable
import mx.globalhealth.paciente.auth.LoginScreen
import mx.globalhealth.paciente.auth.LoginViewModel
import mx.globalhealth.paciente.consent.ConsentScreen
import mx.globalhealth.paciente.consent.ConsentViewModel
import mx.globalhealth.paciente.profile.ProfileScreen
import mx.globalhealth.paciente.profile.ProfileViewModel

// Type-safe routes; navigation looks their serializers up by reflection, so they are not private.
@Serializable
internal data object LoginRoute

@Serializable
internal data object ConsentRoute

@Serializable
internal data object ProfileRoute

private enum class Session { Unknown, SignedOut, SignedIn }

/**
 * The root of the app. The saved session decides the screen (AB-5): without a token, the login; with one, the
 * profile, which may send to the consent (AB-3). Whatever clears the token («Cerrar sesión», or a 401 or a 403 other
 * than `CONSENT_REQUIRED` seen by the interceptor on any request) brings back the login, and saving one (a successful
 * login) leaves it.
 *
 * Until the session file has been read nothing is shown, so a saved session never flashes the login screen.
 */
@Composable
fun GlobalHealthApp(container: AppContainer) {
    val sessionFlow = remember(container) {
        container.sessionStore.token
            .map { if (it == null) Session.SignedOut else Session.SignedIn }
            .distinctUntilChanged()
    }
    val session by sessionFlow.collectAsStateWithLifecycle(Session.Unknown)

    Surface(Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        if (session != Session.Unknown) {
            AppNavHost(container, signedIn = session == Session.SignedIn)
        }
    }
}

@Composable
private fun AppNavHost(container: AppContainer, signedIn: Boolean) {
    val navController = rememberNavController()
    // Read once: later session changes navigate instead of rebuilding the graph.
    val startDestination: Any = remember { if (signedIn) ProfileRoute else LoginRoute }
    val scope = rememberCoroutineScope()
    // A session file that cannot be written leaves the patient where they are instead of crashing the app.
    val signOut: () -> Unit = { scope.launch { runCatching { container.sessionStore.clear() } } }

    LaunchedEffect(signedIn) {
        val onLogin = navController.currentDestination?.hasRoute(LoginRoute::class) == true
        when {
            !signedIn && !onLogin -> navController.navigateClearing(LoginRoute)
            signedIn && onLogin -> navController.navigateClearing(ProfileRoute)
        }
    }

    // No transitions: the screens are states of the session, not a stack, and an exiting screen must not linger.
    NavHost(
        navController = navController,
        startDestination = startDestination,
        enterTransition = { EnterTransition.None },
        exitTransition = { ExitTransition.None },
    ) {
        composable<LoginRoute> {
            LoginScreen(viewModel { LoginViewModel(container.api, container.sessionStore) })
        }
        composable<ConsentRoute> {
            ConsentScreen(
                viewModel = viewModel { ConsentViewModel(container.api) },
                onAccepted = { navController.navigateClearing(ProfileRoute) },
                onSignOut = signOut,
            )
        }
        composable<ProfileRoute> {
            ProfileScreen(
                viewModel = viewModel { ProfileViewModel(container.api) },
                onConsentRequired = { navController.navigateClearing(ConsentRoute) },
                onSignOut = signOut,
            )
        }
    }
}

/** Replaces the whole back stack: «Atrás» from any of these screens leaves the app instead of going back to another. */
private fun NavHostController.navigateClearing(route: Any) {
    navigate(route) {
        popUpTo(graph.id) { inclusive = true }
        launchSingleTop = true
    }
}
