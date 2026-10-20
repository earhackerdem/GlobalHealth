import type { TFunction } from "i18next"

import type {
  ChronicHistoryEntry,
  HistoryEntriesPublic,
  PatientProfilePublic,
  WhenStage,
} from "@/client"

/**
 * The sections with their own screen (keys as in perfil.tsx): chronic (US-18
 * Story B) and the four event sections of Story A.
 */
export const HISTORY_SECTIONS = [
  "chronic",
  "past",
  "surgeries",
  "fractures",
  "transfusions",
] as const

export type HistorySection = (typeof HISTORY_SECTIONS)[number]

/** Every card on "Mi perfil médico", in display order (habits still read-only). */
export const HISTORY_CARD_KEYS = [
  "chronic",
  "past",
  "surgeries",
  "fractures",
  "transfusions",
  "habits",
] as const

export type HistoryCardKey = (typeof HISTORY_CARD_KEYS)[number]

/** es-MX URL segment of each section: /perfil/<slug>. */
export const SECTION_SLUGS: Record<HistorySection, string> = {
  chronic: "cronicas",
  past: "pasadas",
  surgeries: "cirugias",
  fractures: "fracturas",
  transfusions: "transfusiones",
}

export function sectionFromSlug(slug: string): HistorySection | null {
  const match = HISTORY_SECTIONS.find((s) => SECTION_SLUGS[s] === slug)
  return match ?? null
}

export function isHistorySection(key: string): key is HistorySection {
  return (HISTORY_SECTIONS as readonly string[]).includes(key)
}

export type HistoryEntry = HistoryEntriesPublic["data"][number]
export type ChronicEntry = Extract<HistoryEntry, { section: "chronic" }>
/** One "cuándo" answer; the same union as Story A's `when` and B's since/until. */
export type When = NonNullable<ChronicHistoryEntry["since"]>
export type Stage = WhenStage["value"]

/**
 * Chronic conditions catalog (Story B), in display order; the sensitive ones
 * go under their own subtitle "Salud mental y adicciones", then "Otra".
 */
export const CHRONIC_CONDITIONS = [
  "type2_diabetes",
  "hypertension",
  "asthma",
  "hypothyroidism",
  "high_cholesterol",
  "copd",
  "arthritis",
  "epilepsy",
] as const satisfies readonly NonNullable<ChronicEntry["condition"]>[]

export const CHRONIC_SENSITIVE_CONDITIONS = [
  "depression",
  "anxiety",
  "bipolar_disorder",
  "substance_use",
] as const satisfies readonly NonNullable<ChronicEntry["condition"]>[]

/**
 * "Sensible" checked by default for the mental health and addictions
 * conditions (Decision 2, same set as the API's CHRONIC_SENSITIVE_BY_DEFAULT).
 */
export function sensitiveByDefault(condition: string | null | undefined) {
  return (CHRONIC_SENSITIVE_CONDITIONS as readonly string[]).includes(
    condition ?? "",
  )
}

/** A chronic entry's name: the catalog label, or the patient's own text for "Otra". */
export function chronicTitle(entry: ChronicEntry, t: TFunction): string {
  if (entry.condition === "other" && entry.other_text) return entry.other_text
  return entry.condition
    ? t(`profile:history.options.chronicCondition.${entry.condition}`)
    : ""
}

export const STAGES: readonly Stage[] = [
  "before_primary",
  "primary",
  "secondary",
  "high_school",
]

/**
 * Typical ages per school stage in Mexico, [first, last] inclusive.
 * [ASSUMPTION] of the domain (design.md, Decision 4): they only estimate the
 * approximate year on screen, so correcting them never touches stored data.
 * The ONE place these ranges live.
 */
export const STAGE_AGE_RANGES: Record<Stage, readonly [number, number]> = {
  before_primary: [0, 5],
  primary: [6, 11],
  secondary: [12, 14],
  high_school: [15, 17],
}

export const BLOOD_TYPES = [
  "A+",
  "A-",
  "B+",
  "B-",
  "AB+",
  "AB-",
  "O+",
  "O-",
  "unknown",
] as const satisfies readonly NonNullable<PatientProfilePublic["blood_type"]>[]

export type BloodType = (typeof BLOOD_TYPES)[number]

