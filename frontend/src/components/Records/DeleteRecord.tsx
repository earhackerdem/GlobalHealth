import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Trash2 } from "lucide-react"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { useTranslation } from "react-i18next"

import { HealthRecordsService } from "@/client"
import { chronicTitle } from "@/components/Profile/history"
import { getHistoryQueryOptions } from "@/components/Profile/queries"
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
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface DeleteRecordProps {
  id: string
  isDiagnosis: boolean
  onSuccess: () => void
}

const DeleteRecord = ({ id, isDiagnosis, onSuccess }: DeleteRecordProps) => {
  const { t } = useTranslation("records")
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { handleSubmit } = useForm()

  // B-5: a diagnosis may back chronic entries (only a diagnosis can: the API
  // rejects any other link), so the dialog names them, read from
  // GET /profile/history while it is open; a prescription never asks. While
  // it loads, "Eliminar" waits; if it fails, the dialog says so and the
  // patient can still delete (ARCO). No retries: the default three (~7 s)
  // would keep "Eliminar" disabled with nothing on screen saying why.
  const {
    data: history,
    isLoading: historyLoading,
    isError: historyFailed,
  } = useQuery({
    ...getHistoryQueryOptions(),
    enabled: isOpen && isDiagnosis,
    retry: false,
  })
  const backedNames = (history?.data ?? []).flatMap((entry) =>
    entry.section === "chronic" && entry.diagnosis_id === id
      ? [`«${chronicTitle(entry, t)}»`]
      : [],
  )

  const mutation = useMutation({
    mutationFn: (recordId: string) =>
      HealthRecordsService.recordsDeleteHealthRecord({
        path: { id: recordId },
      }),
    onSuccess: async () => {
      // The API unlinks the chronic entries it backed (same transaction).
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["health-records"] }),
        queryClient.invalidateQueries({ queryKey: ["history"] }),
      ])
      showSuccessToast(t("deleteRecord.successToast"))
      setIsOpen(false)
      onSuccess()
    },
    onError: handleError.bind(showErrorToast),
  })

  const onSubmit = () => {
    mutation.mutate(id)
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuItem
        variant="destructive"
        onSelect={(e) => e.preventDefault()}
        onClick={() => setIsOpen(true)}
      >
        <Trash2 />
        {t("deleteRecord.menuItem")}
      </DropdownMenuItem>
      <DialogContent className="sm:max-w-md">
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>{t("deleteRecord.dialogTitle")}</DialogTitle>
            <DialogDescription>
              {t("deleteRecord.dialogDescription")}
              {/* Live: the line arrives after the history loads. */}
              <span aria-live="polite">
                {backedNames.length > 0 && (
                  <span className="mt-2 block">
                    {t("deleteRecord.backsChronic", {
                      count: backedNames.length,
                      names: backedNames.join(", "),
                    })}
                  </span>
                )}
                {historyFailed && (
                  <span className="mt-2 block">
                    {t("deleteRecord.backsChronicUnknown")}
                  </span>
                )}
              </span>
            </DialogDescription>
          </DialogHeader>

          <DialogFooter className="mt-4">
            <DialogClose asChild>
              <Button variant="outline" disabled={mutation.isPending}>
                {t("common:actions.cancel")}
              </Button>
            </DialogClose>
            <LoadingButton
              variant="destructive"
              type="submit"
              loading={mutation.isPending}
              disabled={historyLoading}
            >
              {t("deleteRecord.confirmButton")}
            </LoadingButton>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

export default DeleteRecord
