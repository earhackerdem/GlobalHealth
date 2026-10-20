import { useTranslation } from "react-i18next"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import ChipGroup from "./ChipGroup"
import {
  approxYears,
  draftToWhen,
  formatYearRange,
  STAGES,
  type Stage,
  type WhenDraft,
} from "./history"

/**
 * "¿Cuándo?" answered the way the doctor asks it (A-3, prototype v4): the age
 * you were (default), or the year if you know it (toggle button), or a school
 * stage chip, or "No recuerdo". With a birth date, a hint shows the
 * approximate year computed on screen (Decision 4: nothing derived is stored).
 */
function WhenField({
  idPrefix,
  value,
  onChange,
  birthDate,
  error,
}: {
  idPrefix: string
  value: WhenDraft
  onChange: (next: WhenDraft) => void
  birthDate: string | null | undefined
  error?: string
}) {
  const { t } = useTranslation("profile")
  const inputId = `${idPrefix}-when-input`
  const errorId = `${idPrefix}-when-error`
  const isAge = value.mode === "age"

  const parsed = draftToWhen(value)
  const range =
    parsed && parsed !== "invalid" && parsed.kind !== "year"
      ? approxYears(parsed, birthDate)
      : null

  const chipOptions: { value: Stage | "unknown"; label: string }[] = [
    ...STAGES.map((stage) => ({
      value: stage,
      label: t(`history.when.stages.${stage}`),
    })),
    { value: "unknown", label: t("history.when.unknown") },
  ]

  return (
    <fieldset className="m-0 grid min-w-0 gap-2 border-0 p-0">
      <legend className="mb-2 text-sm font-medium">
        {t("history.when.legend")}
      </legend>
      <div className="grid gap-1.5">
        <Label htmlFor={inputId}>
          {isAge ? t("history.when.age") : t("history.when.year")}
        </Label>
        <div className="flex flex-wrap items-center gap-2">
          <Input
            id={inputId}
            inputMode="numeric"
            autoComplete="off"
            className="w-24"
            value={value.text}
            aria-invalid={!!error || undefined}
            aria-describedby={error ? errorId : undefined}
            onChange={(e) =>
              onChange({
                ...value,
                text: e.target.value,
                // A typed number replaces a chosen chip; an empty box keeps it.
                choice: e.target.value.trim() ? null : value.choice,
              })
            }
          />
          {isAge && (
            <span className="text-sm text-muted-foreground">
              {t("history.when.ageUnit")}
            </span>
          )}
          <Button
            type="button"
            variant="link"
            className="h-auto px-0"
            onClick={() =>
              onChange({ ...value, mode: isAge ? "year" : "age", text: "" })
            }
          >
            {isAge ? t("history.when.toYear") : t("history.when.toAge")}
          </Button>
        </div>
      </div>
      <ChipGroup
        label={t("history.when.stagesLabel")}
        showLabel={false}
        options={chipOptions}
        value={value.choice}
        onChange={(choice) =>
          onChange({ ...value, choice, text: choice ? "" : value.text })
        }
      />
      {range && (
        <p className="text-sm text-muted-foreground">
          {t("history.when.approxHint", { range: formatYearRange(range) })}
        </p>
      )}
      {error && (
        <p id={errorId} className="text-sm text-destructive">
          {error}
        </p>
      )}
    </fieldset>
  )
}

export default WhenField
