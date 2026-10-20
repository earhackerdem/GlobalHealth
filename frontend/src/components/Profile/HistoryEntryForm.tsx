import { useMutation, useQueryClient } from "@tanstack/react-query"
import { AxiosError } from "axios"
import { type FormEvent, useEffect, useId, useRef, useState } from "react"
import { useTranslation } from "react-i18next"

import { ProfileService, type profileCreateHistoryEntryData } from "@/client"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import ChipGroup from "./ChipGroup"
import {
  draftToWhen,
  EMPTY_WHEN,
  type HistoryEntry,
  type HistorySection,
  type WhenDraft,
  whenToDraft,
} from "./history"
import WhenField from "./WhenField"

type EntryBody = profileCreateHistoryEntryData["body"]

const NAME_MAX = 200
const TEXT_MAX = 2000

/**
 * Field layout per section (contract "Contenido por sección", labels from the
 * spec). `text` = a textbox; `choice` = single-choice chips; `yesNo` = Sí /
 * No / No sé chips, optionally with a detail box shown on "Sí"; `when` = the
 * WhenField.
 */
type FieldDef =
  | { kind: "text"; key: string; label: string; required?: boolean }
  | { kind: "choice"; key: string; label: string; options: readonly string[] }
  | { kind: "yesNo"; key: string; label: string; detailKey?: string }
  | { kind: "when" }

const FIELDS: Record<HistorySection, readonly FieldDef[]> = {
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
    { kind: "when" },
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
    { kind: "when" },
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
    { kind: "when" },
    { kind: "yesNo", key: "required_surgery", label: "requiredSurgery" },
    { kind: "text", key: "implant", label: "implant" },
    { kind: "text", key: "sequelae", label: "sequelae" },
  ],
  transfusions: [
    { kind: "when" },
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
  past: "condition",
  surgeries: "name",
  fractures: "what",
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

/** Which keys the current values actually send (a detail only after "Sí"). */
function activeKeys(section: HistorySection, values: Values): string[] {
  const keys: string[] = []
  for (const field of FIELDS[section]) {
    if (field.kind === "when") continue
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
 * Add / edit form of one history entry, on the section's own screen (Decision
 * 5). Validates what the API would reject anyway (nothing filled in, the
 * section's required datum, a non-numeric "cuándo") so the es-MX message
 * shows inline next to its field; anything else the server says is shown
 * inline too: a 422 with a "cuándo" sent is the impossible age or year (the
 * only server check the form does not repeat), so it goes next to "¿Cuándo?".
 * A failed validation moves the focus to the invalid field, whose
 * aria-describedby reads the message. `onDone` fires after a save or a cancel.
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
  const [when, setWhen] = useState<WhenDraft>(() =>
    entry ? whenToDraft(entry.when) : EMPTY_WHEN,
  )
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
    // first chip of an invalid chip group (a fieldset is not focusable).
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
        fail(
          message.status === 422 && body.when
            ? { when: message.detail }
            : { _form: message.detail },
        )
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
    const parsedWhen = draftToWhen(when)
    if (parsedWhen === "invalid") {
      fail({ when: t("history.when.onlyNumber") })
      return
    }
    if (parsedWhen) body.when = parsedWhen

    if (Object.keys(body).length === 0) {
      fail({ _form: t("history.validation.empty") })
      return
    }
    const requiredKey = REQUIRED_KEY[section]
    if (requiredKey && !body[requiredKey]) {
      fail({ [requiredKey]: t(`history.validation.${section}`) })
      return
    }
    // "Otra" chosen but "¿Cuál fue?" empty: the error belongs to that box.
    if (section === "past" && body.condition === "other" && !body.other_text) {
      fail({ other_text: t("history.validation.past") })
      return
    }
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
          return (
            <WhenField
              key="when"
              idPrefix={idPrefix}
              value={when}
              onChange={setWhen}
              birthDate={birthDate}
              error={errors.when}
            />
          )
        }
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
