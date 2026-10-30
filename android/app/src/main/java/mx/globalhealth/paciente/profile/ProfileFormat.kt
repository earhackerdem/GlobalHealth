package mx.globalhealth.paciente.profile

import java.math.BigDecimal
import java.time.LocalDate
import java.time.Period
import java.time.ZoneId
import java.time.format.DateTimeFormatter
import java.util.Locale
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject

/**
 * The presentation rules of «Mi perfil médico» (design.md, Interface contract → Reglas de presentación), the same as
 * the web: `perfil.tsx` (rows and `workSummary`), `history.ts` (`sectionStatus`, `hasHabits`) and `format.ts`
 * (dates and age). Pure functions without a `Context`, so the es-MX texts live here, mirrored from
 * `frontend/src/locales/es-MX/profile.json`; the age takes `today` so nothing depends on the clock.
 */
object ProfileFormat {

    /** The zone of the API's «today» (profile.py `MEXICO_CITY`); the screen passes [today] from it. */
    val MEXICO_CITY: ZoneId = ZoneId.of("America/Mexico_City")

    // --- es-MX texts (profile.json) -----------------------------------------------------------------------------

    const val NOT_RECORDED = "Sin registrar"
    const val NO_ENTRIES = "Sin registros"
    private const val SEPARATOR = " · "
    private const val AGE = "%d años"
    private const val FAMILY_COUNT = "%d registrados"
    private const val WORK_BEFORE = "antes: %s"
    private const val WORK_EXPOSED_TO = "expuesto a %s"
    private const val STATUS_EMPTY = "Sin llenar"
    private const val STATUS_NONE = "Ninguna"
    private const val STATUS_COUNT_ONE = "%d registro"
    private const val STATUS_COUNT_MANY = "%d registros"
    private const val HABITS_FILLED = "Con datos"

    private val SEX = mapOf(
        "female" to "Mujer",
        "male" to "Hombre",
        "unspecified" to "Prefiero no decir",
    )

    private val WORK_STATUS = mapOf(
        "employed" to "Trabajo",
        "looking" to "Busco trabajo",
        "retired" to "Jubilado o pensionado",
        "homemaker" to "Hogar",
        "student" to "Estudio",
        "unable_health" to "No puedo trabajar por mi salud",
    )

    private val WORK_SHIFT = mapOf(
        "day" to "De día",
        "night" to "De noche",
        "rotating" to "Rotativo",
    )

    private val WORK_EXPOSURES = mapOf(
        "dust" to "Polvo",
        "chemicals" to "Químicos o solventes",
        "loud_noise" to "Ruido fuerte",
    )

    private val ES_MX: Locale = Locale.forLanguageTag("es-MX")
    private val DATE_MX: DateTimeFormatter = DateTimeFormatter.ofPattern("dd/MM/yyyy")

    // --- Rules --------------------------------------------------------------------------------------------------

    /** Today in America/Mexico_City, what the screen passes to [birthDate]. */
    fun today(): LocalDate = LocalDate.now(MEXICO_CITY)

    /** `1990-03-15` → «15/03/1990 · 36 años», the completed years as of [today]; null → «Sin registrar». */
    fun birthDate(isoDate: String?, today: LocalDate): String {
        val date = parseDate(isoDate) ?: return NOT_RECORDED
        val age = Period.between(date, today).years
        return date.format(DATE_MX) + SEPARATOR + AGE.fill(age)
    }

    fun sex(sex: String?): String = sex?.let { SEX[it] } ?: NOT_RECORDED

    /** The text as typed, or «Sin registrar» when empty. */
    fun allergies(allergies: String?): String = allergies?.takeIf { it.isNotEmpty() } ?: NOT_RECORDED

    /** «72 kg · 12/10/2026»: the number as the web prints it (72.0 → «72», 72.5 → «72.5»). */
    fun measurement(value: Double?, unit: String, measuredOn: String?): String {
        if (value == null) return NOT_RECORDED
        val number = BigDecimal(value.toString()).stripTrailingZeros().toPlainString()
        val date = parseDate(measuredOn)?.format(DATE_MX)
        return listOfNotNull("$number $unit", date).joinToString(SEPARATOR)
    }

    /**
     * The «Trabajo» row (`perfil.tsx` `workSummary`): the occupation, or the status label without it · the shift in
     * lowercase · «antes: » + the longest job · «expuesto a » + the exposures in lowercase, joined with «, ». No
     * verdict.
     */
    fun workSummary(
        status: String?,
        occupation: String?,
        longestJob: String?,
        exposures: List<String>,
        shift: String?,
    ): String {
        val exposed = exposures.mapNotNull { WORK_EXPOSURES[it]?.lowercase(ES_MX) }
        val parts = listOf(
            occupation?.takeIf { it.isNotEmpty() } ?: status?.let { WORK_STATUS[it] },
            shift?.let { WORK_SHIFT[it]?.lowercase(ES_MX) },
            longestJob?.takeIf { it.isNotEmpty() }?.let { WORK_BEFORE.fill(it) },
            exposed.takeIf { it.isNotEmpty() }?.let { WORK_EXPOSED_TO.fill(it.joinToString(", ")) },
        )
        return parts.filterNot { it.isNullOrEmpty() }.joinToString(SEPARATOR).ifEmpty { NOT_RECORDED }
    }

    /** A history section (`history.ts` `sectionStatus`): its entries win over «Ninguna», else «Sin llenar». */
    fun sectionStatus(count: Int, none: Boolean): String = when {
        count == 1 -> STATUS_COUNT_ONE.fill(count)
        count > 1 -> STATUS_COUNT_MANY.fill(count)
        none -> STATUS_NONE
        else -> STATUS_EMPTY
    }

    /** Habits (`history.ts` `hasHabits`): «Con datos» when any top-level answer is not null. Never a score. */
    fun habitsStatus(habits: JsonObject?): String = if (hasHabits(habits)) HABITS_FILLED else STATUS_EMPTY

    fun hasHabits(habits: JsonObject?): Boolean = habits != null && habits.values.any { it != JsonNull }

    /** Family history: «N registrados», or «Sin registros». */
    fun familyHistory(count: Int): String = if (count > 0) FAMILY_COUNT.fill(count) else NO_ENTRIES

    /** Fills a `%d`/`%s` text with ASCII digits whatever the device locale. */
    private fun String.fill(vararg args: Any): String = String.format(Locale.ROOT, this, *args)

    private fun parseDate(isoDate: String?): LocalDate? =
        isoDate?.takeIf { it.isNotEmpty() }?.let { runCatching { LocalDate.parse(it.take(ISO_DATE_LENGTH)) }.getOrNull() }

    private const val ISO_DATE_LENGTH = 10
}
