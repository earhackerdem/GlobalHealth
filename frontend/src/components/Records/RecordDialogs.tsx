import { type ReactNode, useMemo, useState } from "react"
import { useTranslation } from "react-i18next"

import type { HealthRecordPublic } from "@/client"
import { EditRecordDialog } from "@/components/Records/EditRecord"
import { AttachmentsPanel } from "@/components/Records/RecordAttachments"
import { RecordDialogsContext } from "@/components/Records/RecordDialogsContext"
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

/** dd/mm/aaaa by string parts: new Date("YYYY-MM-DD") is UTC and shifts the
 * day in negative-offset timezones (finding C4). */
function formatDate(occurredOn: string) {
  const [year, month, day] = occurredOn.split("-")
  return `${day}/${month}/${year}`
}

/** Read-only body of the detail view (delta AC10): data only, no inputs. */
function RecordDetailBody({ record }: { record: HealthRecordPublic }) {
  const { t } = useTranslation("records")
  const isPrescription = record.record_type === "prescription"

  return (
    <div className="grid gap-3 text-sm">
      {!isPrescription && record.title && (
        <p>
          <span className="text-muted-foreground">
            {t("fields.diagnosis")}:{" "}
          </span>
          {record.title}
        </p>
      )}
      {record.professional && (
        <p>
          <span className="text-muted-foreground">
            {isPrescription ? t("detail.doctor") : t("detail.professional")}:{" "}
          </span>
          {record.professional}
        </p>
      )}
      <p>
        <span className="text-muted-foreground">{t("detail.date")}: </span>
        {formatDate(record.occurred_on)}
      </p>
      {isPrescription && (
        <div>
          <p className="text-muted-foreground">{t("detail.medicines")}</p>
          <ul className="list-disc pl-5">
            {record.medicines.map((medicine) => (
              <li key={medicine.id}>
                <strong>{medicine.name}</strong>
                {medicine.dose ? ` — ${medicine.dose}` : ""}
                {medicine.frequency ? ` · ${medicine.frequency}` : ""}
              </li>
            ))}
          </ul>
        </div>
      )}
      {isPrescription && record.diagnosis && (
        <p>
          <span className="text-muted-foreground">
            {t("detail.diagnosisLabel")}:{" "}
          </span>
          {record.diagnosis}
        </p>
      )}
      {record.notes && (
        <div>
          <p className="text-muted-foreground">{t("detail.notes")}</p>
          {/* pre-line: the stored "\n" of multiline notes render as real
              line breaks when consulted (delta AC9). */}
          <p className="whitespace-pre-line">{record.notes}</p>
        </div>
      )}
    </div>
  )
}

interface RecordDialogsProviderProps {
  records: HealthRecordPublic[]
  children: ReactNode
}

/**
 * Owns the open/closed state of the record dialogs (detail → confirm → edit)
 * at PAGE level, by record id.
 *
 * Root cause of the reported bug (delta 2026-10-18, AC8): these dialogs used
 * to live inside table cells / dropdown menu content. The list refetch on
 * window focus (TanStack Query refetchOnWindowFocus) re-renders the rows and
 * Radix unmounts the dropdown content when the menu dismisses on focus loss,
 * so switching tabs unmounted the open dialog and lost everything typed.
 * Hoisted here, a refetch only re-renders: the dialog element is the same
 * (same id) and react-hook-form keeps the user's values.
 */
export function RecordDialogsProvider({
  records,
  children,
}: RecordDialogsProviderProps) {
  const { t } = useTranslation("records")
  const [detailId, setDetailId] = useState<string | null>(null)
  const [confirmId, setConfirmId] = useState<string | null>(null)
  const [editId, setEditId] = useState<string | null>(null)

  const api = useMemo(
    () => ({
      openDetail: (recordId: string) => setDetailId(recordId),
      openEdit: (recordId: string) => setEditId(recordId),
    }),
    [],
  )

  // Fresh record from the (possibly refetched) list: dialogs follow the id.
  const detailRecord = records.find((record) => record.id === detailId)
  const confirmRecord = records.find((record) => record.id === confirmId)
  const editRecord = records.find((record) => record.id === editId)

  return (
    <RecordDialogsContext.Provider value={api}>
      {children}

      {detailRecord && (
        <Dialog
          open
          onOpenChange={(open) => {
            if (!open) {
              setDetailId(null)
            }
          }}
        >
          <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>
                {detailRecord.record_type === "prescription"
                  ? t("detail.prescriptionTitle")
                  : t("detail.diagnosisTitle")}
              </DialogTitle>
              <DialogDescription>{t("detail.description")}</DialogDescription>
            </DialogHeader>
            <RecordDetailBody record={detailRecord} />
            <section className="flex flex-col gap-2">
              <h3 className="text-sm font-medium">{t("attachments.title")}</h3>
              <AttachmentsPanel recordId={detailRecord.id} />
            </section>
            <DialogFooter>
              {detailRecord.record_type === "prescription" && (
                <Button
                  variant="outline"
                  onClick={() => {
                    setDetailId(null)
                    setConfirmId(detailRecord.id)
                  }}
                >
                  {t("detail.edit")}
                </Button>
              )}
              <DialogClose asChild>
                <Button>{t("common:actions.close")}</Button>
              </DialogClose>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {confirmRecord && (
        <Dialog
          open
          onOpenChange={(open) => {
            if (!open) {
              setConfirmId(null)
            }
          }}
        >
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>{t("detail.confirmTitle")}</DialogTitle>
              <DialogDescription>
                {t("detail.confirmDescription")}
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <DialogClose asChild>
                <Button variant="outline">{t("common:actions.cancel")}</Button>
              </DialogClose>
              <Button
                onClick={() => {
                  setConfirmId(null)
                  setEditId(confirmRecord.id)
                }}
              >
                {t("detail.confirmButton")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}

      {editRecord && (
        <EditRecordDialog
          key={editRecord.id}
          record={editRecord}
          onClose={() => setEditId(null)}
        />
      )}
    </RecordDialogsContext.Provider>
  )
}
