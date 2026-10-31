/**
 * Date helpers for the medical profile. They work on the ISO "aaaa-mm-dd"
 * strings the API returns, WITHOUT going through `new Date(iso)`: parsing an
 * ISO date lands on UTC midnight and shifts a day back in negative-offset
 * timezones (es-MX included).
 */

/** "aaaa-mm-dd" → "dd/mm/aaaa" (es-MX display format). */
export function formatDateMx(isoDate: string): string {
  const [year, month, day] = isoDate.split("-")
  return `${day}/${month}/${year}`
}

/**
 * Today in America/Mexico_City as "aaaa-mm-dd", whatever the device's
 * timezone: the API's "today" for the history checks (profile.py MEXICO_CITY),
 * so the form never blocks what the server accepts, nor the reverse.
 */
export function mexicoCityTodayIso(now: Date = new Date()): string {
  // en-CA formats as aaaa-mm-dd.
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Mexico_City",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(now)
}

/** Age (completed years) as of today for an ISO "aaaa-mm-dd" birth date. */
export function ageFrom(isoDate: string): number {
  const [year, month, day] = isoDate.split("-").map(Number)
  const today = new Date()
  let age = today.getFullYear() - year
  const beforeBirthday =
    today.getMonth() + 1 < month ||
    (today.getMonth() + 1 === month && today.getDate() < day)
  if (beforeBirthday) {
    age -= 1
  }
  return age
}
