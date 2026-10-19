import type { Dispatch, SetStateAction } from "react"
import { useTranslation } from "react-i18next"

import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export const CONDITIONS = [
  "diabetes",
  "cancer",
  "hypertension",
  "heart_disease",
  "other",
] as const

export const RELATIVES = [
  "mother",
  "father",
  "maternal_grandmother",
  "maternal_grandfather",
  "paternal_grandmother",
  "paternal_grandfather",
  "sibling",
  "other",
] as const

export type Condition = (typeof CONDITIONS)[number]
export type Relative = (typeof RELATIVES)[number]

/** Per-condition draft: presence in the map means the condition is checked. */
export type HistoryDraft = { relatives: Relative[]; detail: string }
export type HistoryMap = Partial<Record<Condition, HistoryDraft>>

/**
 * The family-history editor shared by the onboarding wizard (step 2) and the
 * "Editar antecedentes" dialog on /perfil: one checkbox per condition that,
 * when checked, reveals its relatives as checkboxes plus an optional detail.
 * `idPrefix` keeps DOM ids unique if two instances ever coexist.
 */
function FamilyHistoryFields({
  value,
  onChange,
  idPrefix,
}: {
  value: HistoryMap
  onChange: Dispatch<SetStateAction<HistoryMap>>
  idPrefix: string
}) {
  const { t } = useTranslation("profile")

  return (
    <div className="grid gap-4">
      {CONDITIONS.map((condition) => {
        const draft = value[condition]
        return (
          <fieldset
            key={condition}
            className="m-0 grid min-w-0 gap-2 border-0 p-0"
          >
            <div className="flex items-center gap-2">
              <Checkbox
                id={`${idPrefix}-condition-${condition}`}
                checked={!!draft}
                onCheckedChange={(checked) =>
                  onChange((prev) => {
                    const next = { ...prev }
                    if (checked) {
                      next[condition] = { relatives: [], detail: "" }
                    } else {
                      delete next[condition]
                    }
                    return next
                  })
                }
              />
              <Label htmlFor={`${idPrefix}-condition-${condition}`}>
                {t(`conditions.${condition}`)}
              </Label>
            </div>
            {draft && (
              <div className="ml-6 grid gap-2">
                <div className="flex flex-wrap gap-x-4 gap-y-2">
                  {RELATIVES.map((relative) => (
                    <div key={relative} className="flex items-center gap-2">
                      <Checkbox
                        id={`${idPrefix}-relative-${condition}-${relative}`}
                        checked={draft.relatives.includes(relative)}
                        onCheckedChange={(checked) =>
                          onChange((prev) => {
                            const current = prev[condition]
                            if (!current) return prev
                            const relatives = checked
                              ? [...current.relatives, relative]
                              : current.relatives.filter((r) => r !== relative)
                            return {
                              ...prev,
                              [condition]: { ...current, relatives },
                            }
                          })
                        }
                      />
                      <Label
                        htmlFor={`${idPrefix}-relative-${condition}-${relative}`}
                      >
                        {t(`relatives.${relative}`)}
                      </Label>
                    </div>
                  ))}
                </div>
                <Input
                  aria-label={t("fields.detail")}
                  placeholder={t("fields.detail")}
                  value={draft.detail}
                  onChange={(e) =>
                    onChange((prev) => {
                      const current = prev[condition]
                      if (!current) return prev
                      return {
                        ...prev,
                        [condition]: { ...current, detail: e.target.value },
                      }
                    })
                  }
                />
              </div>
            )}
          </fieldset>
        )
      })}
    </div>
  )
}

export default FamilyHistoryFields
