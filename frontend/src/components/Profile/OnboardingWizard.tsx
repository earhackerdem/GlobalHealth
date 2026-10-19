import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import {
  type FamilyHistoryCreate,
  type PatientProfileUpdate,
  ProfileService,
} from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { ageFrom, formatDateMx } from "./format"

const CONDITIONS = [
  "diabetes",
  "cancer",
  "hypertension",
  "heart_disease",
  "other",
] as const

const RELATIVES = [
  "mother",
  "father",
  "maternal_grandmother",
  "maternal_grandfather",
  "paternal_grandmother",
  "paternal_grandfather",
  "sibling",
  "other",
] as const

type Condition = (typeof CONDITIONS)[number]
type Relative = (typeof RELATIVES)[number]

/** Per-condition draft: presence in the map means the condition is checked. */
type HistoryDraft = { relatives: Relative[]; detail: string }

type Sex = NonNullable<PatientProfileUpdate["sex"]>

const SELECT_CLASS =
  "border-input h-9 w-full rounded-md border bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 dark:bg-input/30"

/**
 * Onboarding wizard (FR-027): three skippable steps mounted on the dashboard
 * while the server-side onboarding state is "pending" (design decision 5).
 * Closing it — "Guardar perfil" or "Ahora no" — is an explicit POST so the
 * one-time offer survives devices, then lands on the expediente.
 */
