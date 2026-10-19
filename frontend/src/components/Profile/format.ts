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

/** Today as a LOCAL "aaaa-mm-dd" string (toISOString would be UTC). */
export function localTodayIso(): string {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, "0")
  const day = String(now.getDate()).padStart(2, "0")
  return `${now.getFullYear()}-${month}-${day}`
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
