import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import {
  type PatientProfilePublic,
  type PatientProfileUpdate,
  ProfileService,
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
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { LoadingButton } from "@/components/ui/loading-button"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

type Sex = NonNullable<PatientProfileUpdate["sex"]>

const SELECT_CLASS =
  "border-input h-9 w-full rounded-md border bg-transparent px-3 text-sm shadow-xs outline-none focus-visible:ring-[3px] focus-visible:ring-ring/50 dark:bg-input/30"

/**
 * "Editar datos básicos" dialog on /perfil: a full PUT /profile of the three
 * basic fields (partial on the wire isn't needed — the dialog always shows the
 * complete current state; an emptied field sends null, which clears it).
 */
function EditBasicData({ profile }: { profile: PatientProfilePublic }) {
  const { t } = useTranslation("profile")
  const [isOpen, setIsOpen] = useState(false)
  const [birthDate, setBirthDate] = useState("")
  const [sex, setSex] = useState("")
  const [allergies, setAllergies] = useState("")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: () =>
      ProfileService.updateProfile({
        body: {
          birth_date: birthDate || null,
          sex: (sex || null) as Sex | null,
          allergies: allergies.trim() || null,
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
      setBirthDate(profile.birth_date ?? "")
      setSex(profile.sex ?? "")
      setAllergies(profile.allergies ?? "")
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
        <div className="grid gap-4 py-2">
          <div className="grid gap-2">
            <Label htmlFor="edit-birth-date">{t("fields.birthDate")}</Label>
            <Input
              id="edit-birth-date"
              type="date"
              value={birthDate}
              onChange={(e) => setBirthDate(e.target.value)}
            />
          </div>
          <div className="grid gap-2">
            <Label htmlFor="edit-sex">{t("fields.sex")}</Label>
            <select
              id="edit-sex"
              className={SELECT_CLASS}
              value={sex}
              onChange={(e) => setSex(e.target.value)}
            >
              <option value="">{t("sexOptions.placeholder")}</option>
              <option value="female">{t("sexOptions.female")}</option>
              <option value="male">{t("sexOptions.male")}</option>
              <option value="unspecified">{t("sexOptions.unspecified")}</option>
            </select>
          </div>
          <div className="grid gap-2">
            <Label htmlFor="edit-allergies">{t("fields.allergies")}</Label>
            <Textarea
              id="edit-allergies"
              value={allergies}
              onChange={(e) => setAllergies(e.target.value)}
            />
          </div>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" disabled={mutation.isPending}>
              {t("common:actions.cancel")}
            </Button>
          </DialogClose>
          <LoadingButton
            loading={mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            {t("basic.save")}
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default EditBasicData
