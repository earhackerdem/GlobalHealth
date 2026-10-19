import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Keyboard, Mic, Paperclip, ScanLine } from "lucide-react"
import { useRef, useState } from "react"
import { useTranslation } from "react-i18next"

import { type HealthRecordCreate, HealthRecordsService } from "@/client"
import PrescriptionForm, {
  emptyMedicineRow,
  medicinesPayload,
  type PrescriptionFormData,
} from "@/components/Records/PrescriptionForm"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

/** Manual capture of a prescription ("Registrar receta"): medicines[] 1..N,
 * optional diagnosis, no validity dates (new model, receta-mexicana), plus an
 * optional photo/PDF attached in the same form (delta AC11). */
const AddPrescription = () => {
  const { t } = useTranslation("records")
  const [isOpen, setIsOpen] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    // The record is created FIRST; the optional attachment is uploaded after
    // the 201 with the existing attachments API (design, Decision 6). If the
    // upload fails the prescription already exists: the error is reported
    // without losing it.
    mutationFn: async (vars: {
      data: HealthRecordCreate
      file: File | null
    }) => {
      const created = (
        await HealthRecordsService.recordsCreateHealthRecord({
          body: vars.data,
        })
      ).data
      if (!vars.file) {
        return { attachmentFailed: false }
      }
      try {
        await HealthRecordsService.recordsCreateHealthRecordAttachment({
          path: { id: created.id },
          body: { file: vars.file },
        })
        return { attachmentFailed: false }
      } catch {
        return { attachmentFailed: true }
      }
    },
    onSuccess: async ({ attachmentFailed }) => {
      await queryClient.invalidateQueries({ queryKey: ["health-records"] })
      if (attachmentFailed) {
        showErrorToast(t("addPrescription.attachmentFailedToast"))
      }
      showSuccessToast(t("addPrescription.successToast"))
      setFile(null)
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: PrescriptionFormData) => {
    mutation.mutate({
      data: {
        record_type: "prescription",
        occurred_on: data.occurred_on,
        professional: data.professional.trim() || null,
        diagnosis: data.diagnosis.trim() || null,
        notes: data.notes.trim() || null,
        medicines: medicinesPayload(data),
      },
      file,
    })
  }

  return (
    <Dialog
      open={isOpen}
      onOpenChange={(open) => {
        setIsOpen(open)
        if (!open) {
          setFile(null)
        }
      }}
    >
      <DialogTrigger asChild>
        <Button variant="outline">
          <Keyboard className="mr-2" />
          {t("addPrescription.button")}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("addPrescription.dialogTitle")}</DialogTitle>
          <DialogDescription>
            {t("addPrescription.dialogDescription")}
          </DialogDescription>
          {/* Capture-ladder placeholders (delta): disabled, announced as
              "Próximamente" with VISIBLE text — a title on a disabled button
              reaches no one: no hover (pointer-events: none), no keyboard,
              no touch (finding K3). aria-describedby links it for AT. */}
          <div className="flex flex-wrap items-center gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled
              aria-describedby="capture-coming-soon"
            >
              <Mic className="mr-2" />
              {t("addPrescription.dictate")}
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled
              aria-describedby="capture-coming-soon"
            >
              <ScanLine className="mr-2" />
              {t("addPrescription.scan")}
            </Button>
            <span
              id="capture-coming-soon"
              className="text-xs text-muted-foreground"
            >
              {t("addPrescription.comingSoon")}
            </span>
          </div>
        </DialogHeader>
        <PrescriptionForm
          defaultValues={{
            professional: "",
            occurred_on: "",
            medicines: [{ ...emptyMedicineRow }],
            diagnosis: "",
            notes: "",
          }}
          pending={mutation.isPending}
          onSubmit={onSubmit}
          attachmentSlot={
            // Hidden native input + es-MX button: the native control renders
            // its "Choose File" text in the browser's language (finding K4).
            <div className="grid gap-2">
              <Label htmlFor="prescription-attachment">
                {t("addPrescription.attachmentLabel")}
              </Label>
              <input
                ref={fileInputRef}
                id="prescription-attachment"
                type="file"
                accept="application/pdf,image/jpeg,image/png"
                className="hidden"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
              />
              <div className="flex min-w-0 items-center gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => fileInputRef.current?.click()}
                >
                  <Paperclip className="mr-2" />
                  {t("addPrescription.attachmentButton")}
                </Button>
                <span className="truncate text-sm text-muted-foreground">
                  {file ? file.name : t("addPrescription.attachmentEmpty")}
                </span>
              </div>
            </div>
          }
        />
      </DialogContent>
    </Dialog>
  )
}

export default AddPrescription
