import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Pencil } from "lucide-react"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import {
  type HealthRecordPublic,
  HealthRecordsService,
  type HealthRecordUpdate,
} from "@/client"
import PrescriptionForm, {
  emptyMedicineRow,
  medicinesPayload,
  type PrescriptionFormData,
} from "@/components/Records/PrescriptionForm"
import { useRecordDialogs } from "@/components/Records/RecordDialogsContext"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { DropdownMenuItem } from "@/components/ui/dropdown-menu"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import i18n from "@/i18n"
import { handleError } from "@/utils"

const diagnosisSchema = z.object({
  title: z
    .string()
    .min(1, { message: i18n.t("records:validation.titleRequired") }),
  occurred_on: z
    .string()
    .min(1, { message: i18n.t("records:validation.dateRequired") }),
  professional: z.string().optional(),
  notes: z.string().optional(),
})

type DiagnosisFormData = z.infer<typeof diagnosisSchema>

interface EditRecordProps {
  record: HealthRecordPublic
}

/**
 * "Editar registro" menu item. It only ASKS the page-level provider to open
 * the edit dialog by id: the dialog itself must not live inside the dropdown
 * content, which Radix unmounts when the menu closes (e.g. on focus loss) —
 * that unmount was the reported data-loss bug (delta 2026-10-18, AC8).
 */
const EditRecord = ({ record }: EditRecordProps) => {
  const { t } = useTranslation("records")
  const { openEdit } = useRecordDialogs()

  return (
    <DropdownMenuItem onSelect={() => openEdit(record.id)}>
      <Pencil />
      {t("editRecord.menuItem")}
    </DropdownMenuItem>
  )
}

interface EditRecordDialogProps {
  record: HealthRecordPublic
  onClose: () => void
}

/**
 * The actual edit dialog, rendered at page level by RecordDialogsProvider.
 * It stays mounted across list refetches (same record id → same element), so
 * the form keeps whatever the user already typed (AC8).
 */
export const EditRecordDialog = ({ record, onClose }: EditRecordDialogProps) => {
  const { t } = useTranslation("records")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const isDiagnosis = record.record_type === "diagnosis"

  const form = useForm<DiagnosisFormData>({
    resolver: zodResolver(diagnosisSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      title: record.title ?? "",
      occurred_on: record.occurred_on,
      professional: record.professional ?? "",
      notes: record.notes ?? "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: HealthRecordUpdate) =>
      HealthRecordsService.recordsUpdateHealthRecord({
        path: { id: record.id },
        body: data,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["health-records"] })
      showSuccessToast(t("editRecord.successToast"))
      onClose()
    },
    onError: handleError.bind(showErrorToast),
  })

  // record_type is immutable: it is never sent in the PATCH body.
  const onSubmitDiagnosis = (data: DiagnosisFormData) => {
    mutation.mutate({
      title: data.title,
      occurred_on: data.occurred_on,
      professional: data.professional || null,
      notes: data.notes || null,
    })
  }

  // `medicines` in the PATCH is a FULL replacement of the list (design,
  // Decision 2): the form always submits the resulting list.
  const onSubmitPrescription = (data: PrescriptionFormData) => {
    mutation.mutate({
      occurred_on: data.occurred_on,
      professional: data.professional.trim() || null,
      diagnosis: data.diagnosis.trim() || null,
      notes: data.notes.trim() || null,
      medicines: medicinesPayload(data),
    })
  }

  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open) {
          onClose()
        }
      }}
    >
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("editRecord.dialogTitle")}</DialogTitle>
          <DialogDescription>
            {t("editRecord.dialogDescription")}
          </DialogDescription>
        </DialogHeader>
        {isDiagnosis ? (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmitDiagnosis)} noValidate>
              <div className="grid gap-4 py-4">
                <FormField
                  control={form.control}
                  name="title"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>
                        {t("fields.diagnosis")}{" "}
                        <span className="text-destructive">*</span>
                      </FormLabel>
                      <FormControl>
                        <Input type="text" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="occurred_on"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>
                        {t("fields.date")}{" "}
                        <span className="text-destructive">*</span>
                      </FormLabel>
                      <FormControl>
                        <Input type="date" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="professional"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("fields.professional")}</FormLabel>
                      <FormControl>
                        <Input type="text" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="notes"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>{t("fields.notes")}</FormLabel>
                      <FormControl>
                        <Textarea {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <DialogFooter>
                <DialogClose asChild>
                  <Button variant="outline" disabled={mutation.isPending}>
                    {t("common:actions.cancel")}
                  </Button>
                </DialogClose>
                <LoadingButton type="submit" loading={mutation.isPending}>
                  {t("actions.save")}
                </LoadingButton>
              </DialogFooter>
            </form>
          </Form>
        ) : (
          <PrescriptionForm
            defaultValues={{
              professional: record.professional ?? "",
              occurred_on: record.occurred_on,
              medicines: record.medicines.length
                ? record.medicines.map((m) => ({
                    name: m.name,
                    dose: m.dose ?? "",
                    frequency: m.frequency ?? "",
                  }))
                : [{ ...emptyMedicineRow }],
              diagnosis: record.diagnosis ?? "",
              notes: record.notes ?? "",
            }}
            pending={mutation.isPending}
            onSubmit={onSubmitPrescription}
          />
        )}
      </DialogContent>
    </Dialog>
  )
}

export default EditRecord
