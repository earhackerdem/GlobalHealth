import type { ColumnDef } from "@tanstack/react-table"

import type { HealthRecordPublic } from "@/client"
import type { DataTableFeatures } from "@/components/Common/DataTable"
import { Badge } from "@/components/ui/badge"
import i18n from "@/i18n"
import { ArchiveRecordButton } from "./ArchiveRecordButton"
import { RecordActionsMenu } from "./RecordActionsMenu"
import { RecordTitle } from "./RecordAttachments"

/** Flow chips of a record: diagnosis chip and archived state (prescription),
 * confirmation status (loose diagnosis). */
function RecordChips({ record }: { record: HealthRecordPublic }) {
  const isPrescription = record.record_type === "prescription"
  return (
    <div className="flex flex-wrap gap-1">
      {isPrescription && record.archived && (
        <Badge variant="secondary">
          {i18n.t("records:archive.archivedChip")}
        </Badge>
      )}
      {isPrescription && record.diagnosis && (
        <Badge variant="secondary">
          {i18n.t("records:diagnosisChip", { diagnosis: record.diagnosis })}
        </Badge>
      )}
      {!isPrescription && record.confirmation_status === "unconfirmed" && (
        <Badge variant="secondary">
          {i18n.t("records:confirmation.unconfirmed")}
        </Badge>
      )}
    </div>
  )
}

export const columns: ColumnDef<DataTableFeatures, HealthRecordPublic>[] = [
  {
    accessorKey: "record_type",
    header: () => i18n.t("records:table.typeHeader"),
    cell: ({ row }) => (
      <Badge variant="outline">
        {i18n.t(`records:types.${row.original.record_type}`)}
      </Badge>
    ),
  },
  {
    accessorKey: "title",
    header: () => i18n.t("records:table.titleHeader"),
    cell: ({ row }) => (
      <div className="flex flex-col gap-1">
        <RecordTitle record={row.original} />
        <RecordChips record={row.original} />
      </div>
    ),
  },
  {
    accessorKey: "occurred_on",
    header: () => i18n.t("records:table.dateHeader"),
    cell: ({ row }) => {
      // Parse "YYYY-MM-DD" by parts: new Date("YYYY-MM-DD") is UTC and
      // shifts the day in negative-offset timezones (finding C4).
      const [year, month, day] = row.original.occurred_on.split("-")
      return (
        <span className="text-muted-foreground">
          {`${day}/${month}/${year}`}
        </span>
      )
    },
  },
  {
    id: "actions",
    header: () => (
      <span className="sr-only">{i18n.t("common:table.actions")}</span>
    ),
    cell: ({ row }) => (
      <div className="flex items-center justify-end gap-1">
        {row.original.record_type === "prescription" && (
          <ArchiveRecordButton record={row.original} />
        )}
        <RecordActionsMenu record={row.original} />
      </div>
    ),
  },
]
