import { zodResolver } from "@hookform/resolvers/zod"
import { X } from "lucide-react"
import { useFieldArray, useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import type { HealthRecordMedicineCreate } from "@/client"
import { Button } from "@/components/ui/button"
import { DialogClose, DialogFooter } from "@/components/ui/dialog"
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
import i18n from "@/i18n"

const medicineSchema = z.object({
  name: z.string(),
  dose: z.string(),
  frequency: z.string(),
})

export const prescriptionFormSchema = z.object({
  professional: z.string(),
  occurred_on: z
    .string()
    .min(1, { message: i18n.t("records:validation.dateRequired") }),
  medicines: z.array(medicineSchema).refine(
    // At least one medicine with a name: empty rows do not count (AC-1).
    (medicines) => medicines.some((m) => m.name.trim().length > 0),
    { message: i18n.t("records:validation.medicinesRequired") },
  ),
  diagnosis: z.string(),
  notes: z.string(),
})

export type PrescriptionFormData = z.infer<typeof prescriptionFormSchema>

export const emptyMedicineRow = { name: "", dose: "", frequency: "" }

/** Rows with a name become the API payload; blanks map to null, never "". */
export function medicinesPayload(
  data: PrescriptionFormData,
): HealthRecordMedicineCreate[] {
  return data.medicines
    .filter((m) => m.name.trim().length > 0)
    .map((m) => ({
      name: m.name.trim(),
      dose: m.dose.trim() || null,
      frequency: m.frequency.trim() || null,
    }))
}

interface PrescriptionFormProps {
  defaultValues: PrescriptionFormData
  pending: boolean
  onSubmit: (data: PrescriptionFormData) => void
}

/**
 * Shared capture/edit form for a prescription (prototype
 * product/prototipos/receta-primero.html): doctor, date, 1..N medicine rows,
 * optional diagnosis and notes. Validation mirrors the API contract with zod
 * (noValidate), es-MX messages.
 */
const PrescriptionForm = ({
  defaultValues,
  pending,
  onSubmit,
}: PrescriptionFormProps) => {
  const { t } = useTranslation("records")

  const form = useForm<PrescriptionFormData>({
    resolver: zodResolver(prescriptionFormSchema),
    mode: "onSubmit",
    criteriaMode: "all",
    defaultValues,
  })

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "medicines",
  })

  const medicinesError =
    form.formState.errors.medicines?.root?.message ??
    form.formState.errors.medicines?.message

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} noValidate>
        <div className="grid gap-4 py-4">
          <FormField
            control={form.control}
            name="professional"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("prescriptionForm.doctor")}</FormLabel>
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
                <FormLabel>{t("prescriptionForm.date")}</FormLabel>
                <FormControl>
                  <Input type="date" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="flex flex-col gap-3">
            <p className="text-sm font-medium">
              {t("prescriptionForm.medicines")}
            </p>
            {fields.map((row, index) => (
              <div key={row.id} className="flex items-end gap-2">
                <div className="grid flex-1 gap-2 sm:grid-cols-3">
                  <FormField
                    control={form.control}
                    name={`medicines.${index}.name`}
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          {t("prescriptionForm.medicineName")}
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
                    name={`medicines.${index}.dose`}
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          {t("prescriptionForm.medicineDose")}
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
                    name={`medicines.${index}.frequency`}
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          {t("prescriptionForm.medicineFrequency")}
                        </FormLabel>
                        <FormControl>
                          <Input type="text" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  aria-label={t("prescriptionForm.removeMedicine")}
                  // Minimum one row, like the prototype: removing the last
                  // row is a no-op.
                  onClick={() => {
                    if (fields.length > 1) {
                      remove(index)
                    }
                  }}
                >
                  <X />
                </Button>
              </div>
            ))}
            {medicinesError && (
              <p className="text-sm font-medium text-destructive">
                {medicinesError}
              </p>
            )}
            <Button
              type="button"
              variant="link"
              className="self-start px-0"
              onClick={() => append({ ...emptyMedicineRow })}
            >
              {t("prescriptionForm.addMedicine")}
            </Button>
          </div>

          <FormField
            control={form.control}
            name="diagnosis"
            render={({ field }) => (
              <FormItem>
                <FormLabel>{t("prescriptionForm.diagnosis")}</FormLabel>
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
                <FormLabel>{t("prescriptionForm.notes")}</FormLabel>
                <FormControl>
                  <Input type="text" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" disabled={pending}>
              {t("common:actions.cancel")}
            </Button>
          </DialogClose>
          <LoadingButton type="submit" loading={pending}>
            {t("prescriptionForm.submit")}
          </LoadingButton>
        </DialogFooter>
      </form>
    </Form>
  )
}

export default PrescriptionForm
