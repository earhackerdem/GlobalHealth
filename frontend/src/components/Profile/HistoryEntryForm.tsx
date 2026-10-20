import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { AxiosError } from "axios"
import { type FormEvent, useEffect, useId, useRef, useState } from "react"
import { useTranslation } from "react-i18next"

import { ProfileService, type profileCreateHistoryEntryData } from "@/client"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import ChipGroup from "./ChipGroup"
import {
  CHRONIC_CONDITIONS,
  CHRONIC_SENSITIVE_CONDITIONS,
  draftToWhen,
  type HistoryEntry,
  type HistorySection,
  sensitiveByDefault,
  type When,
  type WhenDraft,
  whenToDraft,
} from "./history"
import { getDiagnosesQueryOptions } from "./queries"
import WhenField from "./WhenField"

type EntryBody = profileCreateHistoryEntryData["body"]

const NAME_MAX = 200
const TEXT_MAX = 2000

/** The "cuándo" answers: Story A's `when`, chronic's `since` / `until`. */
type WhenKey = "when" | "since" | "until"
const WHEN_KEYS: readonly WhenKey[] = ["when", "since", "until"]

/** Radix Select needs a non-empty value for "Ninguno". */
const NO_DIAGNOSIS = "none"

/**
 * Field layout per section (contract "Contenido por sección", labels from the
 * spec). `text` = a textbox; `choice` = single-choice chips; `yesNo` = Sí /
 * No / No sé chips, optionally with a detail box shown on "Sí"; `when` = the
 * WhenField (`legend` names it when it is not "¿Cuándo?"). Chronic only:
 * `chronicCondition` = the "¿Cuál?" radios; `sensitive` = the "Sensible"
 * checkbox; `diagnosis` = the select of the patient's diagnoses.
 */
type FieldDef =
  | { kind: "text"; key: string; label: string; required?: boolean }
  | { kind: "choice"; key: string; label: string; options: readonly string[] }
  | { kind: "yesNo"; key: string; label: string; detailKey?: string }
  | { kind: "when"; key: WhenKey; legend?: string }
  | { kind: "chronicCondition" }
  | { kind: "sensitive" }
  | { kind: "diagnosis" }

const FIELDS: Record<HistorySection, readonly FieldDef[]> = {
  chronic: [
    { kind: "chronicCondition" },
    { kind: "sensitive" },
    {
      kind: "choice",
      key: "status",
      label: "status",
      options: ["active", "resolved"],
    },
    { kind: "when", key: "since", legend: "legendSince" },
    // Only with "Ya no la tengo" (whenKeys); never sent while active.
    { kind: "when", key: "until", legend: "legendUntil" },
    { kind: "text", key: "treatment", label: "treatment" },
    { kind: "text", key: "note", label: "note" },
    { kind: "diagnosis" },
  ],
  past: [
    {
      kind: "choice",
      key: "condition",
      label: "condition",
      options: [
        "varicella",
        "measles",
        "mumps",
        "rubella",
        "hepatitis_a",
        "hepatitis_b",
        "hepatitis_c",
        "severe_covid19",
        "dengue",
        "tuberculosis",
        "other",
      ],
    },
    { kind: "when", key: "when" },
    { kind: "yesNo", key: "hospitalized", label: "hospitalized" },
    { kind: "text", key: "sequelae", label: "sequelae" },
    { kind: "text", key: "note", label: "note" },
  ],
  surgeries: [
    {
      kind: "choice",
      key: "kind",
      label: "kind",
      options: ["surgery", "hospitalization"],
    },
    { kind: "text", key: "name", label: "name", required: true },
    { kind: "when", key: "when" },
    { kind: "text", key: "reason", label: "reason" },
    { kind: "text", key: "place", label: "place" },
    { kind: "text", key: "physician", label: "physician" },
    { kind: "text", key: "complications", label: "complications" },
    {
      kind: "yesNo",
      key: "anesthesia_reaction",
      label: "anesthesiaReaction",
      detailKey: "anesthesia_reaction_detail",
    },
    { kind: "text", key: "implant", label: "implant" },
  ],
  fractures: [
    { kind: "text", key: "what", label: "what", required: true },
    {
      kind: "choice",
      key: "side",
      label: "side",
      options: ["left", "right", "both", "not_applicable"],
    },
    { kind: "when", key: "when" },
    { kind: "yesNo", key: "required_surgery", label: "requiredSurgery" },
    { kind: "text", key: "implant", label: "implant" },
    { kind: "text", key: "sequelae", label: "sequelae" },
  ],
  transfusions: [
    { kind: "when", key: "when" },
    { kind: "text", key: "reason", label: "reason" },
    {
      kind: "choice",
      key: "component",
      label: "component",
      options: ["blood", "platelets", "plasma", "unknown"],
    },
    { kind: "text", key: "place", label: "place" },
    {
      kind: "yesNo",
      key: "reaction",
      label: "reaction",
      detailKey: "reaction_detail",
    },
  ],
}