/** Birth year from an ISO "aaaa-mm-dd" string (no `new Date(iso)`, see format.ts). */
function birthYearOf(birthDate: string | null | undefined): number | null {
  if (!birthDate) return null
  const year = Number(birthDate.split("-")[0])
  return Number.isFinite(year) ? year : null
}

/**
 * Approximate calendar years for an age or a stage, computed at render time
 * from the birth date (Decision 4). Null without a birth date, for a year
 * (already exact) and for "No recuerdo".
 */
export function approxYears(
  when: When | null | undefined,
  birthDate: string | null | undefined,
): readonly [number, number] | null {
  const birthYear = birthYearOf(birthDate)
  if (!when || birthYear === null) return null
  if (when.kind === "age")
    return [birthYear + when.value, birthYear + when.value]
  if (when.kind === "stage") {
    const [from, to] = STAGE_AGE_RANGES[when.value]
    return [birthYear + from, birthYear + to]
  }
  return null
}

/** "1997" or "1996–2001" (en dash). */
export function formatYearRange([from, to]: readonly [number, number]): string {
  return from === to ? `${from}` : `${from}–${to}`
}

/** i18n key family per wording: "a los…" (when), "desde los…" (since), "hasta los…" (until). */
const WHEN_SUMMARY_KEYS = {
  when: "profile:history.when.summary",
  since: "profile:history.when.summarySince",
  until: "profile:history.when.summaryUntil",
} as const

/**
 * "a los 7 años (≈1997)" · "en la primaria (≈1996–2001)" · "en 2015" · "no
 * recuerda cuándo"; with `wording` "since" / "until" the chronic forms "desde
 * los 31 años (≈2021)" · "hasta la primaria (≈…)" · "desde 2015".
 */
export function whenSummary(
  when: When,
  birthDate: string | null | undefined,
  t: TFunction,
  wording: keyof typeof WHEN_SUMMARY_KEYS = "when",
): string {
  const base = WHEN_SUMMARY_KEYS[wording]
  let text: string
  if (when.kind === "age") {
    text = t(`${base}.age`, { value: when.value })
  } else if (when.kind === "stage") {
    text = t(`${base}.stages.${when.value}`)
  } else if (when.kind === "year") {
    return t(`${base}.year`, { value: when.value })
  } else {
    return t(`${base}.unknown`)
  }
  const range = approxYears(when, birthDate)
  return range
    ? t("profile:history.when.summary.approx", {
        text,
        range: formatYearRange(range),
      })
    : text
}

/**
 * What the WhenField holds while editing: the number box (in age or year mode)
 * or one chip (a stage or "No recuerdo"). Typing clears the chip and choosing
 * a chip clears the box, so at most one answer is ever sent.
 */
export type WhenDraft = {
  mode: "age" | "year"
  text: string
  choice: Stage | "unknown" | null
}

export const EMPTY_WHEN: WhenDraft = { mode: "age", text: "", choice: null }

export function whenToDraft(when: When | null | undefined): WhenDraft {
  if (!when) return EMPTY_WHEN
  if (when.kind === "age")
    return { mode: "age", text: `${when.value}`, choice: null }
  if (when.kind === "year") {
    return { mode: "year", text: `${when.value}`, choice: null }
  }
  if (when.kind === "stage") return { ...EMPTY_WHEN, choice: when.value }
  return { ...EMPTY_WHEN, choice: "unknown" }
}

/** Draft → `When` for the API; `"invalid"` when the box holds a non-number. */
export function draftToWhen(draft: WhenDraft): When | null | "invalid" {
  if (draft.choice === "unknown") return { kind: "unknown" }
  if (draft.choice) return { kind: "stage", value: draft.choice }
  const text = draft.text.trim()
  if (!text) return null
  if (!/^\d+$/.test(text)) return "invalid"
  return { kind: draft.mode, value: Number(text) }
}

/** Card / section status: "Sin llenar" · "Ninguna" · "1 registro" · "N registros". */
export function sectionStatus(
  count: number,
  none: boolean,
  t: TFunction,
): string {
  if (count > 0) return t("profile:history.status.count", { count })
  if (none) return t("profile:history.status.none")
  return t("profile:history.status.empty")
}
