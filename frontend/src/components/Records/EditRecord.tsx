import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Pencil } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import {
  type HealthRecordPublic,
  HealthRecordsService,
  type HealthRecordUpdate,
} from "@/client"
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
import useCustomToast from "@/hooks/useCustomToast"
import i18n from "@/i18n"
import { handleError } from "@/utils"

const formSchema = z.object({
  title: z
    .string()
    .min(1, { message: i18n.t("records:validation.titleRequired") }),
  occurred_on: z
    .string()
    .min(1, { message: i18n.t("records:validation.dateRequired") }),
  professional: z.string().optional(),
  notes: z.string().optional(),
  dose: z.string().optional(),
  valid_from: z.string().optional(),
  valid_to: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

interface EditRecordProps {
  record: HealthRecordPublic
  onSuccess: () => void
}

const EditRecord = ({ record, onSuccess }: EditRecordProps) => {
  const { t } = useTranslation("records")
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const isDiagnosis = record.record_type === "diagnosis"

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      title: record.title,
      occurred_on: record.occurred_on,
      professional: record.professional ?? "",
      notes: record.notes ?? "",
      dose: record.dose ?? "",
      valid_from: record.valid_from ?? "",
      valid_to: record.valid_to ?? "",
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
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: FormData) => {
    // record_type is immutable: it is never sent in the PATCH body.
    const body: HealthRecordUpdate = isDiagnosis
      ? {
          title: data.title,
          occurred_on: data.occurred_on,
          professional: data.professional || null,
          notes: data.notes || null,
        }
      : {
          title: data.title,
          occurred_on: data.occurred_on,
          dose: data.dose || null,
          valid_from: data.valid_from || null,
          valid_to: data.valid_to || null,
        }
    mutation.mutate(body)
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
      >
        <Pencil />
        {t("editRecord.menuItem")}
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <DialogHeader>
              <DialogTitle>{t("editRecord.dialogTitle")}</DialogTitle>
              <DialogDescription>
                {t("editRecord.dialogDescription")}
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      {isDiagnosis
                        ? t("fields.diagnosis")
                        : t("fields.medication")}{" "}
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

              {isDiagnosis ? (
                <>
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
                          <Input type="text" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </>
              ) : (
                <>
                  <FormField
                    control={form.control}
                    name="dose"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t("fields.dose")}</FormLabel>
                        <FormControl>
                          <Input type="text" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="valid_from"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t("fields.validFrom")}</FormLabel>
                        <FormControl>
                          <Input type="date" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name="valid_to"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>{t("fields.validTo")}</FormLabel>
                        <FormControl>
                          <Input type="date" {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </>
              )}
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
      </DialogContent>
    </Dialog>
  )
}

export default EditRecord
