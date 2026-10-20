import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"

import { type PatientProfilePublic, ProfileService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import ChipGroup from "./ChipGroup"
import { BLOOD_TYPES, type BloodType } from "./history"

const MUTATION_KEY = ["profile", "blood-type"]

/**
 * "Grupo sanguíneo" chips on the transfusions screen (A-7): one value in the
 * 1:1 profile, saved on tap through PUT /profile (absent fields untouched;
 * tapping the chosen chip again sends null, which clears it). Taps are
 * serialized (mutation scope) and shown optimistically, so a quick
 * correction O+ → "No lo sé" always lands in that order.
 */
function BloodTypePicker({ profile }: { profile: PatientProfilePublic }) {
  const { t } = useTranslation("profile")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationKey: MUTATION_KEY,
    scope: { id: "profile-blood-type" },
    mutationFn: async (bloodType: BloodType | null) =>
      (
        await ProfileService.updateProfile({
          body: { blood_type: bloodType },
        })
      ).data,
    onMutate: (bloodType) => {
      queryClient.setQueryData<PatientProfilePublic>(["profile"], (prev) =>
        prev ? { ...prev, blood_type: bloodType } : prev,
      )
    },
    onSuccess: (saved) => {
      // Only the last pending tap writes the server's answer back, so an
      // earlier response never flickers the chips.
      if (queryClient.isMutating({ mutationKey: MUTATION_KEY }) <= 1) {
        queryClient.setQueryData(["profile"], saved)
      }
      showSuccessToast(t("history.bloodType.savedToast"))
    },
    onError: (err) => {
      handleError.call(showErrorToast, err)
      queryClient.invalidateQueries({ queryKey: ["profile"] })
    },
  })

  return (
    <section className="grid gap-2 rounded-lg border p-4">
      <ChipGroup
        label={t("history.bloodType.label")}
        options={BLOOD_TYPES.map((value) => ({
          value,
          label: t(`history.bloodType.options.${value}`),
        }))}
        value={profile.blood_type}
        onChange={(next) => mutation.mutate(next)}
      />
      <p className="text-sm text-muted-foreground">
        {t("history.bloodType.hint")}
      </p>
    </section>
  )
}

export default BloodTypePicker
