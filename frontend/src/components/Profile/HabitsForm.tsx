import {
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from "@tanstack/react-query"
import { useBlocker, useNavigate } from "@tanstack/react-router"
import { AxiosError } from "axios"
import type { TFunction } from "i18next"
import { Loader2 } from "lucide-react"
import {
  type FormEvent,
  type ReactNode,
  useCallback,
  useEffect,
  useId,
  useRef,
  useState,
} from "react"
import { useTranslation } from "react-i18next"

import {
  type AlcoholHabit,
  type Habits,
  ProfileService,
  type SecondhandSmoke,
  type TobaccoHabit,
  type VapingHabit,
} from "@/client"
import {
  zAlcoholHabit,
  zSecondhandSmoke,
  zTobaccoHabit,
  zVapingHabit,
  zWoodSmokeHabit,
} from "@/client/zod.gen"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import ChipGroup, { ChipMultiGroup } from "./ChipGroup"
import { mexicoCityTodayIso } from "./format"
import { ageToday } from "./history"
import { getHabitsQueryOptions, getProfileQueryOptions } from "./queries"

type AlcoholStatus = AlcoholHabit["status"]
type SmokeStatus = TobaccoHabit["status"]
type Frequency = NonNullable<AlcoholHabit["frequency"]>
type TypicalDrinks = NonNullable<AlcoholHabit["typical_drinks"]>
type SixOrMore = NonNullable<AlcoholHabit["six_or_more"]>
type VapingFrequency = NonNullable<VapingHabit["frequency"]>
type Place = NonNullable<SecondhandSmoke["places"]>[number]
/** "No me expongo": the exclusive chip of "¿Dónde?", sent as `exposed: false`. */
type PlaceChoice = Place | "none"

const ALCOHOL_STATUSES: readonly AlcoholStatus[] = ["never", "quit", "current"]
const SMOKE_STATUSES: readonly SmokeStatus[] = ["never", "former", "current"]
const FREQUENCIES: readonly Frequency[] = [
  "monthly_or_less",
  "two_to_four_monthly",
  "two_to_three_weekly",
  "four_plus_weekly",
]
const TYPICAL_DRINKS: readonly TypicalDrinks[] = [
  "one_two",
  "three_four",
  "five_six",
  "seven_nine",
  "ten_plus",
]
const SIX_OR_MORE: readonly SixOrMore[] = [
  "never",
  "less_than_monthly",
  "monthly",
  "weekly",
  "daily",
]
const VAPING_FREQUENCIES: readonly VapingFrequency[] = ["daily", "some_days"]
const PLACES: readonly Place[] = ["home", "work_school", "other"]
const YES_NO = ["yes", "no"] as const

/** What the screen holds while editing; numbers stay text until sent. */
type Draft = {
  alcoholStatus: AlcoholStatus | null
  alcoholStartAge: string
  alcoholQuitAge: string
  frequency: Frequency | null
  typicalDrinks: TypicalDrinks | null
  sixOrMore: SixOrMore | null
  mostlyWeekends: boolean | null
  tobaccoStatus: SmokeStatus | null
  cigarettes: string
  tobaccoStartAge: string
  tobaccoQuitAge: string
  vapingStatus: SmokeStatus | null
  vapingFrequency: VapingFrequency | null
  vapingDays: string
  vapingStartAge: string
  vapingQuitAge: string
  places: PlaceChoice[]
  daysPerWeek: string
  woodStatus: SmokeStatus | null
  woodStartAge: string
  woodQuitAge: string
  woodHours: string
}

/** The draft entries that hold a number box's text. */
type NumberDraftKey = {
  [K in keyof Draft]: Draft[K] extends string ? K : never
}[keyof Draft]

const numberText = (value: number | null | undefined) =>
  value == null ? "" : `${value}`

function draftFrom(habits: Habits): Draft {
  const {
    alcohol,
    tobacco,
    vaping,
    secondhand_smoke: smoke,
    wood_smoke,
  } = habits
  let places: PlaceChoice[] = []
  if (smoke) places = smoke.exposed ? [...(smoke.places ?? [])] : ["none"]
  return {
    alcoholStatus: alcohol?.status ?? null,
    alcoholStartAge: numberText(alcohol?.start_age),
    alcoholQuitAge: numberText(alcohol?.quit_age),
    frequency: alcohol?.frequency ?? null,
    typicalDrinks: alcohol?.typical_drinks ?? null,
    sixOrMore: alcohol?.six_or_more ?? null,
    mostlyWeekends: alcohol?.mostly_weekends ?? null,
    tobaccoStatus: tobacco?.status ?? null,
    cigarettes: numberText(tobacco?.cigarettes_per_day),
    tobaccoStartAge: numberText(tobacco?.start_age),
    tobaccoQuitAge: numberText(tobacco?.quit_age),
    vapingStatus: vaping?.status ?? null,
    vapingFrequency: vaping?.frequency ?? null,
    vapingDays: numberText(vaping?.days_last_30),
    vapingStartAge: numberText(vaping?.start_age),
    vapingQuitAge: numberText(vaping?.quit_age),
    places,
    daysPerWeek: numberText(smoke?.days_per_week),
    woodStatus: wood_smoke?.status ?? null,
    woodStartAge: numberText(wood_smoke?.start_age),
    woodQuitAge: numberText(wood_smoke?.quit_age),
    woodHours: numberText(wood_smoke?.hours_per_day),
  }
}

/**
 * The number boxes, keyed like the API's 422 `loc` ("<block>.<field>") so a
 * client error and a server one land on the same box. Each scale comes from
 * the generated schema (src/client/zod.gen.ts, design.md Decision 6), never
 * written here; `age` ones are also checked against the patient's current
 * age. `hint`: a help line under the label, linked to the box.
 */
type NumberKey =
  | "alcohol.start_age"
  | "alcohol.quit_age"
  | "tobacco.cigarettes_per_day"
  | "tobacco.start_age"
  | "tobacco.quit_age"
  | "vaping.start_age"
  | "vaping.quit_age"
  | "vaping.days_last_30"
  | "secondhand_smoke.days_per_week"
  | "wood_smoke.start_age"
  | "wood_smoke.quit_age"
  | "wood_smoke.hours_per_day"

/** A generated `z.int().gte(min).lte(max).nullish()`, seen through. */
type BoundedInt = {
  unwrap(): { unwrap(): { minValue: number | null; maxValue: number | null } }
}

type NumberField = {
  draft: NumberDraftKey
  label: string
  min: number
  max: number
  age: boolean
  hint?: string
}

function numberFieldOf(
  draft: NumberDraftKey,
  schema: BoundedInt,
  { age = false, hint }: { age?: boolean; hint?: string } = {},
): NumberField {
  const scale = schema.unwrap().unwrap()
  return {
    draft,
    label: draft,
    min: scale.minValue ?? Number.NEGATIVE_INFINITY,
    max: scale.maxValue ?? Number.POSITIVE_INFINITY,
    age,
    hint,
  }
}

const NUMBER_FIELDS: Record<NumberKey, NumberField> = {
  "alcohol.start_age": numberFieldOf(
    "alcoholStartAge",
    zAlcoholHabit.shape.start_age,
    { age: true, hint: "alcoholStartAgeHint" },
  ),
  "alcohol.quit_age": numberFieldOf(
    "alcoholQuitAge",
    zAlcoholHabit.shape.quit_age,
    { age: true },
  ),
  "tobacco.cigarettes_per_day": {
    ...numberFieldOf("cigarettes", zTobaccoHabit.shape.cigarettes_per_day),
    label: "cigarettesPerDay",
  },
  "tobacco.start_age": numberFieldOf(
    "tobaccoStartAge",
    zTobaccoHabit.shape.start_age,
    { age: true },
  ),
  "tobacco.quit_age": numberFieldOf(
    "tobaccoQuitAge",
    zTobaccoHabit.shape.quit_age,
    { age: true },
  ),
  "vaping.start_age": numberFieldOf(
    "vapingStartAge",
    zVapingHabit.shape.start_age,
    { age: true },
  ),
  "vaping.quit_age": numberFieldOf(
    "vapingQuitAge",
    zVapingHabit.shape.quit_age,
    { age: true },
  ),
  "vaping.days_last_30": numberFieldOf(
    "vapingDays",
    zVapingHabit.shape.days_last_30,
  ),
  "secondhand_smoke.days_per_week": numberFieldOf(
    "daysPerWeek",
    zSecondhandSmoke.shape.days_per_week,
  ),
  "wood_smoke.start_age": numberFieldOf(
    "woodStartAge",
    zWoodSmokeHabit.shape.start_age,
    { age: true },
  ),
  "wood_smoke.quit_age": numberFieldOf(
    "woodQuitAge",
    zWoodSmokeHabit.shape.quit_age,
    { age: true },
  ),
  "wood_smoke.hours_per_day": numberFieldOf(
    "woodHours",
    zWoodSmokeHabit.shape.hours_per_day,
  ),
}

/**
 * Start ≤ end of each block (design.md, Interface contract → Validación): the
 * message goes on the start age, with the block's own wording.
 */
const AGE_PAIRS: readonly [NumberKey, NumberKey, string][] = [
  ["alcohol.start_age", "alcohol.quit_age", "startAfterQuit"],
  ["tobacco.start_age", "tobacco.quit_age", "startAfterQuit"],
  ["vaping.start_age", "vaping.quit_age", "startAfterQuit"],
  ["wood_smoke.start_age", "wood_smoke.quit_age", "startAfterEnd"],
]

/** A box and the other end of its block's pair: both are re-checked on blur. */
function blurKeys(key: NumberKey): NumberKey[] {
  const pair = AGE_PAIRS.find(([start, quit]) => key === start || key === quit)
  return pair ? [pair[0], pair[1]] : [key]
}

const ongoing = (status: string | null) => !!status && status !== "never"

/** The number boxes on screen: only the questions that apply (C-1…C-4, C-10…C-12). */
function visibleNumbers(draft: Draft): NumberKey[] {
  const keys: NumberKey[] = []
  if (ongoing(draft.alcoholStatus)) keys.push("alcohol.start_age")
  if (draft.alcoholStatus === "quit") keys.push("alcohol.quit_age")
  if (ongoing(draft.tobaccoStatus)) {
    keys.push("tobacco.cigarettes_per_day", "tobacco.start_age")
    if (draft.tobaccoStatus === "former") keys.push("tobacco.quit_age")
  }
  if (ongoing(draft.vapingStatus)) keys.push("vaping.start_age")
  if (draft.vapingStatus === "former") keys.push("vaping.quit_age")
  if (
    draft.vapingStatus === "current" &&
    draft.vapingFrequency === "some_days"
  ) {
    keys.push("vaping.days_last_30")
  }
  if (draft.places.some((place) => place !== "none")) {
    keys.push("secondhand_smoke.days_per_week")
  }
  if (ongoing(draft.woodStatus)) {
    keys.push("wood_smoke.start_age")
    if (draft.woodStatus === "former") keys.push("wood_smoke.quit_age")
    keys.push("wood_smoke.hours_per_day")
  }
  return keys
}

/**
 * Where a server 422 lands when its `loc` is not a number box: the block's
 * first control (a model-level error has `loc` ["body", "<block>"]).
 */
const BLOCK_ANCHOR: Record<string, string> = {
  alcohol: "alcohol.status",
  tobacco: "tobacco.status",
  vaping: "vaping.status",
  secondhand_smoke: "secondhand_smoke.places",
  wood_smoke: "wood_smoke.status",
}

const ANCHOR_KEYS = new Set(Object.values(BLOCK_ANCHOR))

/** The chip questions asked only while drinking now (C-1), keyed by `loc`. */
const DRINKING_CHIPS = [
  "alcohol.frequency",
  "alcohol.typical_drinks",
  "alcohol.six_or_more",
  "alcohol.mostly_weekends",
] as const

/** Every control on screen with its own error slot, besides the anchors. */
function visibleFields(draft: Draft): string[] {
  const fields: string[] = visibleNumbers(draft)
  if (draft.alcoholStatus === "current") fields.push(...DRINKING_CHIPS)
  if (draft.vapingStatus === "current") fields.push("vaping.frequency")
  return fields
}

/**
 * What the screen shows, as a string to compare with the one at opening
 * (design.md, Interface contract → Cambios sin guardar): every answer on
 * screen and the raw text of every visible box, typed but not left included.
 * A hidden question does not count, and choosing an option and going back to
 * the one before gives the same string.
 */
function screenOf(draft: Draft): string {
  const drinksNow = draft.alcoholStatus === "current"
  return JSON.stringify({
    alcohol: draft.alcoholStatus,
    drinking: drinksNow
      ? [
          draft.frequency,
          draft.typicalDrinks,
          draft.sixOrMore,
          draft.mostlyWeekends,
        ]
      : null,
    tobacco: draft.tobaccoStatus,
    vaping: draft.vapingStatus,
    vapingFrequency:
      draft.vapingStatus === "current" ? draft.vapingFrequency : null,
    places: [...draft.places].sort(),
    wood: draft.woodStatus,
    numbers: visibleNumbers(draft).map(
      (key) => [key, draft[NUMBER_FIELDS[key].draft]] as const,
    ),
  })
}

/** The session the screen opened with (design.md, hallazgo A5). */
const currentToken = () => localStorage.getItem("access_token")

/**
 * A 422 placed by its `loc`, never by its text (design.md, Decision 4; review
 * R20): ["body", block, field] goes to that field when it is on screen
 * (`fields`: a number box or a chip group, review R18), ["body", block] or a
 * field that is hidden or has no control of its own (`exposed`) to the
 * block's anchor, anything else under the form. Null when the error is not a
 * 422 with a `detail` list.
 */
function serverErrors(
  err: unknown,
  fields: readonly string[],
): Record<string, string> | null {
  if (!(err instanceof AxiosError) || err.response?.status !== 422) return null
  const detail = (err.response.data as { detail?: unknown } | undefined)?.detail
  if (typeof detail === "string") return { _form: detail }
  if (!Array.isArray(detail)) return null
  const errors: Record<string, string> = {}
  for (const item of detail as { loc?: unknown[]; msg?: string }[]) {
    const loc = (item.loc ?? []).map(String)
    const key = loc.slice(1, 3).join(".")
    let target = "_form"
    if (fields.includes(key) || ANCHOR_KEYS.has(key)) {
      target = key
    } else if (loc[0] === "body" && BLOCK_ANCHOR[loc[1]]) {
      target = BLOCK_ANCHOR[loc[1]]
    }
    errors[target] ??= item.msg ?? ""
  }
  return errors
}

/**
 * Draft → PUT body, plus the client errors (design.md, Decisions 3 and 6):
 * the same rules as the server, run before sending so each message shows
 * next to its own box (review R5), and the gate of "Guardar" (nothing goes
 * while there is an error, Decision 4). What does not apply is never
 * sent (the server drops it anyway): hidden questions go as null. The
 * server's "exposed without places" cannot happen here: `exposed` is derived
 * from the chips (a place → true, "No me expongo" → false, none → no
 * answer), so that rule only arrives as a 422 on `places`, placed by
 * serverErrors.
 */
function buildBody(
  draft: Draft,
  birthDate: string | null | undefined,
  t: TFunction,
): { body: Habits; errors: Record<string, string> } {
  const errors: Record<string, string> = {}
  const visible = visibleNumbers(draft)
  const current = birthDate ? ageToday(birthDate, mexicoCityTodayIso()) : null
  const numbers: Partial<Record<NumberKey, number | null>> = {}

  for (const key of visible) {
    const field = NUMBER_FIELDS[key]
    const text = draft[field.draft].trim()
    if (!text) {
      numbers[key] = null
      continue
    }
    if (!/^\d+$/.test(text)) {
      errors[key] = t("habits.validation.onlyNumber")
      continue
    }
    const value = Number(text)
    if (value < field.min || value > field.max) {
      errors[key] = t("habits.validation.outOfRange", {
        min: field.min,
        max: field.max,
      })
    } else if (field.age && current !== null && value > current) {
      errors[key] = t("habits.validation.ageOverCurrent")
    } else {
      numbers[key] = value
    }
  }

  for (const [startKey, quitKey, message] of AGE_PAIRS) {
    const start = numbers[startKey]
    const quit = numbers[quitKey]
    if (start != null && quit != null && start > quit) {
      errors[startKey] = t(`habits.validation.${message}`)
    }
  }

  const number = (key: NumberKey) => numbers[key] ?? null
  const exposed = draft.places.length > 0 && !draft.places.includes("none")
  const drinksNow = draft.alcoholStatus === "current"
  const vapesNow = draft.vapingStatus === "current"
  const body: Habits = {
    alcohol: draft.alcoholStatus
      ? {
          status: draft.alcoholStatus,
          start_age: number("alcohol.start_age"),
          quit_age: number("alcohol.quit_age"),
          frequency: drinksNow ? draft.frequency : null,
          typical_drinks: drinksNow ? draft.typicalDrinks : null,
          six_or_more: drinksNow ? draft.sixOrMore : null,
          mostly_weekends: drinksNow ? draft.mostlyWeekends : null,
        }
      : null,
    tobacco: draft.tobaccoStatus
      ? {
          status: draft.tobaccoStatus,
          cigarettes_per_day: number("tobacco.cigarettes_per_day"),
          start_age: number("tobacco.start_age"),
          quit_age: number("tobacco.quit_age"),
        }
      : null,
    vaping: draft.vapingStatus
      ? {
          status: draft.vapingStatus,
          frequency: vapesNow ? draft.vapingFrequency : null,
          days_last_30: number("vaping.days_last_30"),
          start_age: number("vaping.start_age"),
          quit_age: number("vaping.quit_age"),
        }
      : null,
    secondhand_smoke:
      draft.places.length === 0
        ? null
        : exposed
          ? {
              exposed: true,
              places: draft.places.filter((p): p is Place => p !== "none"),
              days_per_week: number("secondhand_smoke.days_per_week"),
            }
          : { exposed: false, places: [], days_per_week: null },
    wood_smoke: draft.woodStatus
      ? {
          status: draft.woodStatus,
          start_age: number("wood_smoke.start_age"),
          quit_age: number("wood_smoke.quit_age"),
          hours_per_day: number("wood_smoke.hours_per_day"),
        }
      : null,
  }
  return { body, errors }
}

/**
 * The habits questionnaire, /perfil/habitos (design.md, Interface contract →
 * Frontend): four blocks, each question only when it applies. Nothing is
 * sent until "Guardar" (Decision 8): one PUT through the mutation, so the
 * 401/403 handling of main.tsx applies. "Guardar" and "Cancelar" are
 * aria-disabled while that PUT is in flight (D20). Leaving a box checks it
 * and its block's start ≤ end without moving the focus; "Guardar" checks
 * everything and moves the focus to the first error (review R5). Leaving the
 * screen with unsaved changes asks first, in the app (useBlocker) and on
 * reload or close (beforeunload), unless the session changed since opening.
 * Nothing here scores or labels the answers (C-6).
 */
function HabitsForm() {
  const { t } = useTranslation("profile")
  const idPrefix = useId()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const formRef = useRef<HTMLFormElement>(null)
  const stayRef = useRef<HTMLButtonElement>(null)

  const { data: habits } = useSuspenseQuery(getHabitsQueryOptions())
  const { data: profile } = useSuspenseQuery(getProfileQueryOptions())

  // What was stored when the screen opened, and the session it opened with.
  const [opening] = useState(() => screenOf(draftFrom(habits)))
  const [openingToken] = useState(currentToken)
  const [draft, setDraft] = useState<Draft>(() => draftFrom(habits))
  // The latest draft for handlers and the blocker, ahead of the render.
  const draftRef = useRef(draft)
  const [errors, setErrors] = useState<Record<string, string>>({})
  // Bumped on every failed "Guardar" so the focus moves even when the same
  // error repeats.
  const [failedAttempt, setFailedAttempt] = useState(0)
  // A PUT in flight, known before the next render (D20: a second click or
  // Enter right after the first does nothing).
  const sending = useRef(false)
  // "Guardar" succeeded or "Cancelar" was pressed: the screen is leaving on
  // purpose, without asking.
  const leaving = useRef(false)

  const build = (from: Draft = draftRef.current) =>
    buildBody(from, profile.birth_date, t)

  const changed = () => screenOf(draftRef.current) !== opening

  const backToProfile = () => navigate({ to: "/perfil" })

  // Only refs and the opening values: stable, so the blocker is registered
  // once.
  const mustAsk = useCallback(
    () =>
      !leaving.current &&
      currentToken() === openingToken &&
      screenOf(draftRef.current) !== opening,
    [opening, openingToken],
  )
  // Where the focus was when the leave dialog opened: "Seguir editando"
  // brings it back there (Radix has no trigger to return to).
  const focusBefore = useRef<HTMLElement | null>(null)
  const blockAndRemember = useCallback(() => {
    const ask = mustAsk()
    if (ask && document.activeElement instanceof HTMLElement) {
      focusBefore.current = document.activeElement
    }
    return ask
  }, [mustAsk])
  const blocker = useBlocker({
    shouldBlockFn: blockAndRemember,
    enableBeforeUnload: mustAsk,
    withResolver: true,
  })

  const mutation = useMutation({
    mutationFn: async (body: Habits) =>
      (await ProfileService.updateHabits({ body })).data,
    onSuccess: (saved) => {
      leaving.current = true
      queryClient.setQueryData(["habits"], saved)
      showSuccessToast(t("habits.savedToast"))
      backToProfile()
    },
    onError: (err) => {
      const placed = serverErrors(err, visibleFields(draftRef.current))
      if (placed) {
        setErrors(placed)
        setFailedAttempt((n) => n + 1)
      } else {
        handleError.call(showErrorToast, err as Error)
      }
    },
    onSettled: () => {
      sending.current = false
    },
  })
  const busy = mutation.isPending

  useEffect(() => {
    if (!failedAttempt) return
    // A box (aria-invalid) or the first chip of an invalid group (a fieldset
    // is not focusable), like HistoryEntryForm.
    formRef.current
      ?.querySelector<HTMLElement>(
        '[aria-invalid="true"], fieldset[data-invalid] button',
      )
      ?.focus()
  }, [failedAttempt])

  const update = (next: Draft) => {
    draftRef.current = next
    setDraft(next)
  }

  /**
   * A chip answer, kept on screen until "Guardar". Only the errors of the
   * questions it hides go away (hallazgo A3): a box still on screen keeps its
   * mark, except a start-after-end error whose end question is now hidden,
   * which is about that question (review R12).
   */
  const choose = <K extends keyof Draft>(key: K, value: Draft[K]) => {
    const next = { ...draftRef.current, [key]: value }
    update(next)
    const shown = new Set<string>([
      ...visibleFields(next),
      ...ANCHOR_KEYS,
      "secondhand_smoke.places",
      "_form",
    ])
    const hiddenPairs = AGE_PAIRS.filter(([, end]) => !shown.has(end))
    setErrors((prev) => {
      const kept: Record<string, string> = {}
      for (const [k, message] of Object.entries(prev)) {
        if (!shown.has(k)) continue
        const pair = hiddenPairs.find(([start]) => start === k)
        if (pair && message === t(`habits.validation.${pair[2]}`)) continue
        kept[k] = message
      }
      return kept
    })
  }

  // A box left by pressing something else (a chip, "Guardar") shows its
  // error once that press ends: an error line appearing mid-press shifts the
  // layout under the pointer and the click would land somewhere else.
  const pressing = useRef(false)
  const afterPress = useRef<(() => void) | null>(null)
  useEffect(() => {
    const down = () => {
      pressing.current = true
    }
    // After the click that follows, so the press is handled first.
    const up = () =>
      setTimeout(() => {
        pressing.current = false
        const run = afterPress.current
        afterPress.current = null
        run?.()
      })
    document.addEventListener("pointerdown", down, true)
    document.addEventListener("pointerup", up, true)
    document.addEventListener("pointercancel", up, true)
    return () => {
      document.removeEventListener("pointerdown", down, true)
      document.removeEventListener("pointerup", up, true)
      document.removeEventListener("pointercancel", up, true)
    }
  }, [])

  /**
   * Leaving a box: its errors (and its pair's) are refreshed from the draft
   * as it is then (a chip pressed meanwhile may have hidden the pair), and
   * the focus stays where it went.
   */
  const leave = (key: NumberKey) => {
    const refresh = () => {
      const { errors: found } = build()
      setErrors((prev) => {
        const next = { ...prev }
        for (const k of blurKeys(key)) {
          if (found[k]) next[k] = found[k]
          else delete next[k]
        }
        return next
      })
    }
    if (pressing.current) afterPress.current = refresh
    else refresh()
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (sending.current) return
    const { body, errors: found } = build()
    if (Object.keys(found).length) {
      setErrors(found)
      setFailedAttempt((n) => n + 1)
      return
    }
    setErrors({})
    sending.current = true
    mutation.mutate(body)
  }

  /** Never sends anything nor asks (Decision 5). */
  const handleCancel = () => {
    if (sending.current) return
    const discarded = changed()
    leaving.current = true
    if (discarded) showSuccessToast(t("habits.discardedToast"))
    backToProfile()
  }

  /** The leave dialog, open while the blocker holds a navigation. */
  const asking = blocker.status === "blocked"
  const stay = () => {
    if (blocker.status === "blocked") blocker.reset()
  }
  const leaveAnyway = () => {
    if (blocker.status === "blocked") blocker.proceed()
  }

  const errorId = (key: string) => `${idPrefix}-${key}-error`
  const fieldError = (key: string) =>
    errors[key] ? (
      <p id={errorId(key)} className="text-sm text-destructive">
        {errors[key]}
      </p>
    ) : null

  const visible = visibleNumbers(draft)

  const numberField = (key: NumberKey) => {
    if (!visible.includes(key)) return null
    const field = NUMBER_FIELDS[key]
    const id = `${idPrefix}-${key}`
    const hintId = field.hint ? `${id}-hint` : undefined
    return (
      <div key={key} className="grid gap-1.5">
        <Label htmlFor={id}>{t(`habits.fields.${field.label}`)}</Label>
        {field.hint && (
          <p id={hintId} className="text-sm text-muted-foreground">
            {t(`habits.fields.${field.hint}`)}
          </p>
        )}
        <Input
          id={id}
          inputMode="numeric"
          autoComplete="off"
          className="w-24"
          value={draft[field.draft]}
          aria-invalid={!!errors[key] || undefined}
          aria-describedby={
            [hintId, errors[key] ? errorId(key) : undefined]
              .filter(Boolean)
              .join(" ") || undefined
          }
          onChange={(e) =>
            update({ ...draftRef.current, [field.draft]: e.target.value })
          }
          onBlur={() => leave(key)}
        />
        {fieldError(key)}
      </div>
    )
  }

  /** Single-choice chips with their error under them (`key` = its `loc`). */
  const chips = <V extends string>(
    key: string,
    label: string,
    options: readonly V[],
    optionKey: string,
    value: V | null,
    onChange: (next: V | null) => void,
    { showLabel = true, hintId }: { showLabel?: boolean; hintId?: string } = {},
  ) => (
    <div className="grid gap-2">
      <ChipGroup
        label={label}
        showLabel={showLabel}
        options={options.map((option) => ({
          value: option,
          label: t(`habits.options.${optionKey}.${option}`),
        }))}
        value={value}
        onChange={onChange}
        invalid={!!errors[key]}
        describedBy={
          [hintId, errors[key] ? errorId(key) : undefined]
            .filter(Boolean)
            .join(" ") || undefined
        }
      />
      {fieldError(key)}
    </div>
  )

  /** `hint`: the block's help, linked to its first group by `id` (review R13). */
  const block = (
    title: string,
    hint: { id: string; text: string } | null,
    children: ReactNode,
  ) => (
    <section className="grid gap-4 rounded-lg border p-4">
      <div className="grid gap-1">
        <h2 className="text-lg font-semibold">{title}</h2>
        {hint && (
          <p id={hint.id} className="text-sm text-muted-foreground">
            {hint.text}
          </p>
        )}
      </div>
      {children}
    </section>
  )

  const drinksHintId = `${idPrefix}-drinks-hint`
  const secondhandHintId = `${idPrefix}-secondhand-hint`
  const woodHintId = `${idPrefix}-wood-hint`
  // "Sobre todo fines de semana" is true | false | null: Sí / No chips, so a
  // second tap on the chosen one takes the answer back (D18; review R14).
  const weekends =
    draft.mostlyWeekends === null ? null : draft.mostlyWeekends ? "yes" : "no"

  return (
    <form
      ref={formRef}
      onSubmit={handleSubmit}
      noValidate
      className="flex flex-col gap-4"
    >
      <div className="grid gap-1">
        <h1 className="text-2xl font-bold tracking-tight">
          {t("habits.title")}
        </h1>
        <p className="text-muted-foreground">{t("habits.intro")}</p>
        <p className="text-sm text-muted-foreground">{t("habits.saveHint")}</p>
      </div>

      {/* The status chips go first and carry the block's name (the visible
          title is the heading); the nested questions follow them. */}
      {block(
        t("habits.blocks.alcohol"),
        null,
        <>
          {chips(
            "alcohol.status",
            t("habits.blocks.alcohol"),
            ALCOHOL_STATUSES,
            "alcoholStatus",
            draft.alcoholStatus,
            (next) => choose("alcoholStatus", next),
            { showLabel: false },
          )}
          {numberField("alcohol.start_age")}
          {numberField("alcohol.quit_age")}
          {draft.alcoholStatus === "current" && (
            <>
              {chips(
                "alcohol.frequency",
                t("habits.fields.frequency"),
                FREQUENCIES,
                "frequency",
                draft.frequency,
                (next) => choose("frequency", next),
              )}
              {chips(
                "alcohol.mostly_weekends",
                t("habits.fields.mostlyWeekends"),
                YES_NO,
                "yesNo",
                weekends,
                (next) =>
                  choose(
                    "mostlyWeekends",
                    next === null ? null : next === "yes",
                  ),
              )}
              <p id={drinksHintId} className="text-sm text-muted-foreground">
                {t("habits.fields.typicalDrinksHint")}
              </p>
              {chips(
                "alcohol.typical_drinks",
                t("habits.fields.typicalDrinks"),
                TYPICAL_DRINKS,
                "typicalDrinks",
                draft.typicalDrinks,
                (next) => choose("typicalDrinks", next),
                { hintId: drinksHintId },
              )}
              {chips(
                "alcohol.six_or_more",
                t("habits.fields.sixOrMore"),
                SIX_OR_MORE,
                "sixOrMore",
                draft.sixOrMore,
                (next) => choose("sixOrMore", next),
              )}
            </>
          )}
        </>,
      )}

      {block(
        t("habits.blocks.tobacco"),
        null,
        <>
          {chips(
            "tobacco.status",
            t("habits.blocks.tobacco"),
            SMOKE_STATUSES,
            "smokeStatus",
            draft.tobaccoStatus,
            (next) => choose("tobaccoStatus", next),
            { showLabel: false },
          )}
          {numberField("tobacco.cigarettes_per_day")}
          {numberField("tobacco.start_age")}
          {numberField("tobacco.quit_age")}
          {chips(
            "vaping.status",
            t("habits.fields.vaping"),
            SMOKE_STATUSES,
            "smokeStatus",
            draft.vapingStatus,
            (next) => choose("vapingStatus", next),
          )}
          {numberField("vaping.start_age")}
          {numberField("vaping.quit_age")}
          {draft.vapingStatus === "current" &&
            chips(
              "vaping.frequency",
              t("habits.fields.vapingFrequency"),
              VAPING_FREQUENCIES,
              "vapingFrequency",
              draft.vapingFrequency,
              (next) => choose("vapingFrequency", next),
            )}
          {numberField("vaping.days_last_30")}
        </>,
      )}

      {block(
        t("habits.blocks.secondhand"),
        { id: secondhandHintId, text: t("habits.fields.secondhandHint") },
        <>
          <div className="grid gap-2">
            <ChipMultiGroup
              label={t("habits.fields.places")}
              options={PLACES.map((place) => ({
                value: place,
                label: t(`habits.options.places.${place}`),
              }))}
              exclusive={{
                value: "none" as const,
                label: t("habits.options.places.none"),
              }}
              values={draft.places}
              onChange={(next) => choose("places", next)}
              invalid={!!errors["secondhand_smoke.places"]}
              describedBy={[
                secondhandHintId,
                errors["secondhand_smoke.places"]
                  ? errorId("secondhand_smoke.places")
                  : undefined,
              ]
                .filter(Boolean)
                .join(" ")}
            />
            {fieldError("secondhand_smoke.places")}
          </div>
          {numberField("secondhand_smoke.days_per_week")}
        </>,
      )}

      {block(
        t("habits.blocks.wood"),
        { id: woodHintId, text: t("habits.fields.woodHint") },
        <>
          {chips(
            "wood_smoke.status",
            t("habits.blocks.wood"),
            SMOKE_STATUSES,
            "smokeStatus",
            draft.woodStatus,
            (next) => choose("woodStatus", next),
            { showLabel: false, hintId: woodHintId },
          )}
          {numberField("wood_smoke.start_age")}
          {numberField("wood_smoke.quit_age")}
          {numberField("wood_smoke.hours_per_day")}
        </>,
      )}

      {errors._form && (
        <p role="alert" className="text-sm text-destructive">
          {errors._form}
        </p>
      )}

      {/* D20: aria-disabled, not disabled, so the focus stays on "Guardar"
          while it saves (LoadingButton sets the native attribute); the
          handlers ignore the press meanwhile. */}
      <div className="flex flex-wrap items-center gap-2">
        <Button
          type="submit"
          aria-disabled={busy || undefined}
          className="aria-disabled:opacity-50"
        >
          {busy && <Loader2 className="mr-2 h-5 w-5 animate-spin" />}
          {t("history.save")}
        </Button>
        <Button
          type="button"
          variant="outline"
          aria-disabled={busy || undefined}
          className="aria-disabled:opacity-50"
          onClick={handleCancel}
        >
          {t("history.cancel")}
        </Button>
      </div>

      <Dialog open={asking} onOpenChange={(open) => !open && stay()}>
        <DialogContent
          showCloseButton={false}
          onOpenAutoFocus={(event) => {
            event.preventDefault()
            stayRef.current?.focus()
          }}
          onCloseAutoFocus={(event) => {
            event.preventDefault()
            const before = focusBefore.current
            focusBefore.current = null
            if (before?.isConnected) before.focus()
          }}
        >
          <DialogHeader>
            <DialogTitle>{t("habits.leave.title")}</DialogTitle>
            <DialogDescription>{t("habits.leave.text")}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={leaveAnyway}>
              {t("habits.leave.discard")}
            </Button>
            <Button type="button" ref={stayRef} onClick={stay}>
              {t("habits.leave.stay")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </form>
  )
}

export default HabitsForm
