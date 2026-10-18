import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import { type HealthRecordCreate, HealthRecordsService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
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
  dose: z
    .string()
    .min(1, { message: i18n.t("records:validation.doseRequired") }),
  valid_from: z
    .string()
    .min(1, { message: i18n.t("records:validation.validFromRequired") }),
  valid_to: z
    .string()
    .min(1, { message: i18n.t("records:validation.validToRequired") }),
})

type FormData = z.infer<typeof formSchema>

const AddPrescription = () => {
  const { t } = useTranslation("records")
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      title: "",
      occurred_on: "",
      dose: "",
      valid_from: "",
      valid_to: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: HealthRecordCreate) =>
      HealthRecordsService.recordsCreateHealthRecord({ body: data }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["health-records"] })
      showSuccessToast(t("addPrescription.successToast"))
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = (data: FormData) => {
    mutation.mutate({
      record_type: "prescription",
      title: data.title,
      occurred_on: data.occurred_on,
      dose: data.dose || null,
      valid_from: data.valid_from || null,
      valid_to: data.valid_to || null,
    })
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant="outline">
          <Plus className="mr-2" />
          {t("addPrescription.button")}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("addPrescription.dialogTitle")}</DialogTitle>
          <DialogDescription>
            {t("addPrescription.dialogDescription")}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} noValidate>
            <div className="grid gap-4 py-4">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      {t("fields.medication")}{" "}
                      <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input type="text" {...field} required />
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
                      <Input type="date" {...field} required />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="dose"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      {t("fields.dose")}{" "}
                      <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input type="text" {...field} required />
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
                    <FormLabel>
                      {t("fields.validFrom")}{" "}
                      <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input type="date" {...field} required />
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
                    <FormLabel>
                      {t("fields.validTo")}{" "}
                      <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input type="date" {...field} required />
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
      </DialogContent>
    </Dialog>
  )
}

export default AddPrescription
