import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Keyboard } from "lucide-react"
import { useState } from "react"
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
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

/** Manual capture of a prescription ("A mano"): medicines[] 1..N, optional
 * diagnosis, no validity dates (new model, receta-mexicana). */
const AddPrescription = () => {
  const { t } = useTranslation("records")
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (data: HealthRecordCreate) =>
      HealthRecordsService.recordsCreateHealthRecord({ body: data }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["health-records"] })
      showSuccessToast(t("addPrescription.successToast"))
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: PrescriptionFormData) => {
    mutation.mutate({
      record_type: "prescription",
      occurred_on: data.occurred_on,
      professional: data.professional.trim() || null,
      diagnosis: data.diagnosis.trim() || null,
      notes: data.notes.trim() || null,
      medicines: medicinesPayload(data),
    })
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Keyboard className="mr-2" />
          {t("addPrescription.button")}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("addPrescription.dialogTitle")}</DialogTitle>
          <DialogDescription>
            {t("addPrescription.dialogDescription")}
          </DialogDescription>
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
        />
      </DialogContent>
    </Dialog>
  )
}

export default AddPrescription
