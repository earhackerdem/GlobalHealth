import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Download, Trash2, Upload } from "lucide-react"
import { useRef, useState } from "react"
import { useTranslation } from "react-i18next"

import {
  type HealthRecordAttachmentPublic,
  type HealthRecordPublic,
  HealthRecordsService,
} from "@/client"
import { useRecordDialogs } from "@/components/Records/RecordDialogsContext"
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
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import i18n from "@/i18n"
import { handleError } from "@/utils"

function getAttachmentsQueryKey(recordId: string) {
  return ["health-records", recordId, "attachments"]
}

interface AttachmentsPanelProps {
  recordId: string
}

export function AttachmentsPanel({ recordId }: AttachmentsPanelProps) {
  const { t } = useTranslation("records")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const fileInputRef = useRef<HTMLInputElement>(null)
  // Deleting an attachment is destructive: it needs its own confirmation
  // dialog, like deleting a record (finding C2).
  const [pendingDelete, setPendingDelete] =
    useState<HealthRecordAttachmentPublic | null>(null)

  const { data: attachments } = useQuery({
    queryKey: getAttachmentsQueryKey(recordId),
    queryFn: async () =>
      (
        await HealthRecordsService.recordsReadHealthRecordAttachments({
          path: { id: recordId },
        })
      ).data,
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) =>
      HealthRecordsService.recordsCreateHealthRecordAttachment({
        path: { id: recordId },
        body: { file },
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: getAttachmentsQueryKey(recordId),
      })
      showSuccessToast(t("attachments.addedToast"))
    },
    onError: handleError.bind(showErrorToast),
  })

  const deleteMutation = useMutation({
    mutationFn: (attachmentId: string) =>
      HealthRecordsService.recordsDeleteHealthRecordAttachment({
        path: { id: recordId, attachment_id: attachmentId },
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: getAttachmentsQueryKey(recordId),
      })
      showSuccessToast(t("attachments.deletedToast"))
      setPendingDelete(null)
    },
    onError: handleError.bind(showErrorToast),
  })

  // The generated client types this download as JSON; the response is binary
  // (decrypted bytes + Content-Disposition), so we fetch directly with the
  // bearer token and hand the blob to the browser as a named download.
  const handleDownload = async (attachment: HealthRecordAttachmentPublic) => {
    try {
      const baseUrl = import.meta.env.VITE_API_URL ?? ""
      const token = localStorage.getItem("access_token") ?? ""
      const response = await fetch(
        `${baseUrl}/api/v1/health-records/${recordId}/attachments/${attachment.id}`,
        { headers: { Authorization: `Bearer ${token}` } },
      )
      if (!response.ok) {
        throw new Error(i18n.t("common:errors.generic"))
      }
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const link = document.createElement("a")
      link.href = url
      link.download = attachment.filename
      document.body.appendChild(link)
      link.click()
      link.remove()
      setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch {
      showErrorToast(i18n.t("common:errors.generic"))
    }
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      uploadMutation.mutate(file)
    }
    event.target.value = ""
  }

  return (
    <div className="flex flex-col gap-4">
      {attachments && attachments.data.length > 0 ? (
        <ul className="flex flex-col gap-2">
          {attachments.data.map((attachment) => (
            <li
              key={attachment.id}
              className="flex items-center justify-between gap-2 rounded-md border px-3 py-2"
            >
              <span className="truncate text-sm">{attachment.filename}</span>
              <div className="flex shrink-0 gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDownload(attachment)}
                >
                  <Download />
                  {t("attachments.download")}
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={deleteMutation.isPending}
                  onClick={() => setPendingDelete(attachment)}
                >
                  <Trash2 />
                  {t("attachments.delete")}
                </Button>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-sm text-muted-foreground">
          {t("attachments.empty")}
        </p>
      )}

      <div>
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf,image/jpeg,image/png"
          className="hidden"
          onChange={handleFileChange}
        />
        <Button
          variant="outline"
          disabled={uploadMutation.isPending}
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload />
          {t("attachments.upload")}
        </Button>
      </div>

      {pendingDelete && (
        <Dialog
          open
          onOpenChange={(open) => {
            if (!open) {
              setPendingDelete(null)
            }
          }}
        >
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>{t("attachments.deleteDialogTitle")}</DialogTitle>
              <DialogDescription>
                {t("attachments.deleteDialogDescription", {
                  filename: pendingDelete.filename,
                })}
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline" disabled={deleteMutation.isPending}>
                  {t("common:actions.cancel")}
                </Button>
              </DialogClose>
              <LoadingButton
                variant="destructive"
                loading={deleteMutation.isPending}
                onClick={() => deleteMutation.mutate(pendingDelete.id)}
              >
                {t("attachments.deleteConfirmButton")}
              </LoadingButton>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}

interface RecordTitleProps {
  record: HealthRecordPublic
}

/**
 * The record title opens the READ-ONLY detail dialog when clicked (delta
 * AC10: consulting never edits nor asks for a file). For a prescription
 * (title is null in the new model) the clickable summary is the prescribing
 * doctor plus the medicines list ("name — dose · frequency"). The dialog
 * itself lives at page level (RecordDialogsProvider): a cell unmount on
 * refetch must never close it (AC8).
 */
export function RecordTitle({ record }: RecordTitleProps) {
  const { t } = useTranslation("records")
  const { openDetail } = useRecordDialogs()
  const isPrescription = record.record_type === "prescription"
  const displayTitle = isPrescription
    ? (record.professional ?? t("types.prescription"))
    : (record.title ?? "")
  // dd/mm/aaaa by string parts (same rationale as finding C4). The date makes
  // the accessible name distinguishable between rows (finding K2).
  const [year, month, day] = record.occurred_on.split("-")
  const displayDate = `${day}/${month}/${year}`

  return (
    <button
      type="button"
      className="text-left font-medium underline-offset-4 hover:underline"
      aria-label={t("detail.open", { title: displayTitle, date: displayDate })}
      // Focus fallback for the page-level dialogs (finding K6).
      data-record-trigger={record.id}
      onClick={() => openDetail(record.id)}
    >
      {isPrescription ? (
        // Only phrasing content inside a <button>: a <ul> here is invalid
        // HTML (finding K2), so the medicines render as stacked spans.
        <span className="flex flex-col gap-1">
          <span>{displayTitle}</span>
          <span className="flex flex-col pl-5 font-normal">
            {record.medicines.map((medicine) => (
              <span key={medicine.id}>
                {"• "}
                <strong>{medicine.name}</strong>
                {medicine.dose ? ` — ${medicine.dose}` : ""}
                {medicine.frequency ? ` · ${medicine.frequency}` : ""}
              </span>
            ))}
          </span>
        </span>
      ) : (
        record.title
      )}
    </button>
  )
}
