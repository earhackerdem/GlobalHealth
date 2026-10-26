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
  useLayoutEffect,
  useRef,
  useState,
} from "react"
import { useTranslation } from "react-i18next"

import {
  type AlcoholHabit,
  type DailyMovement,
  type ExerciseActivities,
  type Habits,
  ProfileService,
  type SecondhandSmoke,
  type SleepHabit,
  type TobaccoHabit,
  type VapingHabit,
} from "@/client"
import {
  zAlcoholHabit,
  zDailyMovement,
  zExerciseActivity,
  zOtherExerciseActivity,
  zSecondhandSmoke,
  zSleepHabit,
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
type Activity = keyof ExerciseActivities
/** "No hago ejercicio": the exclusive chip of the exercise, sent as `does_exercise: false`. */
type ActivityChoice = Activity | "none"
type MainActivity = NonNullable<DailyMovement["main_activity"]>
type Trouble = NonNullable<SleepHabit["trouble_falling_asleep"]>
/** An activity's days and minutes, keyed by their 422 `loc` (design.md, Interface contract). */
type ActivityNumberKey =
  `exercise.activities.${Activity}.${"days_per_week" | "minutes_per_session"}`

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
/** The catalog of activities, in its order (design.md, Interface contract). */
const ACTIVITIES: readonly Activity[] = [
  "walking",
  "running",
  "cycling",
  "swimming",
  "weights_gym",
  "football_other_sport",
  "yoga_pilates",
  "dance",
  "other",
]
const MAIN_ACTIVITIES: readonly MainActivity[] = [
  "sitting",
  "standing_walking",
  "light_loads",
  "heavy_work",
]
const TROUBLES: readonly Trouble[] = [
  "never",
  "some_days",
  "most_days",
  "every_day",
]
/** The active travel asks "No" before "Sí" (prototipo.html). */
const NO_YES = ["no", "yes"] as const
const daysKey = (activity: Activity): ActivityNumberKey =>
  `exercise.activities.${activity}.days_per_week`
const minutesKey = (activity: Activity): ActivityNumberKey =>
  `exercise.activities.${activity}.minutes_per_session`
/** "¿Cuál?" of "Otra": a text box, keyed by its `loc` like the numbers. */
const OTHER_NAME = "exercise.activities.other.name"
/** Its length, from the generated schema like the scales. */
const OTHER_NAME_MAX =
  zOtherExerciseActivity.shape.name.unwrap().unwrap().maxLength ?? undefined
/**
 * "No recuerdo" (perfil-habitos-completitud design.md, Decision 1), stored in
 * the number's own field.
 */
const UNKNOWN = "unknown" as const

/**
 * What the screen holds while editing; numbers stay text until sent, and
 * `unknown` lists the boxes marked "No recuerdo" (their text stays empty).
 * Each activity's days and minutes are held under their `loc`.
 */
type Draft = Record<ActivityNumberKey, string> & {
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
  activities: ActivityChoice[]
  otherName: string
  mainActivity: MainActivity | null
  activeTravel: boolean | null
  activeTravelDays: string
  sittingHours: string
  sleepHours: string
  troubleFallingAsleep: Trouble | null
  troubleStayingAsleep: Trouble | null
  unknown: readonly NumberKey[]
}

/** The activities chosen, in catalog order ("No hago ejercicio" is not one). */
const chosenActivities = (draft: Draft) =>
  ACTIVITIES.filter((activity) => draft.activities.includes(activity))

/** The draft entries that hold a number box's text. */
type NumberDraftKey = {
  [K in keyof Draft]: Draft[K] extends string ? K : never
}[keyof Draft]

/** "No recuerdo" opens with an empty box (its chip pressed, see `draftFrom`). */
const numberText = (value: number | typeof UNKNOWN | null | undefined) =>
  value == null || value === UNKNOWN ? "" : `${value}`

/** The boxes stored as "No recuerdo", read by their `loc`. */
function unknownOf(habits: Habits): NumberKey[] {
  return (Object.keys(NUMBER_FIELDS) as NumberKey[]).filter((key) => {
    const [block, field] = key.split(".") as [keyof Habits, string]
    const answer = habits[block] as Record<string, unknown> | null | undefined
    return answer?.[field] === UNKNOWN
  })
}

function draftFrom(habits: Habits): Draft {
  const {
    alcohol,
    tobacco,
    vaping,
    secondhand_smoke: smoke,
    wood_smoke,
    exercise,
    daily_movement: movement,
    sleep,
  } = habits
  let places: PlaceChoice[] = []
  if (smoke) places = smoke.exposed ? [...(smoke.places ?? [])] : ["none"]
  const done = exercise?.activities ?? {}
  let activities: ActivityChoice[] = []
  if (exercise) {
    activities = exercise.does_exercise
      ? ACTIVITIES.filter((activity) => done[activity] != null)
      : ["none"]
  }
  const activityNumbers = {} as Record<ActivityNumberKey, string>
  for (const activity of ACTIVITIES) {
    activityNumbers[daysKey(activity)] = numberText(
      done[activity]?.days_per_week,
    )
    activityNumbers[minutesKey(activity)] = numberText(
      done[activity]?.minutes_per_session,
    )
  }
  return {
    ...activityNumbers,
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
    activities,
    otherName: done.other?.name ?? "",
    mainActivity: movement?.main_activity ?? null,
    activeTravel: movement?.active_travel ?? null,
    activeTravelDays: numberText(movement?.active_travel_days),
    sittingHours: numberText(movement?.sitting_hours),
    sleepHours: numberText(sleep?.hours),
    troubleFallingAsleep: sleep?.trouble_falling_asleep ?? null,
    troubleStayingAsleep: sleep?.trouble_staying_asleep ?? null,
    unknown: unknownOf(habits),
  }
}

/**
 * The number boxes, keyed like the API's 422 `loc` ("<block>.<field>") so a
 * client error and a server one land on the same box. Each scale comes from
 * the generated schema (src/client/zod.gen.ts, design.md Decision 6), never
 * written here; `age` ones are also checked against the patient's current
 * age. `hint`: a help line under the label, linked to the box. An
 * activity's boxes (`activity`) are four levels deep, like their `loc`.
 */
type NumberKey =
  | ActivityNumberKey
  | "daily_movement.active_travel_days"
  | "daily_movement.sitting_hours"
  | "sleep.hours"
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

type Scale = { minValue: number | null; maxValue: number | null }

/**
 * A generated `z.int().gte(min).lte(max).nullish()`, seen through; where
 * "No recuerdo" is admitted the int is the first option of a union with
 * `z.literal('unknown')`, and the scale is that option's.
 */
type BoundedInt = {
  unwrap(): { unwrap(): Scale | { options: readonly unknown[] } }
}

function scaleOf(schema: BoundedInt): Scale {
  const inner = schema.unwrap().unwrap()
  if (!("options" in inner)) return inner
  const int = inner.options.find(
    (option): option is Scale =>
      typeof option === "object" && option !== null && "minValue" in option,
  )
  return int ?? { minValue: null, maxValue: null }
}

type NumberField = {
  draft: NumberDraftKey
  label: string
  min: number
  max: number
  age: boolean
  hint?: string
  activity?: Activity
}

function numberFieldOf(
  draft: NumberDraftKey,
  schema: BoundedInt,
  { age = false, hint }: { age?: boolean; hint?: string } = {},
): NumberField {
  const scale = scaleOf(schema)
  return {
    draft,
    label: draft,
    min: scale.minValue ?? Number.NEGATIVE_INFINITY,
    max: scale.maxValue ?? Number.POSITIVE_INFINITY,
    age,
    hint,
  }
}

/**
 * Each activity's days and minutes, with the scale of its own schema ("Otra"
 * has one of its own); they share their question and are named after their
 * activity on screen (R7).
 */
function activityFields(): Record<ActivityNumberKey, NumberField> {
  const fields = {} as Record<ActivityNumberKey, NumberField>
  for (const activity of ACTIVITIES) {
    const { shape } =
      activity === "other" ? zOtherExerciseActivity : zExerciseActivity
    fields[daysKey(activity)] = {
      ...numberFieldOf(daysKey(activity), shape.days_per_week),
      label: "daysPerWeek",
      activity,
    }
    fields[minutesKey(activity)] = {
      ...numberFieldOf(minutesKey(activity), shape.minutes_per_session),
      label: "minutesPerSession",
      activity,
    }
  }
  return fields
}

const NUMBER_FIELDS: Record<NumberKey, NumberField> = {
  ...activityFields(),
  "daily_movement.active_travel_days": numberFieldOf(
    "activeTravelDays",
    zDailyMovement.shape.active_travel_days,
  ),
  "daily_movement.sitting_hours": numberFieldOf(
    "sittingHours",
    zDailyMovement.shape.sitting_hours,
    { hint: "sittingHoursHint" },
  ),
  "sleep.hours": numberFieldOf("sleepHours", zSleepHabit.shape.hours, {
    hint: "sleepHoursHint",
  }),
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

/**
 * The number boxes on screen: only the questions that apply (C-1…C-5,
 * C-10…C-12; the day's movement and the sleep of actividad-sueno).
 */
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
  for (const activity of chosenActivities(draft)) {
    keys.push(daysKey(activity), minutesKey(activity))
  }
  if (draft.activeTravel) keys.push("daily_movement.active_travel_days")
  keys.push("daily_movement.sitting_hours", "sleep.hours")
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
  exercise: "exercise.activities",
  daily_movement: "daily_movement.main_activity",
  sleep: "sleep.hours",
}

const ANCHOR_KEYS = new Set(Object.values(BLOCK_ANCHOR))

/** The chip questions asked only while drinking now (C-1), keyed by `loc`. */
const DRINKING_CHIPS = [
  "alcohol.frequency",
  "alcohol.typical_drinks",
  "alcohol.six_or_more",
  "alcohol.mostly_weekends",
] as const

/** The chip questions always on screen that are not their block's anchor. */
const STANDING_CHIPS = [
  "daily_movement.active_travel",
  "sleep.trouble_falling_asleep",
  "sleep.trouble_staying_asleep",
] as const

/** Every control on screen with its own error slot, besides the anchors. */
function visibleFields(draft: Draft): string[] {
  const fields: string[] = visibleNumbers(draft)
  if (draft.alcoholStatus === "current") fields.push(...DRINKING_CHIPS)
  if (draft.vapingStatus === "current") fields.push("vaping.frequency")
  if (chosenActivities(draft).includes("other")) fields.push(OTHER_NAME)
  fields.push(...STANDING_CHIPS)
  return fields
}

/**
 * What each answer opens and has to be answered on "Guardar"
 * (perfil-habitos-completitud design.md, Interface contract → § Validación;
 * C-15), as data mirroring the backend's
 * HABITS_REQUIRED (backend/app/models.py): block → answer → [required, "No
 * recuerdo" not admitted; required, "No recuerdo" admitted], by field. An
 * answer not listed requires nothing. The second list is also where the "No
 * recuerdo" chip goes (Decision 2: only what already happened).
 */
const HABITS_REQUIRED: Record<
  string,
  Record<string, readonly [readonly string[], readonly string[]]>
> = {
  alcohol: {
    quit: [[], ["start_age", "quit_age"]],
    current: [
      ["frequency", "typical_drinks", "six_or_more", "mostly_weekends"],
      ["start_age"],
    ],
  },
  tobacco: {
    former: [[], ["cigarettes_per_day", "start_age", "quit_age"]],
    current: [["cigarettes_per_day"], ["start_age"]],
  },
  vaping: {
    former: [[], ["start_age", "quit_age"]],
    current: [["frequency"], ["start_age"]],
    current_some_days: [["frequency", "days_last_30"], ["start_age"]],
  },
  secondhand_smoke: { exposed: [["places", "days_per_week"], []] },
  wood_smoke: {
    former: [[], ["start_age", "quit_age", "hours_per_day"]],
    current: [["hours_per_day"], ["start_age"]],
  },
  // perfil-habitos-actividad-sueno; the sleep requires nothing.
  exercise: { does_exercise: [["activities"], []] },
  daily_movement: { active_travel: [["active_travel_days"], []] },
}

/**
 * What each chosen activity requires, one level deeper than its block
 * (backend's ACTIVITY_REQUIRED and OTHER_ACTIVITY_REQUIRED); none admits "No
 * recuerdo" (actividad-sueno design.md, Decision 6).
 */
const ACTIVITY_REQUIRED = ["days_per_week", "minutes_per_session"] as const
const OTHER_ACTIVITY_REQUIRED = ["name", ...ACTIVITY_REQUIRED] as const

/** A missing answer whose message is not the generic one keeps its own (backend's HABITS_MISSING_MESSAGE, ACTIVITY_MISSING_MESSAGE). */
const MISSING_MESSAGE: Record<string, string> = {
  "secondhand_smoke.places": "habits.validation.missingPlaces",
  "exercise.activities": "habits.validation.missingActivities",
  [OTHER_NAME]: "habits.validation.missingOtherName",
}

/** `exposed` comes from the chips: a place → true, "No me expongo" → false. */
const exposedOf = (draft: Draft) =>
  draft.places.length > 0 && !draft.places.includes("none")

/** Each block's HABITS_REQUIRED row, like the backend's `_habit_answer_key`. */
function answersOf(draft: Draft): [string, string | null][] {
  const someDays =
    draft.vapingStatus === "current" && draft.vapingFrequency === "some_days"
  return [
    ["alcohol", draft.alcoholStatus],
    ["tobacco", draft.tobaccoStatus],
    ["vaping", someDays ? "current_some_days" : draft.vapingStatus],
    ["secondhand_smoke", exposedOf(draft) ? "exposed" : null],
    ["wood_smoke", draft.woodStatus],
    ["exercise", chosenActivities(draft).length ? "does_exercise" : null],
    ["daily_movement", draft.activeTravel ? "active_travel" : null],
  ]
}

/** The questions the answers on screen require, by `loc`: true where "No recuerdo" is admitted. */
function requiredOf(draft: Draft): Map<string, boolean> {
  const required = new Map<string, boolean>()
  for (const [block, answer] of answersOf(draft)) {
    const [plain, orUnknown] = (answer && HABITS_REQUIRED[block][answer]) || [
      [],
      [],
    ]
    for (const field of plain) required.set(`${block}.${field}`, false)
    for (const field of orUnknown) required.set(`${block}.${field}`, true)
  }
  for (const activity of chosenActivities(draft)) {
    const fields =
      activity === "other" ? OTHER_ACTIVITY_REQUIRED : ACTIVITY_REQUIRED
    for (const field of fields) {
      required.set(`exercise.activities.${activity}.${field}`, false)
    }
  }
  return required
}

/**
 * A box marked "No recuerdo" whose question admits it now: a mark left on a
 * question that stopped admitting it (cigarettes from "Antes" to "Actual")
 * is neither shown nor sent, like the text of a hidden box.
 */
const isUnknown = (draft: Draft, key: NumberKey) =>
  draft.unknown.includes(key) && requiredOf(draft).get(key) === true

/** The chip answers the table can require, by `loc`. */
const CHIP_ANSWERS: Record<string, (draft: Draft) => unknown> = {
  "alcohol.frequency": (draft) => draft.frequency,
  "alcohol.typical_drinks": (draft) => draft.typicalDrinks,
  "alcohol.six_or_more": (draft) => draft.sixOrMore,
  "alcohol.mostly_weekends": (draft) => draft.mostlyWeekends,
  "vaping.frequency": (draft) => draft.vapingFrequency,
  "secondhand_smoke.places": (draft) =>
    draft.places.filter((place) => place !== "none"),
  "exercise.activities": chosenActivities,
}

/**
 * The required questions left unanswered (C-15), with the server's messages:
 * a box answers with its text or, where admitted, "No recuerdo".
 */
function missingOf(draft: Draft, t: TFunction): Record<string, string> {
  const missing: Record<string, string> = {}
  for (const [loc, orUnknown] of requiredOf(draft)) {
    let answered: boolean
    if (loc in NUMBER_FIELDS) {
      const key = loc as NumberKey
      answered =
        !!draft[NUMBER_FIELDS[key].draft].trim() || isUnknown(draft, key)
    } else if (loc === OTHER_NAME) {
      answered = !!draft.otherName.trim()
    } else {
      const answer = CHIP_ANSWERS[loc]?.(draft)
      answered = answer != null && !(Array.isArray(answer) && !answer.length)
    }
    if (answered) continue
    missing[loc] = t(
      MISSING_MESSAGE[loc] ??
        (orUnknown
          ? "habits.validation.missingOrUnknown"
          : "habits.validation.missing"),
    )
  }
  return missing
}

/**
 * What the screen shows, as a string to compare with the one at opening
 * (design.md, Interface contract → Cambios sin guardar): every answer on
 * screen and the raw text (or "No recuerdo") of every visible box, typed but
 * not left included.
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
    activities: [...draft.activities].sort(),
    otherName: chosenActivities(draft).includes("other")
      ? draft.otherName
      : null,
    movement: [draft.mainActivity, draft.activeTravel],
    sleep: [draft.troubleFallingAsleep, draft.troubleStayingAsleep],
    numbers: visibleNumbers(draft).map(
      (key) =>
        [
          key,
          isUnknown(draft, key) ? UNKNOWN : draft[NUMBER_FIELDS[key].draft],
        ] as const,
    ),
  })
}

/** Longer than any menu takes to close (the side sheet animates out). */
const MENU_CLOSE_MS = 1000

/**
 * A leave called off: the focus goes to `title` when the element the leave
 * came from is gone (R4-3). A menu still closing keeps that element connected
 * until it unmounts, and then gives the focus back to its own trigger: so
 * wait for the element to go and take the focus back once from that trigger.
 * An element still on screen (in the form, or a menu that stays open) keeps
 * the focus where it is.
 */
function focusTitleOnceGone(
  from: HTMLElement | null,
  form: HTMLFormElement | null,
  title: HTMLHeadingElement | null,
) {
  if (!title) return
  if (!from?.isConnected) {
    title.focus()
    return
  }
  if (form?.contains(from)) return
  const deadline = Date.now() + MENU_CLOSE_MS
  const takeBack = (event: FocusEvent) => {
    if (form?.contains(event.target as Node)) return
    document.removeEventListener("focusin", takeBack)
    if (Date.now() < deadline) title.focus()
  }
  const observer = new MutationObserver(() => {
    if (from.isConnected) return
    observer.disconnect()
    title.focus()
    document.addEventListener("focusin", takeBack)
  })
  observer.observe(document.body, { childList: true, subtree: true })
  setTimeout(() => {
    observer.disconnect()
    document.removeEventListener("focusin", takeBack)
  }, MENU_CLOSE_MS)
}

/** The session the screen opened with (design.md, hallazgo A5). */
const currentToken = () => localStorage.getItem("access_token")

/**
 * A 422 placed by its `loc`, never by its text (design.md, Decision 4; review
 * R20): ["body", block, field] goes to that field when it is on screen
 * (`fields`: a number box or a chip group, review R18), ["body", block] or a
 * field that is hidden or has no control of its own (`exposed`) to the
 * block's anchor, anything else under the form. Null when the error is not a
 * 422 with a `detail` list. An activity's field is deeper (["body",
 * "exercise", "activities", type, field]): the longest `loc` with a control
 * on screen wins.
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
    let target = "_form"
    for (let end = loc.length; end >= 3 && target === "_form"; end--) {
      const key = loc.slice(1, end).join(".")
      if (fields.includes(key) || ANCHOR_KEYS.has(key)) target = key
    }
    if (target === "_form" && loc[0] === "body" && BLOCK_ANCHOR[loc[1]]) {
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
 * while there is an error, Decision 4). `errors` are the ones of what was
 * written (checked on leaving a box too); `missing`, the required questions
 * left unanswered, only for "Guardar" (perfil-habitos-completitud, Decision
 * 4). What does not apply is never sent (the server drops it anyway): hidden
 * questions go as null, and "No recuerdo" only where it is admitted. The
 * server's "exposed without places" cannot happen here: `exposed` is derived
 * from the chips (a place → true, "No me expongo" → false, none → no
 * answer), so that rule only arrives as a 422 on `places`, placed by
 * serverErrors.
 */
function buildBody(
  draft: Draft,
  birthDate: string | null | undefined,
  t: TFunction,
): {
  body: Habits
  errors: Record<string, string>
  missing: Record<string, string>
} {
  const errors: Record<string, string> = {}
  const visible = visibleNumbers(draft)
  const current = birthDate ? ageToday(birthDate, mexicoCityTodayIso()) : null
  const numbers: Partial<Record<NumberKey, number | typeof UNKNOWN | null>> = {}

  for (const key of visible) {
    const field = NUMBER_FIELDS[key]
    const text = draft[field.draft].trim()
    if (!text) {
      numbers[key] = isUnknown(draft, key) ? UNKNOWN : null
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

  // "No recuerdo" is never compared (perfil-habitos-completitud design.md,
  // § Validación).
  for (const [startKey, quitKey, message] of AGE_PAIRS) {
    const start = numbers[startKey]
    const quit = numbers[quitKey]
    if (typeof start === "number" && typeof quit === "number" && start > quit) {
      errors[startKey] = t(`habits.validation.${message}`)
    }
  }

  const number = (key: NumberKey) => numbers[key] ?? null
  // The boxes that never admit "No recuerdo" (days, and every box of the
  // exercise, the day and the sleep).
  const count = (key: NumberKey) => {
    const value = numbers[key]
    return typeof value === "number" ? value : null
  }
  const exposed = exposedOf(draft)
  const drinksNow = draft.alcoholStatus === "current"
  const vapesNow = draft.vapingStatus === "current"
  // An activity not chosen is not sent; with none chosen and no "No hago
  // ejercicio" the block is unanswered (null), like "¿Dónde?".
  const chosen: ExerciseActivities = {}
  for (const activity of chosenActivities(draft)) {
    chosen[activity] = {
      days_per_week: count(daysKey(activity)),
      minutes_per_session: count(minutesKey(activity)),
    }
  }
  if (chosen.other) chosen.other.name = draft.otherName.trim() || null
  let exercise: Habits["exercise"] = null
  if (draft.activities.includes("none")) exercise = { does_exercise: false }
  else if (Object.keys(chosen).length) {
    exercise = { does_exercise: true, activities: chosen }
  }
  const sittingHours = count("daily_movement.sitting_hours")
  const sleepHours = count("sleep.hours")
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
          days_last_30: count("vaping.days_last_30"),
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
              days_per_week: count("secondhand_smoke.days_per_week"),
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
    exercise,
    daily_movement:
      draft.mainActivity !== null ||
      draft.activeTravel !== null ||
      sittingHours !== null
        ? {
            main_activity: draft.mainActivity,
            active_travel: draft.activeTravel,
            active_travel_days: count("daily_movement.active_travel_days"),
            sitting_hours: sittingHours,
          }
        : null,
    sleep:
      sleepHours !== null ||
      draft.troubleFallingAsleep !== null ||
      draft.troubleStayingAsleep !== null
        ? {
            hours: sleepHours,
            trouble_falling_asleep: draft.troubleFallingAsleep,
            trouble_staying_asleep: draft.troubleStayingAsleep,
          }
        : null,
  }
  return { body, errors, missing: missingOf(draft, t) }
}

/**
 * "Total de lo anotado" (actividad-sueno design.md, Decision 4): days ×
 * minutes of each chosen activity whose two numbers are valid, as they would
 * be sent; null when none has them. Shown on screen only, never sent nor
 * compared with anything (C-6).
 */
function weeklyTotalOf(body: Habits): number | null {
  let total: number | null = null
  for (const answer of Object.values(body.exercise?.activities ?? {})) {
    const days = answer?.days_per_week
    const minutes = answer?.minutes_per_session
    if (typeof days === "number" && typeof minutes === "number") {
      total = (total ?? 0) + days * minutes
    }
  }
  return total
}

/**
 * The habits questionnaire, /perfil/habitos (design.md, Interface contract →
 * Frontend): four blocks, and the exercise, the day's movement and the sleep
 * of perfil-habitos-actividad-sueno, each question only when it applies. Nothing is
 * sent until "Guardar" (Decision 8): one PUT through the mutation, so the
 * 401/403 handling of main.tsx applies. "Guardar" and "Cancelar" are
 * aria-disabled while that PUT is in flight (D20), "Guardar" reads
 * "Guardando…" (R2-5) and the questions take no changes, the chips dimmed
 * like "Guardar" (R2-3, R3-4); leaving meanwhile does not ask but waits for
 * the PUT, going on after a save and staying after a failure (R3-1, R3-3), and
 * its end only touches the screen and the session that sent it (R2-1, R2-2).
 * Leaving a box checks it
 * and its block's start ≤ end without moving the focus; "Guardar" checks
 * everything, what each answer requires included (HABITS_REQUIRED, C-15),
 * and moves the focus to the first error (review R5). Leaving the
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
  // The screen is still open: a PUT that ends after leaving it only refreshes
  // the cache (R2-1, R2-2).
  const mounted = useRef(false)
  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
    }
  }, [])
  const titleRef = useRef<HTMLHeadingElement>(null)

  const build = (from: Draft = draftRef.current) =>
    buildBody(from, profile.birth_date, t)

  const changed = () => screenOf(draftRef.current) !== opening

  const backToProfile = () => navigate({ to: "/perfil" })

  // Only refs and the opening values: stable, so the blocker is registered
  // once. Never while the PUT is in flight (R2-2): leaving then waits for it
  // instead (`mustWait`), and reloading or closing does not ask.
  const mustAsk = useCallback(
    () =>
      !leaving.current &&
      !sending.current &&
      currentToken() === openingToken &&
      screenOf(draftRef.current) !== opening,
    [opening, openingToken],
  )
  // Leaving while "Guardar" is in flight, with the session it opened with,
  // waits for the PUT without asking (R3-1, R3-3): held by the blocker, it goes
  // on after a save and is called off after a failure. After a change of
  // session nothing is held.
  const mustWait = useCallback(
    () =>
      !leaving.current && sending.current && currentToken() === openingToken,
    [openingToken],
  )
  // `silent`: the navigation the blocker holds is waiting, not asking (no
  // dialog). `waiting`: a held navigation the end of the PUT has to resolve.
  const silent = useRef(false)
  const waiting = useRef(false)
  // How the PUT resolved the held navigation; applied once the blocker holds
  // it (the PUT may end before the blocker reports it).
  const [heldOutcome, setHeldOutcome] = useState<"go" | "stay" | null>(null)
  // Where the focus was when the leave dialog opened: "Seguir editando"
  // brings it back there (Radix has no trigger to return to).
  const focusBefore = useRef<HTMLElement | null>(null)
  // The element the held leave came from, and whether its failure placed a
  // 422 on a field: a leave called off moves the focus to the title when that
  // element is gone and no field takes it (R4-3).
  const heldFrom = useRef<HTMLElement | null>(null)
  const heldPlaced = useRef(false)
  const blockAndRemember = useCallback(() => {
    const wait = mustWait()
    silent.current = wait
    if (wait) {
      waiting.current = true
      heldFrom.current =
        document.activeElement instanceof HTMLElement
          ? document.activeElement
          : null
      return true
    }
    const ask = mustAsk()
    if (ask && document.activeElement instanceof HTMLElement) {
      focusBefore.current = document.activeElement
    }
    return ask
  }, [mustAsk, mustWait])
  const blocker = useBlocker({
    shouldBlockFn: blockAndRemember,
    enableBeforeUnload: mustAsk,
    withResolver: true,
  })

  const mutation = useMutation({
    mutationFn: async (body: Habits) =>
      (await ProfileService.updateHabits({ body })).data,
    // Only for the screen and the session that sent it (R2-1, R2-2): after
    // leaving or a change of session the answer is not written into the
    // cache (it could be another account's); ["habits"] is asked again with
    // the session of that moment, without a toast or a navigation. A leave
    // held meanwhile goes where it was going instead of /perfil (R3-1).
    onSuccess: (saved) => {
      const held = waiting.current
      waiting.current = false
      if (!mounted.current || currentToken() !== openingToken) {
        queryClient.invalidateQueries({ queryKey: ["habits"] })
        if (held) setHeldOutcome("go")
        return
      }
      leaving.current = true
      queryClient.setQueryData(["habits"], saved)
      showSuccessToast(t("habits.savedToast"))
      if (held) setHeldOutcome("go")
      else backToProfile()
    },
    // A leave held meanwhile is called off: the error stays in sight (R3-3).
    onError: (err) => {
      const placed = serverErrors(err, visibleFields(draftRef.current))
      if (waiting.current) {
        waiting.current = false
        heldPlaced.current = !!placed
        setHeldOutcome("stay")
      }
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

  // While saving the chips say they take no changes (R2-3; `choose` ignores
  // the press). ChipGroup has no such prop and stays untouched (design.md,
  // what is not touched): the attribute is set on its buttons from here, and
  // React leaves it alone because it never renders it.
  useLayoutEffect(() => {
    const buttons =
      formRef.current?.querySelectorAll<HTMLButtonElement>("fieldset button")
    for (const button of buttons ?? []) {
      if (busy) button.setAttribute("aria-disabled", "true")
      else button.removeAttribute("aria-disabled")
    }
  }, [busy])

  /**
   * A chip answer, kept on screen until "Guardar". Only the errors of the
   * questions it hides go away (hallazgo A3): a box still on screen keeps its
   * mark, except a start-after-end error whose end question is now hidden,
   * which is about that question (review R12), and a "Contesta esta
   * pregunta" that no longer holds as it was (answered now, or asked with
   * the other wording: cigarettes from "Actual" to "Antes").
   */
  const choose = <K extends keyof Draft>(key: K, value: Draft[K]) => {
    // While saving the answers stay as sent (R2-3).
    if (sending.current) return
    const next = { ...draftRef.current, [key]: value }
    update(next)
    const shown = new Set<string>([
      ...visibleFields(next),
      ...ANCHOR_KEYS,
      "secondhand_smoke.places",
      "_form",
    ])
    const hiddenPairs = AGE_PAIRS.filter(([, end]) => !shown.has(end))
    const missing = missingOf(next, t)
    const missingTexts = new Set(
      [
        "missing",
        "missingOrUnknown",
        "missingPlaces",
        "missingActivities",
        "missingOtherName",
      ].map((k) => t(`habits.validation.${k}`)),
    )
    setErrors((prev) => {
      const kept: Record<string, string> = {}
      for (const [k, message] of Object.entries(prev)) {
        if (!shown.has(k)) continue
        const pair = hiddenPairs.find(([start]) => start === k)
        if (pair && message === t(`habits.validation.${pair[2]}`)) continue
        if (missingTexts.has(message) && missing[k] !== message) continue
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
   * the focus stays where it went. What is missing is not checked here
   * (perfil-habitos-completitud design.md, Decision 4), but a "Contesta esta
   * pregunta" from "Guardar" stays while the box is still unanswered. The
   * pair's box, if it has the focus, gets no new error: it is being typed in
   * (C-17), and a refresh held by a press may run after typing there began
   * (the timer can lag behind the keys).
   */
  const leave = (key: NumberKey) => {
    const refresh = () => {
      const { errors: found, missing } = build()
      const typingIn = document.activeElement?.id
      setErrors((prev) => {
        const next = { ...prev }
        for (const k of blurKeys(key)) {
          const typing = k !== key && typingIn === `${idPrefix}-${k}`
          if (found[k]) {
            if (!typing || prev[k]) next[k] = found[k]
          } else if (!prev[k] || prev[k] !== missing[k]) delete next[k]
        }
        return next
      })
    }
    if (pressing.current) afterPress.current = refresh
    else refresh()
  }

  /**
   * A change in a box (C-17): the errors already shown on it (and its pair's)
   * that no longer hold go away at once, a valid or empty box included; no
   * new one appears while typing (they do on leaving the box, C-14). A
   * missing answer of the pair that is still missing keeps its message.
   */
  const settle = (key: NumberKey, next: Draft) => {
    const { errors: found, missing } = build(next)
    setErrors((prev) => {
      const kept = { ...prev }
      for (const k of blurKeys(key)) {
        if (!prev[k] || found[k]) continue
        if (k === key || prev[k] !== missing[k]) delete kept[k]
      }
      return kept
    })
  }

  /**
   * "No recuerdo" (C-16): marking it empties the box and takes its error
   * away; typing in the box unmarks it. While saving it takes no changes,
   * like the chips (D20).
   */
  const toggleUnknown = (key: NumberKey) => {
    if (sending.current) return
    const now = draftRef.current
    const next: Draft = now.unknown.includes(key)
      ? { ...now, unknown: now.unknown.filter((k) => k !== key) }
      : {
          ...now,
          [NUMBER_FIELDS[key].draft]: "",
          unknown: [...now.unknown, key],
        }
    update(next)
    settle(key, next)
  }

  /**
   * "¿Cuál?" of "Otra": its only error is the missing name from "Guardar",
   * which goes as soon as something is written (C-17); nothing is checked on
   * leaving it.
   */
  const changeOtherName = (text: string) => {
    if (sending.current) return
    update({ ...draftRef.current, otherName: text })
    if (!text.trim()) return
    setErrors((prev) => {
      const kept = { ...prev }
      delete kept[OTHER_NAME]
      return kept
    })
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (sending.current) return
    const { body, errors: written, missing } = build()
    const found = { ...missing, ...written }
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

  // The held leave, resolved once the blocker holds it and the PUT ended, and
  // only with the session it opened with: if the session ended meanwhile (a
  // 401/403), main.tsx's reload to /login wins, and a reset here (history.go)
  // would race it (R4-1). Called off, the focus goes to the title when the
  // element it left from is gone (the side menu closed, or is closing) and no
  // 422 placed it on a field (R4-3).
  useEffect(() => {
    if (!heldOutcome || blocker.status !== "blocked") return
    setHeldOutcome(null)
    const from = heldFrom.current
    const placed = heldPlaced.current
    heldFrom.current = null
    heldPlaced.current = false
    if (currentToken() !== openingToken) return
    if (heldOutcome === "go") {
      blocker.proceed()
      return
    }
    blocker.reset()
    if (!placed) focusTitleOnceGone(from, formRef.current, titleRef.current)
  }, [heldOutcome, blocker, openingToken])

  /**
   * The leave dialog, open while the blocker holds a navigation to ask about
   * (not one waiting for the PUT).
   */
  const asking = blocker.status === "blocked" && !silent.current
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
  const required = requiredOf(draft)

  /**
   * The box, and under it "No recuerdo" where the table admits it (C-16): a
   * toggle named after its question so each one is told apart (R7). An
   * activity's box is named after its activity too, for the same reason.
   */
  const numberField = (key: NumberKey) => {
    if (!visible.includes(key)) return null
    const field = NUMBER_FIELDS[key]
    const id = `${idPrefix}-${key}`
    const hintId = field.hint ? `${id}-hint` : undefined
    const label = t(`habits.fields.${field.label}`)
    const spoken = field.activity
      ? t("habits.activityField", {
          field: label,
          activity: t(`habits.options.activities.${field.activity}`),
        })
      : undefined
    const unknown = isUnknown(draft, key)
    return (
      <div key={key} className="grid gap-1.5">
        <Label htmlFor={id}>{label}</Label>
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
          // While saving the box keeps what was sent (R2-3).
          readOnly={busy}
          aria-label={spoken}
          aria-invalid={!!errors[key] || undefined}
          aria-describedby={
            [hintId, errors[key] ? errorId(key) : undefined]
              .filter(Boolean)
              .join(" ") || undefined
          }
          onChange={(e) => {
            if (sending.current) return
            const now = draftRef.current
            const next: Draft = {
              ...now,
              [field.draft]: e.target.value,
              unknown: now.unknown.filter((k) => k !== key),
            }
            update(next)
            settle(key, next)
          }}
          onBlur={() => leave(key)}
        />
        {required.get(key) && (
          <Button
            type="button"
            size="sm"
            variant={unknown ? "default" : "outline"}
            className="w-fit aria-disabled:cursor-not-allowed aria-disabled:opacity-50"
            aria-pressed={unknown}
            aria-label={t("habits.dontRememberFor", { label })}
            aria-disabled={busy || undefined}
            onClick={() => toggleUnknown(key)}
          >
            {t("habits.dontRemember")}
          </Button>
        )}
        {fieldError(key)}
      </div>
    )
  }

  /** "¿Cuál?" of "Otra", before its days and minutes (no "No recuerdo"). */
  const otherNameField = () => {
    const id = `${idPrefix}-${OTHER_NAME}`
    const invalid = !!errors[OTHER_NAME]
    return (
      <div className="grid gap-1.5">
        <Label htmlFor={id}>{t("habits.fields.otherName")}</Label>
        <Input
          id={id}
          autoComplete="off"
          className="max-w-xs"
          maxLength={OTHER_NAME_MAX}
          value={draft.otherName}
          readOnly={busy}
          aria-invalid={invalid || undefined}
          aria-describedby={invalid ? errorId(OTHER_NAME) : undefined}
          onChange={(e) => changeOtherName(e.target.value)}
        />
        {fieldError(OTHER_NAME)}
      </div>
    )
  }

  /**
   * Single-choice chips with their error under them (`key` = its `loc`).
   * `long`: options longer than a phone's width wrap inside their chip
   * instead of widening the page (ChipGroup stays untouched).
   */
  const chips = <V extends string>(
    key: string,
    label: string,
    options: readonly V[],
    optionKey: string,
    value: V | null,
    onChange: (next: V | null) => void,
    {
      showLabel = true,
      hintId,
      long = false,
    }: { showLabel?: boolean; hintId?: string; long?: boolean } = {},
  ) => (
    <div className="grid gap-2">
      <ChipGroup
        className={
          long
            ? "[&_button]:h-auto [&_button]:max-w-full [&_button]:whitespace-normal [&_button]:py-1.5 [&_button]:text-left"
            : undefined
        }
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
  const movementHintId = `${idPrefix}-movement-hint`
  // The active travel too: true | false | null, No / Sí chips.
  const travel =
    draft.activeTravel === null ? null : draft.activeTravel ? "yes" : "no"
  const total = weeklyTotalOf(build(draft).body)

  return (
    <form
      ref={formRef}
      onSubmit={handleSubmit}
      noValidate
      // While saving the chips look like "Guardar" (R3-4), from here like
      // their aria-disabled: ChipGroup stays untouched.
      className={`flex flex-col gap-4 ${
        busy
          ? "[&_fieldset_button]:cursor-not-allowed [&_fieldset_button]:opacity-50"
          : ""
      }`}
    >
      <div className="grid gap-1">
        {/* Focusable by script only: where "Seguir editando" leaves the focus
            when its element is gone (R2-4), and a leave called off after a
            failed save when the element it left from is gone (R4-3). */}
        <h1
          ref={titleRef}
          tabIndex={-1}
          className="text-2xl font-bold tracking-tight"
        >
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

      {/* Each chosen activity, in catalog order, asks its own days and
          minutes; the total sums what is written and is a live region, so
          it is heard as it changes (C-5, C-6). */}
      {block(
        t("habits.blocks.exercise"),
        null,
        <>
          <div className="grid gap-2">
            <ChipMultiGroup
              label={t("habits.fields.exercise")}
              options={ACTIVITIES.map((activity) => ({
                value: activity,
                label: t(`habits.options.activities.${activity}`),
              }))}
              exclusive={{
                value: "none" as const,
                label: t("habits.options.activities.none"),
              }}
              values={draft.activities}
              onChange={(next) => choose("activities", next)}
              invalid={!!errors["exercise.activities"]}
              describedBy={
                errors["exercise.activities"]
                  ? errorId("exercise.activities")
                  : undefined
              }
            />
            {fieldError("exercise.activities")}
          </div>
          {chosenActivities(draft).map((activity) => (
            <div key={activity} className="grid gap-4 border-l-2 pl-3">
              <p className="text-sm font-semibold">
                {t(`habits.options.activities.${activity}`)}
              </p>
              {activity === "other" && otherNameField()}
              {numberField(daysKey(activity))}
              {numberField(minutesKey(activity))}
            </div>
          ))}
          <p role="status" className="text-sm font-medium empty:hidden">
            {total === null ? null : t("habits.weeklyTotal", { count: total })}
          </p>
        </>,
      )}

      {block(
        t("habits.blocks.movement"),
        { id: movementHintId, text: t("habits.fields.movementHint") },
        <>
          {chips(
            "daily_movement.main_activity",
            t("habits.fields.mainActivity"),
            MAIN_ACTIVITIES,
            "mainActivity",
            draft.mainActivity,
            (next) => choose("mainActivity", next),
            { hintId: movementHintId, long: true },
          )}
          {chips(
            "daily_movement.active_travel",
            t("habits.fields.activeTravel"),
            NO_YES,
            "yesNo",
            travel,
            (next) =>
              choose("activeTravel", next === null ? null : next === "yes"),
          )}
          {numberField("daily_movement.active_travel_days")}
          {numberField("daily_movement.sitting_hours")}
        </>,
      )}

      {block(
        t("habits.blocks.sleep"),
        null,
        <>
          {numberField("sleep.hours")}
          {chips(
            "sleep.trouble_falling_asleep",
            t("habits.fields.troubleFallingAsleep"),
            TROUBLES,
            "trouble",
            draft.troubleFallingAsleep,
            (next) => choose("troubleFallingAsleep", next),
          )}
          {chips(
            "sleep.trouble_staying_asleep",
            t("habits.fields.troubleStayingAsleep"),
            TROUBLES,
            "trouble",
            draft.troubleStayingAsleep,
            (next) => choose("troubleStayingAsleep", next),
          )}
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
          {busy ? t("habits.saving") : t("history.save")}
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
            // The side menu or the user menu closed meanwhile: the title
            // (R2-4).
            if (before?.isConnected) before.focus()
            else titleRef.current?.focus()
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
