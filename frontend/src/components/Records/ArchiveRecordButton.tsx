import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"

import { type HealthRecordPublic, HealthRecordsService } from "@/client"
import { Button } from "@/components/ui/button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface ArchiveRecordButtonProps {
  record: HealthRecordPublic
}

/**
 * Manual archive/unarchive of a prescription (AC-8): inline row action, like
 * the prototype card. Archiving is never automatic — there is no validity.
 */
export function ArchiveRecordButton({ record }: ArchiveRecordButtonProps) {
  const { t } = useTranslation("records")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: (archived: boolean) =>
      HealthRecordsService.recordsUpdateHealthRecord({
        path: { id: record.id },
        body: { archived },
      }),
    onSuccess: async (_data, archived) => {
      await queryClient.invalidateQueries({ queryKey: ["health-records"] })
      showSuccessToast(
        archived ? t("archive.archivedToast") : t("archive.unarchivedToast"),
      )
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <Button
      variant="ghost"
      size="sm"
      // The long label may wrap on narrow viewports (K9: at 384px CSS the
      // nowrap button forced the actions column behind horizontal scroll).
      className="h-auto min-h-8 shrink whitespace-normal py-1 text-left"
      disabled={mutation.isPending}
      onClick={() => mutation.mutate(!record.archived)}
    >
      {record.archived ? t("archive.unarchive") : t("archive.archive")}
    </Button>
  )
}
