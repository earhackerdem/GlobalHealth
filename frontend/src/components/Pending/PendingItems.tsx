import { useTranslation } from "react-i18next"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

const PendingItems = () => {
  const { t } = useTranslation("items")
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>{t("table.idHeader")}</TableHead>
          <TableHead>{t("table.titleHeader")}</TableHead>
          <TableHead>{t("table.descriptionHeader")}</TableHead>
          <TableHead>
            <span className="sr-only">{t("common:table.actions")}</span>
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {Array.from({ length: 5 }).map((_, index) => (
          <TableRow key={index}>
            <TableCell>
              <Skeleton className="h-4 w-64 font-mono" />
            </TableCell>
            <TableCell>
              <Skeleton className="h-4 w-32" />
            </TableCell>
            <TableCell>
              <Skeleton className="h-4 w-48" />
            </TableCell>
            <TableCell>
              <div className="flex justify-end">
                <Skeleton className="size-8 rounded-md" />
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export default PendingItems