/** The field that carries each section's required-data message. */
const REQUIRED_KEY: Partial<Record<HistorySection, string>> = {
  chronic: "condition",
  past: "condition",
  surgeries: "name",
  fractures: "what",
}

/**
 * The API's chronic 422 messages and the field each belongs to
 * (backend/app/models.py HISTORY_REQUIRED and _validate_chronic_dates,
 * api/routes/profile.py _check_diagnosis_link).
 */
const SERVER_MESSAGE_FIELD: Record<string, string> = {
  "Elige la condición o escribe cuál es": "condition",
  "No puede ser antes de «desde cuándo»": "until",
  "Ese diagnóstico no está en tu expediente": "diagnosis_id",
}

const SHORT_TEXT_KEYS = new Set(["name", "what", "other_text"])
const YES_NO = ["yes", "no", "unknown"] as const

type Values = Record<string, string>

/** Every string field of an entry, "" when absent (the form's starting state). */
function valuesFrom(entry: HistoryEntry | null): Values {
  if (!entry) return {}
  const values: Values = {}
  for (const [key, value] of Object.entries(entry)) {
    if (typeof value === "string") values[key] = value
  }
  return values
}

/** The stored answer of one "cuándo" (chronic has since/until, not when). */
function whenOf(entry: HistoryEntry | null, key: WhenKey): When | null {
  if (!entry) return null
  if (entry.section === "chronic") {
    return key === "when" ? null : (entry[key] ?? null)
  }
  return key === "when" ? (entry.when ?? null) : null
}

/** The WhenFields on screen: "¿Hasta cuándo?" only with "Ya no la tengo". */
function whenKeys(section: HistorySection, values: Values): WhenKey[] {
  const keys: WhenKey[] = []
  for (const field of FIELDS[section]) {
    if (field.kind !== "when") continue
    if (field.key === "until" && values.status !== "resolved") continue
    keys.push(field.key)
  }
  return keys
}

/** Which keys the current values actually send (a detail only after "Sí"). */
function activeKeys(section: HistorySection, values: Values): string[] {
  const keys: string[] = []
  for (const field of FIELDS[section]) {
    if (field.kind === "when" || field.kind === "sensitive") continue
    if (field.kind === "diagnosis") {
      keys.push("diagnosis_id")
      continue
    }
    if (field.kind === "chronicCondition") {
      keys.push("condition")
      if (values.condition === "other") keys.push("other_text")
      continue
    }
    keys.push(field.key)
    if (
      field.kind === "yesNo" &&
      field.detailKey &&
      values[field.key] === "yes"
    ) {
      keys.push(field.detailKey)
    }
    if (field.key === "condition" && values.condition === "other") {
      keys.push("other_text")
    }
  }
  return keys
}

function serverMessage(
  err: unknown,
): { status?: number; detail: string } | null {
  if (err instanceof AxiosError) {
    const detail = (err.response?.data as { detail?: unknown } | undefined)
      ?.detail
    if (typeof detail === "string") {
      return { status: err.response?.status, detail }
    }
  }
  return null
}

/**
 * The field a server error belongs to: a known chronic message goes to its
 * field; any other 422 with exactly one "cuándo" sent is that answer's
 * impossible age or year; otherwise (two "cuándo" sent, other statuses) the
 * message stays under the form.
 */
function serverErrorKey(
  status: number | undefined,
  detail: string,
  body: Record<string, unknown>,
): string {
  if (status !== 422) return "_form"
  const known = SERVER_MESSAGE_FIELD[detail]
  if (known) return known
  const sent = WHEN_KEYS.filter((key) => body[key])
  return sent.length === 1 ? sent[0] : "_form"
}

