import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Loader2 } from "lucide-react"
import { type FormEvent, useId, useLayoutEffect, useRef, useState } from "react"
import { useTranslation } from "react-i18next"

import { ProfileService, type Work } from "@/client"
import { zWork } from "@/client/zod.gen"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import ChipGroup, { ChipMultiGroup } from "./ChipGroup"
import { getWorkQueryOptions } from "./queries"

type Status = NonNullable<Work["status"]>
type Exposure = NonNullable<Work["exposures"]>[number]
type Shift = NonNullable<Work["shift"]>
/** "Nada de esto": the exclusive chip of the exposures, sent as `no_exposures`. */
type ExposureChip = Exposure | "none"

/** The options and the lengths, from the generated schema (as HabitsForm). */
const WORK_STATUSES = zWork.shape.status.unwrap().unwrap().options
const WORK_EXPOSURES = zWork.shape.exposures.unwrap().element.options
const WORK_SHIFTS = zWork.shape.shift.unwrap().unwrap().options
const OCCUPATION_MAX =
  zWork.shape.occupation.unwrap().unwrap().maxLength ?? undefined
const LONGEST_JOB_MAX =
  zWork.shape.longest_job.unwrap().unwrap().maxLength ?? undefined

type Draft = {
  status: Status | null
  occupation: string
  longestJob: string
  exposures: ExposureChip[]
  shift: Shift | null
}

const draftFrom = (work: Work): Draft => ({
  status: work.status ?? null,
  occupation: work.occupation ?? "",
  longestJob: work.longest_job ?? "",
  exposures: work.no_exposures ? ["none"] : [...(work.exposures ?? [])],
  shift: work.shift ?? null,
})

const isExposure = (value: ExposureChip): value is Exposure => value !== "none"

/**
 * The whole block for PUT /profile/work: what only applies to "Trabajo" goes
 * empty with any other status, as the server normalizes it too.
 */
const bodyFrom = (draft: Draft): Work => {
  const employed = draft.status === "employed"
  return {
    status: draft.status,
    occupation: (employed && draft.occupation.trim()) || null,
    longest_job: draft.longestJob.trim() || null,
    exposures: employed ? draft.exposures.filter(isExposure) : [],
    no_exposures: employed && draft.exposures.includes("none"),
    shift: employed ? draft.shift : null,
  }
}

/**
 * "Editar trabajo" dialog on /perfil (perfil-trabajo, design.md → Interface
 * contract): "Hoy…" with one status, and only with "Trabajo" what the
 * patient does, the exposures (with "Nada de esto", exclusive) and the
 * shift; the longest job always. Every answer is optional. "Guardar" sends
 * the whole block; while that PUT is in flight "Guardar", "Cancelar" and the
 * chips are aria-disabled and the boxes read-only (D20), as in HabitsForm.
 * Nothing here scores or labels the answers (C-6).
 */
function EditWork({ work }: { work: Work }) {
  const { t } = useTranslation("profile")
  const idPrefix = useId()
  const formRef = useRef<HTMLFormElement>(null)
  const [isOpen, setIsOpen] = useState(false)
  const [draft, setDraft] = useState<Draft>(() => draftFrom(work))
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (body: Work) => ProfileService.updateWork({ body }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: getWorkQueryOptions().queryKey,
      })
      showSuccessToast(t("work.savedToast"))
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
  })
  const busy = mutation.isPending

  // ChipGroup has no disabled prop and stays untouched (design.md): while
  // saving, its buttons get aria-disabled from here, as in HabitsForm.
  useLayoutEffect(() => {
    const buttons =
      formRef.current?.querySelectorAll<HTMLButtonElement>("fieldset button")
    for (const button of buttons ?? []) {
      if (busy) button.setAttribute("aria-disabled", "true")
      else button.removeAttribute("aria-disabled")
    }
  }, [busy])

  const handleOpenChange = (open: boolean) => {
    // While saving the dialog stays: its end closes it.
    if (busy) return
    if (open) setDraft(draftFrom(work))
    setIsOpen(open)
  }

  const choose = <K extends keyof Draft>(key: K, value: Draft[K]) => {
    if (busy) return
    setDraft((current) => ({ ...current, [key]: value }))
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (busy) return
    mutation.mutate(bodyFrom(draft))
  }

  const occupationId = `${idPrefix}-occupation`
  const longestJobId = `${idPrefix}-longest-job`

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline">{t("work.edit")}</Button>
      </DialogTrigger>
      {/* D20: while saving, the close X («Cerrar») is not offered either. */}
      <DialogContent
        showCloseButton={!busy}
        className="max-h-[90dvh] overflow-y-auto sm:max-w-md"
      >
        <DialogHeader>
          <DialogTitle>{t("work.title")}</DialogTitle>
          <DialogDescription>{t("work.description")}</DialogDescription>
        </DialogHeader>
        <form
          ref={formRef}
          onSubmit={handleSubmit}
          noValidate
          className={`grid min-w-0 gap-4 ${
            busy
              ? "[&_fieldset_button]:cursor-not-allowed [&_fieldset_button]:opacity-50"
              : ""
          }`}
        >
          <ChipGroup
            label={t("work.fields.status")}
            options={WORK_STATUSES.map((status) => ({
              value: status,
              label: t(`work.status.${status}`),
            }))}
            value={draft.status}
            onChange={(next) => choose("status", next)}
          />

          {draft.status === "employed" && (
            <>
              <div className="grid gap-1.5">
                <Label htmlFor={occupationId}>
                  {t("work.fields.occupation")}
                </Label>
                <Input
                  id={occupationId}
                  autoComplete="off"
                  maxLength={OCCUPATION_MAX}
                  placeholder={t("work.fields.occupationPlaceholder")}
                  value={draft.occupation}
                  readOnly={busy}
                  onChange={(e) => choose("occupation", e.target.value)}
                />
              </div>

              <ChipMultiGroup
                label={t("work.fields.exposures")}
                options={WORK_EXPOSURES.map((exposure) => ({
                  value: exposure as ExposureChip,
                  label: t(`work.exposures.${exposure}`),
                }))}
                exclusive={{
                  value: "none" as const,
                  label: t("work.exposures.none"),
                }}
                values={draft.exposures}
                onChange={(next) => choose("exposures", next)}
              />

              <ChipGroup
                label={t("work.fields.shift")}
                options={WORK_SHIFTS.map((shift) => ({
                  value: shift,
                  label: t(`work.shift.${shift}`),
                }))}
                value={draft.shift}
                onChange={(next) => choose("shift", next)}
              />
            </>
          )}

          <div className="grid gap-1.5">
            <Label htmlFor={longestJobId}>{t("work.fields.longestJob")}</Label>
            <Input
              id={longestJobId}
              autoComplete="off"
              maxLength={LONGEST_JOB_MAX}
              placeholder={t("work.fields.longestJobPlaceholder")}
              value={draft.longestJob}
              readOnly={busy}
              onChange={(e) => choose("longestJob", e.target.value)}
            />
          </div>

          {/* D20: aria-disabled, not disabled, so the focus stays on
              "Guardar" while it saves; the handlers ignore the press. */}
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              aria-disabled={busy || undefined}
              className="aria-disabled:opacity-50"
              onClick={() => handleOpenChange(false)}
            >
              {t("common:actions.cancel")}
            </Button>
            <Button
              type="submit"
              aria-disabled={busy || undefined}
              className="aria-disabled:opacity-50"
            >
              {busy && <Loader2 className="mr-2 h-5 w-5 animate-spin" />}
              {busy ? t("work.saving") : t("common:actions.save")}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default EditWork
