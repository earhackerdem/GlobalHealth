package mx.globalhealth.paciente.profile

import java.time.LocalDate
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import org.junit.Assert.assertEquals
import org.junit.Test

/**
 * Group 2 of android-base, AB-4 · design.md Test plan row 5, pure part: the presentation rules of
 * `profile/ProfileFormat.kt` (design.md, Interface contract → Reglas de presentación), the same as the web
 * (`perfil.tsx`, `history.ts` sectionStatus/hasHabits, `es-MX/profile.json`). Every function is pure and the age
 * takes `today: LocalDate`, so nothing here depends on the clock.
 */
class ProfileFormatTest {

    private val today = LocalDate.of(2026, 10, 29)

    // --- Fecha de nacimiento con la edad -------------------------------------------------------------------------

    @Test
    fun ab4_fechaDeNacimiento_conLaEdadAlDiaDeHoy() {
        assertEquals("15/03/1990 · 36 años", ProfileFormat.birthDate("1990-03-15", today))
    }

    @Test
    fun ab4_edad_laVisperaDelCumpleanosAunNoLoCumple() {
        assertEquals("15/03/1990 · 35 años", ProfileFormat.birthDate("1990-03-15", LocalDate.of(2026, 3, 14)))
    }

    @Test
    fun ab4_edad_elDiaDelCumpleanosYaLoCumple() {
        assertEquals("15/03/1990 · 36 años", ProfileFormat.birthDate("1990-03-15", LocalDate.of(2026, 3, 15)))
    }

    @Test
    fun ab4_fechaDeNacimientoSinRegistrar() {
        assertEquals(NOT_RECORDED, ProfileFormat.birthDate(null, today))
    }

    // --- Sexo ----------------------------------------------------------------------------------------------------

    @Test
    fun ab4_sexo_lasTresOpcionesDeLaWeb() {
        assertEquals("Mujer", ProfileFormat.sex("female"))
        assertEquals("Hombre", ProfileFormat.sex("male"))
        assertEquals("Prefiero no decir", ProfileFormat.sex("unspecified"))
    }

    @Test
    fun ab4_sexoSinRegistrar() {
        assertEquals(NOT_RECORDED, ProfileFormat.sex(null))
    }

    // --- Alergias ------------------------------------------------------------------------------------------------

    @Test
    fun ab4_alergias_elTextoTalCualOSinRegistrar() {
        assertEquals("Penicilina", ProfileFormat.allergies("Penicilina"))
        assertEquals(NOT_RECORDED, ProfileFormat.allergies(null))
        assertEquals(NOT_RECORDED, ProfileFormat.allergies(""))
    }

    // --- Peso y estatura -----------------------------------------------------------------------------------------

    @Test
    fun ab4_pesoYEstatura_conSuFecha() {
        assertEquals("72 kg · 12/10/2026", ProfileFormat.measurement(72.0, "kg", "2026-10-12"))
        assertEquals("165 cm · 12/10/2026", ProfileFormat.measurement(165.0, "cm", "2026-10-12"))
    }

    @Test
    fun ab4_medicionConDecimales_comoLaWeb() {
        assertEquals("72.5 kg · 12/10/2026", ProfileFormat.measurement(72.5, "kg", "2026-10-12"))
    }

    @Test
    fun ab4_medicionSinRegistrar() {
        assertEquals(NOT_RECORDED, ProfileFormat.measurement(null, "kg", null))
    }

    // --- Trabajo -------------------------------------------------------------------------------------------------

    @Test
    fun ab4_trabajo_choferRotativoExpuestoARuidoFuerte() {
        assertEquals(
            "Chofer de transporte · rotativo · expuesto a ruido fuerte",
            ProfileFormat.workSummary(
                status = "employed",
                occupation = "Chofer de transporte",
                longestJob = null,
                exposures = listOf("loud_noise"),
                shift = "rotating",
            ),
        )
    }

    @Test
    fun ab4_trabajo_jubiladoConSuTrabajoMasLargo() {
        assertEquals(
            "Jubilado o pensionado · antes: Minero",
            ProfileFormat.workSummary(
                status = "retired",
                occupation = null,
                longestJob = "Minero",
                exposures = emptyList<String>(),
                shift = null,
            ),
        )
    }

    @Test
    fun ab4_trabajo_variasExposicionesSeparadasPorComaEnMinusculas() {
        assertEquals(
            "Albañil · de día · expuesto a polvo, químicos o solventes",
            ProfileFormat.workSummary(
                status = "employed",
                occupation = "Albañil",
                longestJob = null,
                exposures = listOf("dust", "chemicals"),
                shift = "day",
            ),
        )
    }

    @Test
    fun ab4_trabajoSinRegistrar() {
        assertEquals(
            NOT_RECORDED,
            ProfileFormat.workSummary(
                status = null,
                occupation = null,
                longestJob = null,
                exposures = emptyList<String>(),
                shift = null,
            ),
        )
    }

    // --- Estado de las secciones del historial -------------------------------------------------------------------

    @Test
    fun ab4_estadoDeSeccion_unRegistroYVariosRegistros() {
        assertEquals("1 registro", ProfileFormat.sectionStatus(count = 1, none = false))
        assertEquals("2 registros", ProfileFormat.sectionStatus(count = 2, none = false))
    }

    @Test
    fun ab4_estadoDeSeccion_ningunaCuandoLaMarcoYNoHayRegistros() {
        assertEquals("Ninguna", ProfileFormat.sectionStatus(count = 0, none = true))
    }

    @Test
    fun ab4_estadoDeSeccion_losRegistrosGananAlNinguna() {
        assertEquals("1 registro", ProfileFormat.sectionStatus(count = 1, none = true))
    }

    @Test
    fun ab4_estadoDeSeccion_sinLlenar() {
        assertEquals("Sin llenar", ProfileFormat.sectionStatus(count = 0, none = false))
    }

    // --- Hábitos -------------------------------------------------------------------------------------------------

    @Test
    fun ab4_habitos_conDatosSiAlgunValorDePrimerNivelNoEsNull() {
        val habits = buildJsonObject {
            put("smoking", JsonNull)
            put("alcohol", buildJsonObject { put("status", "never") })
        }
        assertEquals("Con datos", ProfileFormat.habitsStatus(habits))
    }

    @Test
    fun ab4_habitos_sinLlenarSiTodoEsNullOVacioOSinRespuesta() {
        val allNull = buildJsonObject {
            put("smoking", JsonNull)
            put("alcohol", JsonNull)
            put("physical_activity", JsonNull)
        }
        assertEquals("Sin llenar", ProfileFormat.habitsStatus(allNull))
        assertEquals("Sin llenar", ProfileFormat.habitsStatus(JsonObject(emptyMap())))
        assertEquals("Sin llenar", ProfileFormat.habitsStatus(null))
    }

    // --- Antecedentes familiares ---------------------------------------------------------------------------------

    @Test
    fun ab4_antecedentesFamiliares_cuantosRegistradosOSinRegistros() {
        assertEquals("3 registrados", ProfileFormat.familyHistory(3))
        assertEquals("Sin registros", ProfileFormat.familyHistory(0))
    }

    private companion object {
        const val NOT_RECORDED = "Sin registrar"
    }
}