/**
 * Add / edit form of one history entry, on the section's own screen (Decision
 * 5). Validates what the API would reject anyway (nothing filled in, the
 * section's required datum, a non-numeric "cuándo") so the es-MX message
 * shows inline next to its field; anything else the server says is shown
 * inline too (serverErrorKey): a 422 with a "cuándo" sent is the impossible
 * age or year (the only server check the form does not repeat), so it goes
 * next to its "¿Cuándo?"; chronic's "hasta antes de desde" and foreign
 * diagnosis go next to "¿Hasta cuándo?" and the diagnosis select. A failed
 * validation moves the focus to the invalid field, whose aria-describedby
 * reads the message. `onDone` fires after a save or a cancel.
 *
 * Chronic (Story B): "Sensible" follows the condition's default
 * (sensitiveByDefault) until the patient touches it, and is always sent
 * explicitly; `until` is only sent with "Ya no la tengo".
 */
function HistoryEntryForm({
  section,
  entry,
  birthDate,
  wasNone,
  onDone,
}: {
  section: HistorySection
  entry: HistoryEntry | null
  birthDate: string | null | undefined
  wasNone: boolean
  onDone: () => void
}) {
  const { t } = useTranslation("profile")
  const idPrefix = useId()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const headingRef = useRef<HTMLHeadingElement>(null)
  const formRef = useRef<HTMLFormElement>(null)

  const [values, setValues] = useState<Values>(() => valuesFrom(entry))
  const [whens, setWhens] = useState<Record<WhenKey, WhenDraft>>(() => ({
    when: whenToDraft(whenOf(entry, "when")),
    since: whenToDraft(whenOf(entry, "since")),
    until: whenToDraft(whenOf(entry, "until")),
  }))
  // null = untouched: "Sensible" follows the condition's default. A stored
  // entry always carries an explicit value (the API sets it).
  const [sensitiveChoice, setSensitiveChoice] = useState<boolean | null>(() =>
    entry?.section === "chronic" ? (entry.sensitive ?? null) : null,
  )
  const sensitive = sensitiveChoice ?? sensitiveByDefault(values.condition)
  const { data: diagnoses } = useQuery({
    ...getDiagnosesQueryOptions(),
    enabled: section === "chronic",
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  // Bumped on every failed validation so the focus moves even when the
  // same error repeats.
  const [failedAttempt, setFailedAttempt] = useState(0)

  useEffect(() => {
    headingRef.current?.focus()
  }, [])

  useEffect(() => {
    if (!failedAttempt) return
    // First invalid field in document order: a box (aria-invalid) or the
    // first chip / radio of an invalid group (a fieldset is not focusable).
    formRef.current
      ?.querySelector<HTMLElement>(
        '[aria-invalid="true"], fieldset[data-invalid] button, fieldset[data-invalid] input',
      )
      ?.focus()
  }, [failedAttempt])

  const fail = (next: Record<string, string>) => {
    setErrors(next)
    setFailedAttempt((n) => n + 1)
  }

  const mutation = useMutation({
    mutationFn: (body: EntryBody) =>
      entry
        ? ProfileService.updateHistoryEntry({ path: { id: entry.id }, body })
        : ProfileService.createHistoryEntry({ body }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["history"] }),
        queryClient.invalidateQueries({ queryKey: ["profile"] }),
      ])
      showSuccessToast(
        !entry && wasNone
          ? t("history.savedClearedNoneToast")
          : t("history.savedToast"),
      )
      onDone()
    },
    onError: (err, body) => {
      const message = serverMessage(err)
      if (message) {
        const key = serverErrorKey(
          message.status,
          message.detail,
          body as Record<string, unknown>,
        )
        fail({ [key]: message.detail })
      } else {
        handleError.call(showErrorToast, err as Error)
      }
    },
  })

  const set = (key: string, value: string | null) =>
    setValues((prev) => ({ ...prev, [key]: value ?? "" }))

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    const body: Record<string, unknown> = {}
    for (const key of activeKeys(section, values)) {
      const value = (values[key] ?? "").trim()
      if (value) body[key] = value
    }
    for (const key of whenKeys(section, values)) {
      const parsed = draftToWhen(whens[key])
      if (parsed === "invalid") {
        fail({ [key]: t("history.when.onlyNumber") })
        return
      }
      if (parsed) body[key] = parsed
    }

    if (Object.keys(body).length === 0) {
      fail({ _form: t("history.validation.empty") })
      return
    }
    const requiredKey = REQUIRED_KEY[section]
    if (requiredKey && !body[requiredKey]) {
      fail({ [requiredKey]: t(`history.validation.${section}`) })
      return
    }
    // "Otra" chosen but "¿Cuál fue?" / "¿Cuál es?" empty: the error belongs
    // to that box.
    if (
      (section === "past" || section === "chronic") &&
      body.condition === "other" &&
      !body.other_text
    ) {
      fail({ other_text: t(`history.validation.${section}`) })
      return
    }
    if (section === "chronic") body.sensitive = sensitive
    setErrors({})
    mutation.mutate({ section, ...body } as EntryBody)
  }

  const sectionTitle = t(`pending.sections.${section}`)
  const errorId = (key: string) => `${idPrefix}-${key}-error`
  const fieldError = (key: string) =>
    errors[key] ? (
      <p id={errorId(key)} className="text-sm text-destructive">
        {errors[key]}
      </p>
    ) : null

  const textField = (key: string, label: string, required = false) => {
    const id = `${idPrefix}-${key}`
    const short = SHORT_TEXT_KEYS.has(key)
    const props = {
      id,
      value: values[key] ?? "",
      maxLength: short ? NAME_MAX : TEXT_MAX,
      "aria-required": required || undefined,
      "aria-invalid": !!errors[key] || undefined,
      "aria-describedby": errors[key] ? errorId(key) : undefined,
    }
    return (
      <div key={key} className="grid gap-1.5">
        <Label htmlFor={id}>
          {label}
          {required && (
            <>
              {" "}
              <span className="text-destructive" aria-hidden="true">
                *
              </span>
            </>
          )}
        </Label>
        {/* Up to 2000 characters (secuelas, nota, motivo…) get a Textarea,
            like EditBasicData's allergies; names stay one line. */}
        {short ? (
          <Input {...props} onChange={(e) => set(key, e.target.value)} />
        ) : (
          <Textarea {...props} onChange={(e) => set(key, e.target.value)} />
        )}
        {fieldError(key)}
      </div>
    )
  }

  const visibleWhens = whenKeys(section, values)

  /** "¿Cuál?": one radio per condition, the sensitive ones under their subtitle. */
  const conditionRadios = () => {
    const label = t("history.fields.chronicCondition")
    const name = `${idPrefix}-condition`
    const invalid = !!errors.condition
    const radio = (option: string) => {
      const id = `${name}-${option}`
      return (
        <label
          key={option}
          htmlFor={id}
          className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm has-checked:border-primary has-checked:bg-accent"
        >
          <input
            id={id}
            type="radio"
            name={name}
            value={option}
            checked={values.condition === option}
            onChange={() => set("condition", option)}
            className="size-4 shrink-0 accent-primary"
          />
          {t(`history.options.chronicCondition.${option}`)}
        </label>
      )
    }
    return (
      <div key="condition" className="grid gap-2">
        <span className="text-sm font-medium" aria-hidden="true">
          {label} <span className="text-destructive">*</span>
        </span>
        {/* Nothing chosen: the error sits under the label, where the focus lands,
            not 13 options below (off-screen on a phone). With "Otra", under its text. */}
        {values.condition !== "other" && fieldError("condition")}
        {/* aria-label keeps the group's name the clean label (as ChipGroup). */}
        <fieldset
          aria-label={label}
          aria-describedby={invalid ? errorId("condition") : undefined}
          data-invalid={invalid || undefined}
          className="m-0 grid min-w-0 gap-3 border-0 p-0"
        >
          <div className="grid gap-2 sm:grid-cols-2">
            {CHRONIC_CONDITIONS.map(radio)}
          </div>
          <fieldset className="m-0 grid min-w-0 gap-2 border-0 p-0">
            <legend className="mb-2 text-sm text-muted-foreground">
              {t("history.fields.mentalHealth")}
            </legend>
            <div className="grid gap-2 sm:grid-cols-2">
              {CHRONIC_SENSITIVE_CONDITIONS.map(radio)}
            </div>
          </fieldset>
          <div className="grid gap-2 sm:grid-cols-2">{radio("other")}</div>
        </fieldset>
        {values.condition === "other" &&
          textField("other_text", t("history.fields.chronicOtherText"))}
        {values.condition === "other" && fieldError("condition")}
      </div>
    )
  }

  const sensitiveField = () => {
    const id = `${idPrefix}-sensitive`
    const hintId = `${id}-hint`
    return (
      <div key="sensitive" className="flex items-start gap-2">
        <Checkbox
          id={id}
          checked={sensitive}
          onCheckedChange={(checked) => setSensitiveChoice(checked === true)}
          aria-describedby={hintId}
          className="mt-0.5"
        />
        <div className="grid gap-1">
          <Label htmlFor={id}>{t("history.fields.sensitive")}</Label>
          <p id={hintId} className="text-sm text-muted-foreground">
            {t("history.fields.sensitiveHint")}
          </p>
        </div>
      </div>
    )
  }

  /** "Ninguno" + only the patient's diagnoses (prescriptions never back one). */
  const diagnosisField = () => {
    const id = `${idPrefix}-diagnosis`
    const invalid = !!errors.diagnosis_id
    return (
      <div key="diagnosis" className="grid gap-1.5">
        <Label htmlFor={id}>{t("history.fields.diagnosis")}</Label>
        <Select
          value={values.diagnosis_id || NO_DIAGNOSIS}
          onValueChange={(next) =>
            set("diagnosis_id", next === NO_DIAGNOSIS ? "" : next)
          }
        >
          <SelectTrigger
            id={id}
            className="w-full"
            aria-invalid={invalid || undefined}
            aria-describedby={invalid ? errorId("diagnosis_id") : undefined}
          >
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value={NO_DIAGNOSIS}>
              {t("history.fields.diagnosisNone")}
            </SelectItem>
            {diagnoses?.map((diagnosis) => (
              <SelectItem key={diagnosis.id} value={diagnosis.id}>
                {diagnosis.title}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        {fieldError("diagnosis_id")}
      </div>
    )
  }

  return (
    <form
      ref={formRef}
      onSubmit={handleSubmit}
      noValidate
      className="grid gap-4 rounded-lg border p-4"
    >
      <div className="grid gap-1">
        <h2
          ref={headingRef}
          tabIndex={-1}
          className="text-lg font-semibold outline-none"
        >
          {entry
            ? t("history.formTitleEdit", { section: sectionTitle })
            : t("history.formTitleAdd", { section: sectionTitle })}
        </h2>
        {REQUIRED_KEY[section] && (
          <p className="text-sm text-muted-foreground">
            {t("history.requiredHint")}
          </p>
        )}
      </div>

      {FIELDS[section].map((field) => {
        if (field.kind === "when") {
          if (!visibleWhens.includes(field.key)) return null
          return (
            <WhenField
              key={field.key}
              idPrefix={
                field.key === "when" ? idPrefix : `${idPrefix}-${field.key}`
              }
              value={whens[field.key]}
              onChange={(next) =>
                setWhens((prev) => ({ ...prev, [field.key]: next }))
              }
              birthDate={birthDate}
              error={errors[field.key]}
              legend={
                field.legend ? t(`history.when.${field.legend}`) : undefined
              }
            />
          )
        }
        if (field.kind === "chronicCondition") return conditionRadios()
        if (field.kind === "sensitive") return sensitiveField()
        if (field.kind === "diagnosis") return diagnosisField()
        const label = t(`history.fields.${field.label}`)
        if (field.kind === "text") {
          return textField(field.key, label, field.required)
        }
        if (field.kind === "choice") {
          const isRequired = REQUIRED_KEY[section] === field.key
          return (
            <div key={field.key} className="grid gap-2">
              <ChipGroup
                label={label}
                required={isRequired}
                options={field.options.map((option) => ({
                  value: option,
                  label: t(`history.options.${field.key}.${option}`),
                }))}
                value={values[field.key] || null}
                onChange={(next) => set(field.key, next)}
                invalid={!!errors[field.key]}
                describedBy={errors[field.key] ? errorId(field.key) : undefined}
              />
              {field.key === "condition" &&
                values.condition === "other" &&
                textField("other_text", t("history.fields.otherText"))}
              {fieldError(field.key)}
            </div>
          )
        }
        return (
          <div key={field.key} className="grid gap-2">
            <ChipGroup
              label={label}
              options={YES_NO.map((option) => ({
                value: option,
                label: t(`history.options.yesNo.${option}`),
              }))}
              value={values[field.key] || null}
              onChange={(next) => set(field.key, next)}
            />
            {field.detailKey &&
              values[field.key] === "yes" &&
              textField(field.detailKey, t("history.fields.reactionDetail"))}
          </div>
        )
      })}

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
          onClick={onDone}
        >
          {t("history.cancel")}
        </Button>
      </div>
    </form>
  )
}

export default HistoryEntryForm
