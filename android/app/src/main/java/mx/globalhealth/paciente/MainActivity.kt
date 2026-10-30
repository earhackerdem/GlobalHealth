package mx.globalhealth.paciente

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import mx.globalhealth.paciente.ui.theme.GlobalHealthTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val container = (application as GlobalHealthApplication).container
        setContent {
            GlobalHealthTheme {
                GlobalHealthApp(container)
            }
        }
    }
}
