import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { z } from "zod"

import { type PatientProfilePublic, ProfileService } from "@/client"
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
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import i18n from "@/i18n"
import { handleError } from "@/utils"
import { localTodayIso } from "./format"

const SEXES = ["female", "male", "unspecified"] as const

const formSchema = z.object({
  // Empty is a valid state (the profile may be partial); a captured date must
  // fall in [1900-01-01, today], mirrored from the API so the 422 never has
  // to fire for a well-behaved client — the message shows inline, es-MX.
  birth_date: z
    .string()
    .refine((value) => !value || value <= localTodayIso(), {
      message: i18n.t("profile:validation.birthDateFuture"),
    })
    .refine((value) => !value || value >= "1900-01-01", {
      message: i18n.t("profile:validation.birthDateTooOld"),
    }),
  sex: z.enum(SEXES).or(z.literal("")),
  allergies: z.string(),
})

type FormData = z.infer<typeof formSchema>

/**
 * "Editar datos básicos" dialog on /perfil: a full PUT /profile of the three
 * basic fields (partial on the wire isn't needed — the dialog always shows the
 * complete current state; an emptied field sends null, which clears it).
 */
function EditBasicData({ profile }: { profile: PatientProfilePublic }) {
  const { t } = useTranslation("profile")
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      birth_date: "",
      sex: "",
      allergies: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: FormData) =>
      ProfileService.updateProfile({
        body: {
          birth_date: data.birth_date || null,
          sex: data.sex || null,
          allergies: data.allergies.trim() || null,
        },
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["profile"] })
      showSuccessToast(t("basic.savedToast"))
      setIsOpen(false)
    },
    onError: handleError.bind(showErrorToast),
  })

  const handleOpenChange = (open: boolean) => {
    if (open) {
      // Seed the form from the current profile on every open.
      form.reset({
        birth_date: profile.birth_date ?? "",
        sex: (profile.sex ?? "") as FormData["sex"],
        allergies: profile.allergies ?? "",
      })
    }
    setIsOpen(open)
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline">{t("basic.edit")}</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("basic.edit")}</DialogTitle>
          <DialogDescription>{t("basic.editDescription")}</DialogDescription>
        </DialogHeader>
        <Form {...form}>
          <form
            onSubmit={form.handleSubmit((data) => mutation.mutate(data))}
            noValidate
          >
            <div className="grid gap-4 py-2">
              <FormField
                control={form.control}
                name="birth_date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t("fields.birthDate")}</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="sex"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t("fields.sex")}</FormLabel>
                    <Select value={field.value} onValueChange={field.onChange}>
                      <FormControl>
                        <SelectTrigger className="w-full">
                          <SelectValue
                            placeholder={t("sexOptions.placeholder")}
                          />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {SEXES.map((sex) => (
                          <SelectItem key={sex} value={sex}>
                            {t(`sexOptions.${sex}`)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="allergies"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>{t("fields.allergies")}</FormLabel>
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
                {t("common:actions.save")}
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}

export default EditBasicData
