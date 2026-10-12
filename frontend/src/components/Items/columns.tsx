import type { ColumnDef } from "@tanstack/react-table"
import { Check, Copy } from "lucide-react"
import { useTranslation } from "react-i18next"
import type { ItemPublic } from "@/client"
import type { DataTableFeatures } from "@/components/Common/DataTable"
import { Button } from "@/components/ui/button"
import { useCopyToClipboard } from "@/hooks/useCopyToClipboard"
import i18n from "@/i18n"
import { cn } from "@/lib/utils"
import { ItemActionsMenu } from "./ItemActionsMenu"

function CopyId({ id }: { id: string }) {
  const { t } = useTranslation("items")
  const [copiedText, copy] = useCopyToClipboard()
  const isCopied = copiedText === id

  return (
    <div className="flex items-center gap-1.5 group">
      <span className="font-mono text-xs text-muted-foreground">{id}</span>
      <Button
        variant="ghost"
        size="icon"
        className="size-6 opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={() => copy(id)}
      >
        {isCopied ? (
          <Check className="size-3 text-green-500" />
        ) : (
          <Copy className="size-3" />
        )}
        <span className="sr-only">{t("table.copyId")}</span>
      </Button>
    </div>
  )
}

export const columns: ColumnDef<DataTableFeatures, ItemPublic>[] = [
  {
    accessorKey: "id",
    header: () => i18n.t("items:table.idHeader"),
    cell: ({ row }) => <CopyId id={row.original.id} />,
  },
  {
    accessorKey: "title",
    header: () => i18n.t("items:table.titleHeader"),
    cell: ({ row }) => (
      <span className="font-medium">{row.original.title}</span>
    ),
  },
  {
    accessorKey: "description",
    header: () => i18n.t("items:table.descriptionHeader"),
    cell: ({ row }) => {
      const description = row.original.description
      return (
        <span
          className={cn(
            "max-w-xs truncate block text-muted-foreground",
            !description && "italic",
          )}
        >
          {description || i18n.t("items:table.noDescription")}
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
        <ItemActionsMenu item={row.original} />
      </div>
    ),
  },
]
