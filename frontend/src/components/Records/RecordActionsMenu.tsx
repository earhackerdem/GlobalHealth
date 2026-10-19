import { EllipsisVertical } from "lucide-react"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import type { HealthRecordPublic } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import DeleteRecord from "./DeleteRecord"
import EditRecord from "./EditRecord"

interface RecordActionsMenuProps {
  record: HealthRecordPublic
}

export const RecordActionsMenu = ({ record }: RecordActionsMenuProps) => {
  const { t } = useTranslation("records")
  const [open, setOpen] = useState(false)

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" aria-label={t("actions.openMenu")}>
          <EllipsisVertical />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <EditRecord record={record} />
        <DeleteRecord id={record.id} onSuccess={() => setOpen(false)} />
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
