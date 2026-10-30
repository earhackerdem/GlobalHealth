package mx.globalhealth.paciente

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import mx.globalhealth.paciente.ui.theme.GlobalHealthTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            GlobalHealthTheme {
                Surface(Modifier.fillMaxSize()) {
                    // Scaffold only (android-base task 0.2); groups 1 and 2 replace this with the real navigation.
                    Box(contentAlignment = Alignment.Center) { Text("GlobalHealth") }
                }
            }
        }
    }
}
