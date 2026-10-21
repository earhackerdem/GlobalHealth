import {
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { AxiosError } from "axios"
import type { TFunction } from "i18next"
import {
  type FormEvent,
  type ReactNode,
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
} from "@/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
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
const PLACES: readonly Place[] = ["home", "work_school", "other"]
const YES_NO = ["yes", "no"] as const

/** What the screen holds while editing; numbers stay text until submit. */
type Draft = {
  alcoholStatus: AlcoholStatus | null
  alcoholQuitAge: string
  frequency: Frequency | null
  typicalDrinks: TypicalDrinks | null
  sixOrMore: SixOrMore | null
  mostlyWeekends: boolean | null
  tobaccoStatus: SmokeStatus | null
  cigarettes: string
  tobaccoStartAge: string
  tobaccoQuitAge: string
  vaping: SmokeStatus | null
  places: PlaceChoice[]
  daysPerWeek: string
  woodStatus: SmokeStatus | null
  woodYears: string
}

const numberText = (value: number | null | undefined) =>
  value == null ? "" : `${value}`

function draftFrom(habits: Habits): Draft {
  const { alcohol, tobacco, secondhand_smoke: smoke, wood_smoke } = habits
  let places: PlaceChoice[] = []
  if (smoke) places = smoke.exposed ? [...(smoke.places ?? [])] : ["none"]
  return {
    alcoholStatus: alcohol?.status ?? null,
    alcoholQuitAge: numberText(alcohol?.quit_age),
    frequency: alcohol?.frequency ?? null,
    typicalDrinks: alcohol?.typical_drinks ?? null,
    sixOrMore: alcohol?.six_or_more ?? null,
    mostlyWeekends: alcohol?.mostly_weekends ?? null,
    tobaccoStatus: tobacco?.status ?? null,
    cigarettes: numberText(tobacco?.cigarettes_per_day),
    tobaccoStartAge: numberText(tobacco?.start_age),
    tobaccoQuitAge: numberText(tobacco?.quit_age),
    vaping: habits.vaping ?? null,
    places,
    daysPerWeek: numberText(smoke?.days_per_week),
    woodStatus: wood_smoke?.status ?? null,
    woodYears: numberText(wood_smoke?.years),
  }
}

/**
 * The number boxes, keyed like the API's 422 `loc` ("<block>.<field>") so a
 * client error and a server one land on the same box. Ranges are the API's
 * (design.md, Interface contract → Tipos); `age` ones are also checked
 * against the patient's current age.
 */
type NumberKey =
  | "alcohol.quit_age"
  | "tobacco.cigarettes_per_day"
  | "tobacco.start_age"
  | "tobacco.quit_age"
  | "secondhand_smoke.days_per_week"
  | "wood_smoke.years"

const NUMBER_FIELDS: Record<
  NumberKey,
  { draft: keyof Draft; label: string; min: number; max: number; age: boolean }
> = {
  "alcohol.quit_age": {
    draft: "alcoholQuitAge",
    label: "alcoholQuitAge",
    min: 0,
    max: 130,
    age: true,
  },
  "tobacco.cigarettes_per_day": {
    draft: "cigarettes",
    label: "cigarettesPerDay",
    min: 1,
    max: 100,
    age: false,
  },
  "tobacco.start_age": {
    draft: "tobaccoStartAge",
    label: "tobaccoStartAge",
    min: 0,
    max: 130,
    age: true,
  },
  "tobacco.quit_age": {
    draft: "tobaccoQuitAge",
    label: "tobaccoQuitAge",
    min: 0,
    max: 130,
    age: true,
  },
  "secondhand_smoke.days_per_week": {
    draft: "daysPerWeek",
    label: "daysPerWeek",
    min: 1,
    max: 7,
    age: false,
  },
  "wood_smoke.years": {
    draft: "woodYears",
    label: "woodYears",
    min: 0,
    max: 130,
    age: false,
  },
}

/** The number boxes on screen: only the questions that apply (C-1…C-4). */
function visibleNumbers(draft: Draft): NumberKey[] {
  const keys: NumberKey[] = []
  if (draft.alcoholStatus === "quit") keys.push("alcohol.quit_age")
  if (draft.tobaccoStatus && draft.tobaccoStatus !== "never") {
    keys.push("tobacco.cigarettes_per_day", "tobacco.start_age")
    if (draft.tobaccoStatus === "former") keys.push("tobacco.quit_age")
  }
  if (draft.places.some((place) => place !== "none")) {
    keys.push("secondhand_smoke.days_per_week")
  }
  if (draft.woodStatus && draft.woodStatus !== "never") {
    keys.push("wood_smoke.years")
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
  vaping: "vaping",
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
  return fields
}

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
 * Draft → PUT body, plus the client errors (design.md, Decision 3): the same
 * rules as the server, run before sending so each message shows next to its
 * own box (review R5). What does not apply is never sent (the server drops it
 * anyway): hidden questions go as null. The server's "exposed without places"
 * cannot happen here: `exposed` is derived from the chips (a place → true,
 * "No me expongo" → false, none → no answer), so that rule only arrives as a
 * 422 on `places`, placed by serverErrors.
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
    const text = (draft[field.draft] as string).trim()
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

  const start = numbers["tobacco.start_age"]
  const quit = numbers["tobacco.quit_age"]
  if (start != null && quit != null && start > quit) {
    errors["tobacco.start_age"] = t("habits.validation.startAfterQuit")
  }

  const exposed = draft.places.length > 0 && !draft.places.includes("none")
  const drinksNow = draft.alcoholStatus === "current"
  const body: Habits = {
    alcohol: draft.alcoholStatus
      ? {
          status: draft.alcoholStatus,
          quit_age: numbers["alcohol.quit_age"] ?? null,
          frequency: drinksNow ? draft.frequency : null,
          typical_drinks: drinksNow ? draft.typicalDrinks : null,
          six_or_more: drinksNow ? draft.sixOrMore : null,
          mostly_weekends: drinksNow ? draft.mostlyWeekends : null,
        }
      : null,
    tobacco: draft.tobaccoStatus
      ? {
          status: draft.tobaccoStatus,
          cigarettes_per_day: numbers["tobacco.cigarettes_per_day"] ?? null,
          start_age: start ?? null,
          quit_age: quit ?? null,
        }
      : null,
    vaping: draft.vaping,
    secondhand_smoke:
      draft.places.length === 0
        ? null
        : exposed
          ? {
              exposed: true,
              places: draft.places.filter((p): p is Place => p !== "none"),
              days_per_week: numbers["secondhand_smoke.days_per_week"] ?? null,
            }
          : { exposed: false, places: [], days_per_week: null },
    wood_smoke: draft.woodStatus
      ? {
          status: draft.woodStatus,
          years: numbers["wood_smoke.years"] ?? null,
        }
      : null,
  }
  return { body, errors }
}

/**
 * The habits questionnaire, /perfil/habitos (design.md, Interface contract →
 * Pantalla): four blocks, each question only when it applies, one "Guardar"
 * for the whole questionnaire (Decision 2). Nothing here scores or labels the
 * answers (C-6). A failed validation, client or server, puts each message
 * next to its control (aria-invalid / aria-describedby) and moves the focus
 * to the first invalid one in document order (review R5).
 */
function HabitsForm() {
  const { t } = useTranslation("profile")
  const idPrefix = useId()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const formRef = useRef<HTMLFormElement>(null)

  const { data: habits } = useSuspenseQuery(getHabitsQueryOptions())
  const { data: profile } = useSuspenseQuery(getProfileQueryOptions())

  const [draft, setDraft] = useState<Draft>(() => draftFrom(habits))
  const [errors, setErrors] = useState<Record<string, string>>({})
  // Bumped on every failed validation so the focus moves even when the same
  // error repeats.
  const [failedAttempt, setFailedAttempt] = useState(0)

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

  const fail = (next: Record<string, string>) => {
    setErrors(next)
    setFailedAttempt((n) => n + 1)
  }

  const backToProfile = () => navigate({ to: "/perfil" })

  const mutation = useMutation({
    mutationFn: (body: Habits) => ProfileService.updateHabits({ body }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["habits"] })
      showSuccessToast(t("habits.savedToast"))
      backToProfile()
    },
    onError: (err) => {
      const placed = serverErrors(err, visibleFields(draft))
      if (placed) fail(placed)
      else handleError.call(showErrorToast, err as Error)
    },
  })

  const set = <K extends keyof Draft>(key: K, value: Draft[K]) =>
    setDraft((prev) => ({ ...prev, [key]: value }))

  /**
   * An answer that shows or hides a block's questions: the block's errors
   * go with it, so none outlives the question it was about (review R12).
   */
  const setStatus = <K extends keyof Draft>(
    blockKey: string,
    key: K,
    value: Draft[K],
  ) => {
    set(key, value)
    setErrors((prev) =>
      Object.fromEntries(
        Object.entries(prev).filter(([k]) => !k.startsWith(`${blockKey}.`)),
      ),
    )
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    const { body, errors: found } = buildBody(draft, profile.birth_date, t)
    if (Object.keys(found).length) {
      fail(found)
      return
    }
    setErrors({})
    mutation.mutate(body)
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
    return (
      <div key={key} className="grid gap-1.5">
        <Label htmlFor={id}>{t(`habits.fields.${field.label}`)}</Label>
        <Input
          id={id}
          inputMode="numeric"
          autoComplete="off"
          className="w-24"
          value={draft[field.draft] as string}
          aria-invalid={!!errors[key] || undefined}
          aria-describedby={errors[key] ? errorId(key) : undefined}
          onChange={(e) => set(field.draft, e.target.value)}
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
            (next) => setStatus("alcohol", "alcoholStatus", next),
            { showLabel: false },
          )}
          {numberField("alcohol.quit_age")}
          {draft.alcoholStatus === "current" && (
            <>
              {chips(
                "alcohol.frequency",
                t("habits.fields.frequency"),
                FREQUENCIES,
                "frequency",
                draft.frequency,
                (next) => set("frequency", next),
              )}
              {chips(
                "alcohol.mostly_weekends",
                t("habits.fields.mostlyWeekends"),
                YES_NO,
                "yesNo",
                weekends,
                (next) =>
                  set("mostlyWeekends", next === null ? null : next === "yes"),
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
                (next) => set("typicalDrinks", next),
                { hintId: drinksHintId },
              )}
              {chips(
                "alcohol.six_or_more",
                t("habits.fields.sixOrMore"),
                SIX_OR_MORE,
                "sixOrMore",
                draft.sixOrMore,
                (next) => set("sixOrMore", next),
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
            (next) => setStatus("tobacco", "tobaccoStatus", next),
            { showLabel: false },
          )}
          {numberField("tobacco.cigarettes_per_day")}
          {numberField("tobacco.start_age")}
          {numberField("tobacco.quit_age")}
          {chips(
            "vaping",
            t("habits.fields.vaping"),
            SMOKE_STATUSES,
            "smokeStatus",
            draft.vaping,
            (next) => set("vaping", next),
          )}
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
              onChange={(next) => setStatus("secondhand_smoke", "places", next)}
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
            (next) => setStatus("wood_smoke", "woodStatus", next),
            { showLabel: false, hintId: woodHintId },
          )}
          {numberField("wood_smoke.years")}
        </>,
      )}

      {errors._form && (
        <p role="alert" className="text-sm text-destructive">
          {errors._form}
        </p>
      )}

      <div className="flex flex-wrap gap-2">
        <LoadingButton type="submit" loading={mutation.isPending}>
          {t("history.save")}
        </LoadingButton>
        <Button
          type="button"
          variant="outline"
          disabled={mutation.isPending}
          onClick={backToProfile}
        >
          {t("history.cancel")}
        </Button>
      </div>
    </form>
  )
}

export default HabitsForm
