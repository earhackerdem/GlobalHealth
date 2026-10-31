import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { useEffect, useRef, useState } from "react"
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
} from "@/components/ui/card"
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
import { handleError, isConflictError } from "@/utils"
import FamilyHistoryFields, {
  CONDITIONS,
  type HistoryMap,
} from "./FamilyHistoryFields"
import { ageFrom, formatDateMx, mexicoCityTodayIso } from "./format"

type Sex = NonNullable<PatientProfileUpdate["sex"]>

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
  const [history, setHistory] = useState<HistoryMap>({})

  // a11y (finding G15): each step change moves focus to the step's heading so
  // screen readers announce where the wizard landed. Not on first mount — the
  // wizard shares the dashboard with the greeting.
  const titleRef = useRef<HTMLHeadingElement>(null)
  // Comparing against the previous step (not a first-render flag, which
  // StrictMode's double effect run would burn) keeps the mount unfocused.
  const prevStep = useRef(step)
  useEffect(() => {
    if (prevStep.current !== step) {
      titleRef.current?.focus()
    }
    prevStep.current = step
  }, [step])

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
    // Retry-safe (finding G3): a network cut can land some of these POSTs and
    // lose the response. On every run (first or retry) the server state is
    // re-read and only what is missing gets created; a 409 ("already there")
    // counts as done. Re-running the PUT is idempotent by nature.
    mutationFn: async () => {
      const update: PatientProfileUpdate = {}
      if (birthDate) update.birth_date = birthDate
      if (sex) update.sex = sex
      if (allergies.trim()) update.allergies = allergies.trim()
      if (Object.keys(update).length > 0) {
        await ProfileService.updateProfile({ body: update })
      }
      if (weight || height) {
        const current = (await ProfileService.readProfile()).data
        const today = mexicoCityTodayIso() // the API's measured_on
        const alreadyMeasured = (
          latest: typeof current.latest_weight,
          value: string,
        ) =>
          !!latest &&
          latest.measured_on === today &&
          latest.value === Number(value)
        if (weight && !alreadyMeasured(current.latest_weight, weight)) {
          await ProfileService.createMeasurement({
            body: { type: "weight", value: Number(weight) },
          })
        }
        if (height && !alreadyMeasured(current.latest_height, height)) {
          await ProfileService.createMeasurement({
            body: { type: "height", value: Number(height) },
          })
        }
      }
      const drafted = CONDITIONS.filter((condition) => history[condition])
      if (drafted.length > 0) {
        const existing = (await ProfileService.readFamilyHistory()).data.data
        for (const condition of drafted) {
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
          const alreadyCreated = existing.some(
            (entry) =>
              entry.condition === condition &&
              (condition !== "other" ||
                (entry.other_text ?? "") === (body.other_text ?? "")),
          )
          if (alreadyCreated) continue
          try {
            await ProfileService.createFamilyHistory({ body })
          } catch (err) {
            if (!isConflictError(err)) throw err
          }
        }
      }
      try {
        await ProfileService.closeOnboarding({ body: { outcome: "completed" } })
      } catch (err) {
        // 409: a previous attempt already closed it — the goal is reached.
        if (!isConflictError(err)) throw err
      }
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

  // Inline es-MX validation of the date (finding G16): the same bounds the
  // API enforces, shown next to the field instead of as a 422 toast.
  const birthDateError = !birthDate
    ? null
    : birthDate > mexicoCityTodayIso()
      ? t("validation.birthDateFuture")
      : birthDate < "1900-01-01"
        ? t("validation.birthDateTooOld")
        : null

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
        {/* A real heading (finding M17), focusable so the step change can
            land the focus on it; focus: (not focus-visible:) because the
            focus arrives programmatically and must stay visible. */}
        <h2
          ref={titleRef}
          tabIndex={-1}
          data-slot="card-title"
          className="rounded-sm leading-none font-semibold outline-none focus:ring-[3px] focus:ring-ring/50"
        >
          {stepTitle}
        </h2>
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
                aria-invalid={!!birthDateError}
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
              />
              {birthDateError ? (
                <p className="text-destructive text-sm">{birthDateError}</p>
              ) : (
                birthDate && (
                  <p className="text-sm text-muted-foreground">
                    {t("age", { age: ageFrom(birthDate) })}
                  </p>
                )
              )}
            </div>
            <div className="grid gap-2">
              <Label htmlFor="onboarding-sex">{t("fields.sex")}</Label>
              <Select
                value={sex}
                onValueChange={(value) => setSex(value as Sex)}
              >
                <SelectTrigger id="onboarding-sex" className="w-full">
                  <SelectValue placeholder={t("sexOptions.placeholder")} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="female">
                    {t("sexOptions.female")}
                  </SelectItem>
                  <SelectItem value="male">{t("sexOptions.male")}</SelectItem>
                  <SelectItem value="unspecified">
                    {t("sexOptions.unspecified")}
                  </SelectItem>
                </SelectContent>
              </Select>
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
            <FamilyHistoryFields
              value={history}
              onChange={setHistory}
              idPrefix="onboarding"
            />
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
        {/* "Ahora no" only while something can still be skipped: on the
            summary, with everything captured, it reads as confusing
            (feedback de Saúl Pérez, 2026-10-19). */}
        {step < 2 ? (
          <>
            <Button
              variant="ghost"
              disabled={isPending}
              onClick={() => skipMutation.mutate()}
            >
              {t("wizard.notNow")}
            </Button>
            <div className="flex gap-2">
              <Button
                variant="outline"
                disabled={isPending}
                onClick={skipCurrentStep}
              >
                {t("wizard.skipStep")}
              </Button>
              <Button
                disabled={isPending || (step === 0 && !!birthDateError)}
                onClick={() => setStep(step + 1)}
              >
                {t("wizard.continue")}
              </Button>
            </div>
          </>
        ) : (
          <LoadingButton
            className="ml-auto"
            loading={saveMutation.isPending}
            onClick={() => saveMutation.mutate()}
          >
            {t("wizard.save")}
          </LoadingButton>
        )}
      </CardFooter>
    </Card>
  )
}

export default OnboardingWizard
