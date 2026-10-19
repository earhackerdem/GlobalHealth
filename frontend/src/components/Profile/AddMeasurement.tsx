import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import { ProfileService } from "@/client"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"
import i18n from "@/i18n"
import { handleError } from "@/utils"

const formSchema = z
  .object({
    type: z.enum(["weight", "height"]),
    value: z.string().min(1, {
      message: i18n.t("profile:validation.measurementValueRequired"),
    }),
  })
  .superRefine((data, ctx) => {
    if (!data.value) return
    // Mirror the API's plausibility ranges (design.md decision 4) so the 422
    // never has to fire for a well-behaved client: weight (0, 400] kg,
    // height [30, 250] cm.
    const value = Number(data.value)
    if (data.type === "weight" && !(value > 0 && value <= 400)) {
      ctx.addIssue({
        code: "custom",
        path: ["value"],
        message: i18n.t("profile:validation.weightRange"),
      })
    }
    if (data.type === "height" && !(value >= 30 && value <= 250)) {
      ctx.addIssue({
        code: "custom",
        path: ["value"],
        message: i18n.t("profile:validation.heightRange"),
      })
    }
  })

type FormData = z.infer<typeof formSchema>

/**
 * "Registrar medición" on /perfil (finding G1): a new weight or height capture
 * without re-entering the onboarding. Always an INSERT server-side (a new row
 * with measured_on = today), never an update of a previous capture.
 */
function AddMeasurement() {
  const { t } = useTranslation("profile")
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      type: "weight",
      value: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) =>
      ProfileService.createMeasurement({
        body: { type: data.type, value: Number(data.value) },
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["profile"] })
      showSuccessToast(t("measurements.savedToast"))
      form.reset()
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
  })

  const handleOpenChange = (open: boolean) => {
    if (open) {
      form.reset()
    }
    setIsOpen(open)
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline" data-testid="add-measurement">
          {t("measurements.add")}
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md" data-testid="measurement-dialog">
        <DialogHeader>
          <DialogTitle>{t("measurements.dialogTitle")}</DialogTitle>
          <DialogDescription>
            {t("measurements.dialogDescription")}
          </DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit((data) => mutation.mutate(data))}
            noValidate
          >
            <div className="grid gap-4 py-2">
              <FormField
                control={form.control}
                name="type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t("measurements.typeLabel")}</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange}>
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="weight">
                          {t("fields.weight")}
                        </SelectItem>
                        <SelectItem value="height">
                          {t("fields.height")}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="value"
                render={({ field }) => (
                  <FormItem>
                    {/* The value label carries the unit of the chosen type:
                        "Peso (kg)" / "Estatura (cm)". */}
                    <FormLabel>
                      {t(`fields.${form.watch("type")}`)}{" "}
                      <span className="text-destructive">*</span>
                    </FormLabel>
                    <FormControl>
                      <Input type="number" step="0.1" {...field} required />
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
                {t("common:actions.save")}
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default AddMeasurement
