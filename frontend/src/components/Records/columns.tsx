import type { ColumnDef } from "@tanstack/react-table"

import type { HealthRecordPublic } from "@/client"
import type { DataTableFeatures } from "@/components/Common/DataTable"
import { Badge } from "@/components/ui/badge"
import i18n from "@/i18n"
import { RecordActionsMenu } from "./RecordActionsMenu"
import { RecordTitle } from "./RecordAttachments"

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
    cell: ({ row }) => <RecordTitle record={row.original} />,
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
      <div className="flex justify-end">
        <RecordActionsMenu record={row.original} />
      </div>
    ),
  },
]
