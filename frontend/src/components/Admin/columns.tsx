import type { ColumnDef } from "@tanstack/react-table"

import type { UserPublic } from "@/client"
import type { DataTableFeatures } from "@/components/Common/DataTable"
import { Badge } from "@/components/ui/badge"
import i18n from "@/i18n"
import { cn } from "@/lib/utils"
import { UserActionsMenu } from "./UserActionsMenu"

export type UserTableData = UserPublic & {
  isCurrentUser: boolean
}

export const columns: ColumnDef<DataTableFeatures, UserTableData>[] = [
  {
    accessorKey: "full_name",
    header: () => i18n.t("admin:table.fullNameHeader"),
    cell: ({ row }) => {
      const fullName = row.original.full_name
      return (
        <div className="flex items-center gap-2">
          <span
            className={cn("font-medium", !fullName && "text-muted-foreground")}
          >
            {fullName || i18n.t("common:table.notAvailable")}
          </span>
          {row.original.isCurrentUser && (
            <Badge variant="outline" className="text-xs">
              {i18n.t("admin:table.youBadge")}
            </Badge>
          )}
        </div>
      )
    },
  },
  {
    accessorKey: "email",
    header: () => i18n.t("admin:table.emailHeader"),
    cell: ({ row }) => (
      <span className="text-muted-foreground">{row.original.email}</span>
    ),
  },
  {
    accessorKey: "is_superuser",
    header: () => i18n.t("admin:table.roleHeader"),
    cell: ({ row }) => (
      <Badge variant={row.original.is_superuser ? "default" : "secondary"}>
        {row.original.is_superuser
          ? i18n.t("admin:table.roleSuperuser")
          : i18n.t("admin:table.roleUser")}
      </Badge>
    ),
  },
  {
    accessorKey: "is_active",
    header: () => i18n.t("admin:table.statusHeader"),
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <span
          className={cn(
            "size-2 rounded-full",
            row.original.is_active ? "bg-green-500" : "bg-gray-400",
          )}
        />
        <span className={row.original.is_active ? "" : "text-muted-foreground"}>
          {row.original.is_active
            ? i18n.t("admin:table.statusActive")
            : i18n.t("admin:table.statusInactive")}
        </span>
      </div>
    ),
  },
  {
    id: "actions",
    header: () => (
      <span className="sr-only">{i18n.t("common:table.actions")}</span>
    ),
    cell: ({ row }) => (
      <div className="flex justify-end">
        <UserActionsMenu user={row.original} />
      </div>
    ),
  },
]