function OnboardingWizard() {
  const { t } = useTranslation("profile")
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const [step, setStep] = useState(0)
  const [birthDate, setBirthDate] = useState("")
  const [sex, setSex] = useState<"" | Sex>("")
  const [weight, setWeight] = useState("")
  const [height, setHeight] = useState("")
  const [allergies, setAllergies] = useState("")
  const [history, setHistory] = useState<
    Partial<Record<Condition, HistoryDraft>>
  >({})

  const closeAndLeave = async () => {
    await queryClient.invalidateQueries({ queryKey: ["profile"] })
    await queryClient.invalidateQueries({ queryKey: ["family-history"] })
    navigate({ to: "/expediente" })
  }

  const skipMutation = useMutation({
    mutationFn: () =>
      ProfileService.closeOnboarding({ body: { outcome: "skipped" } }),
    onSuccess: closeAndLeave,
    onError: handleError.bind(showErrorToast),
  })

  const saveMutation = useMutation({
    mutationFn: async () => {
      const update: PatientProfileUpdate = {}
      if (birthDate) update.birth_date = birthDate
      if (sex) update.sex = sex
      if (allergies.trim()) update.allergies = allergies.trim()
      if (Object.keys(update).length > 0) {
        await ProfileService.updateProfile({ body: update })
      }
      if (weight) {
        await ProfileService.createMeasurement({
          body: { type: "weight", value: Number(weight) },
        })
      }
      if (height) {
        await ProfileService.createMeasurement({
          body: { type: "height", value: Number(height) },
        })
      }
      for (const condition of CONDITIONS) {
        const draft = history[condition]
        if (!draft) continue
        const body: FamilyHistoryCreate = {
          condition,
          relatives: draft.relatives,
        }
        const detail = draft.detail.trim()
        if (detail) {
          if (condition === "other") body.other_text = detail
          else body.note = detail
        }
        await ProfileService.createFamilyHistory({ body })
      }
      await ProfileService.closeOnboarding({ body: { outcome: "completed" } })
    },
    onSuccess: async () => {
      showSuccessToast(t("wizard.savedToast"))
      await closeAndLeave()
    },
    onError: handleError.bind(showErrorToast),
  })

  const isPending = skipMutation.isPending || saveMutation.isPending

  const skipCurrentStep = () => {
    if (step === 0) {
      setBirthDate("")
      setSex("")
      setWeight("")
      setHeight("")
    } else if (step === 1) {
      setHistory({})
      setAllergies("")
    }
    setStep(step + 1)
  }

  const stepTitle =
    step === 0
      ? t("wizard.steps.basic")
      : step === 1
        ? t("wizard.steps.family")
        : t("wizard.steps.summary")

  const checkedConditions = CONDITIONS.filter((condition) => history[condition])

  const basicSummary = [
    birthDate &&
      `${formatDateMx(birthDate)} (${t("age", { age: ageFrom(birthDate) })})`,
    sex && t(`sexOptions.${sex}`),
    weight && `${weight} kg`,
    height && `${height} cm`,
    allergies.trim(),
  ]
    .filter(Boolean)
    .join(" · ")

  return (
    <Card className="mt-6 max-w-2xl" data-testid="onboarding-wizard">
      <CardHeader>
        <CardTitle>{stepTitle}</CardTitle>
        <CardDescription>
          {t("wizard.stepCounter", { current: step + 1 })}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {step === 0 && (
          <div className="grid gap-4">
            <div className="grid gap-2">
              <Label htmlFor="onboarding-birth-date">
                {t("fields.birthDate")}
              </Label>
              <Input
                id="onboarding-birth-date"
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
              />
              {birthDate && (
                <p className="text-sm text-muted-foreground">
                  {t("age", { age: ageFrom(birthDate) })}
                </p>
              )}
            </div>
            <div className="grid gap-2">
              <Label htmlFor="onboarding-sex">{t("fields.sex")}</Label>
              <select
                id="onboarding-sex"
                className={SELECT_CLASS}
                value={sex}
                onChange={(e) => setSex(e.target.value as "" | Sex)}
              >
                <option value="">{t("sexOptions.placeholder")}</option>
                <option value="female">{t("sexOptions.female")}</option>
                <option value="male">{t("sexOptions.male")}</option>
                <option value="unspecified">
                  {t("sexOptions.unspecified")}
                </option>
              </select>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="grid gap-2">
                <Label htmlFor="onboarding-weight">{t("fields.weight")}</Label>
                <Input
                  id="onboarding-weight"
                  type="number"
                  min="1"
                  max="400"
                  step="0.1"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="onboarding-height">{t("fields.height")}</Label>
                <Input
                  id="onboarding-height"
                  type="number"
                  min="30"
                  max="250"
                  step="0.1"
                  value={height}
                  onChange={(e) => setHeight(e.target.value)}
                />
              </div>
            </div>
          </div>
        )}

        {step === 1 && (
          <div className="grid gap-4">
            {CONDITIONS.map((condition) => {
              const draft = history[condition]
              return (
                <fieldset
                  key={condition}
                  className="m-0 grid min-w-0 gap-2 border-0 p-0"
                >
                  <div className="flex items-center gap-2">
                    <Checkbox
                      id={`condition-${condition}`}
                      checked={!!draft}
                      onCheckedChange={(checked) =>
                        setHistory((prev) => {
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
                    <Label htmlFor={`condition-${condition}`}>
                      {t(`conditions.${condition}`)}
                    </Label>
                  </div>
                  {draft && (
                    <div className="ml-6 grid gap-2">
                      <div className="flex flex-wrap gap-x-4 gap-y-2">
                        {RELATIVES.map((relative) => (
                          <div
                            key={relative}
                            className="flex items-center gap-2"
                          >
                            <Checkbox
                              id={`relative-${condition}-${relative}`}
                              checked={draft.relatives.includes(relative)}
                              onCheckedChange={(checked) =>
                                setHistory((prev) => {
                                  const current = prev[condition]
                                  if (!current) return prev
                                  const relatives = checked
                                    ? [...current.relatives, relative]
                                    : current.relatives.filter(
                                        (r) => r !== relative,
                                      )
                                  return {
                                    ...prev,
                                    [condition]: { ...current, relatives },
                                  }
                                })
                              }
                            />
                            <Label
                              htmlFor={`relative-${condition}-${relative}`}
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
                          setHistory((prev) => {
                            const current = prev[condition]
                            if (!current) return prev
                            return {
                              ...prev,
                              [condition]: {
                                ...current,
                                detail: e.target.value,
                              },
                            }
                          })
                        }
                      />
                    </div>
                  )}
                </fieldset>
              )
            })}
            <div className="grid gap-2">
              <Label htmlFor="onboarding-allergies">
                {t("fields.allergies")}
              </Label>
              <Textarea
                id="onboarding-allergies"
                value={allergies}
                onChange={(e) => setAllergies(e.target.value)}
              />
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="grid gap-4 text-sm">
            <section className="grid gap-1">
              <h3 className="font-medium">{t("wizard.steps.basic")}</h3>
              <p className="text-muted-foreground">
                {basicSummary || t("wizard.emptyBasic")}
              </p>
            </section>
            <section className="grid gap-2">
              <h3 className="font-medium">{t("wizard.steps.family")}</h3>
              {checkedConditions.length === 0 ? (
                <p className="text-muted-foreground">
                  {t("wizard.emptyFamily")}
                </p>
              ) : (
                checkedConditions.map((condition) => {
                  const draft = history[condition]
                  return (
                    <div
                      key={condition}
                      className="flex flex-wrap items-center gap-2"
                    >
                      <span className="font-medium">
                        {t(`conditions.${condition}`)}
                      </span>
                      {draft?.relatives.map((relative) => (
                        <Badge key={relative} variant="secondary">
                          {t(`relatives.${relative}`)}
                        </Badge>
                      ))}
                      {draft?.detail.trim() && (
                        <span className="text-muted-foreground">
                          {draft.detail.trim()}
                        </span>
                      )}
                    </div>
                  )
                })
              )}
            </section>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex flex-wrap justify-between gap-2">
        <Button
          variant="ghost"
          disabled={isPending}
          onClick={() => skipMutation.mutate()}
        >
          {t("wizard.notNow")}
        </Button>
        <div className="flex gap-2">
          {step < 2 ? (
            <>
              <Button
                variant="outline"
                disabled={isPending}
                onClick={skipCurrentStep}
              >
                {t("wizard.skipStep")}
              </Button>
              <Button disabled={isPending} onClick={() => setStep(step + 1)}>
                {t("wizard.continue")}
              </Button>
            </>
          ) : (
            <LoadingButton
              loading={saveMutation.isPending}
              disabled={skipMutation.isPending}
              onClick={() => saveMutation.mutate()}
            >
              {t("wizard.save")}
            </LoadingButton>
          )}
        </div>
      </CardFooter>
    </Card>
  )
}

export default OnboardingWizard
