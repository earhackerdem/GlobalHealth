import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { FileText } from "lucide-react"
import { Suspense } from "react"
import { useTranslation } from "react-i18next"

import { HealthRecordsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import PendingItems from "@/components/Pending/PendingItems"
import AddDiagnosis from "@/components/Records/AddDiagnosis"
import AddPrescription from "@/components/Records/AddPrescription"
import { columns } from "@/components/Records/columns"
import { RecordDialogsProvider } from "@/components/Records/RecordDialogs"
import i18n from "@/i18n"

function getRecordsQueryOptions() {
  return {
    queryFn: async () =>
      (
        await HealthRecordsService.recordsReadHealthRecords({
          query: { skip: 0, limit: 100 },
        })
      ).data,
    queryKey: ["health-records"],
  }
}

export const Route = createFileRoute("/_layout/expediente")({
  component: Expediente,
  head: () => ({
    meta: [
      {
        title: i18n.t("records:page.pageTitle"),
      },
    ],
  }),
})

function RecordsTableContent() {
  const { t } = useTranslation("records")
  const { data: records } = useSuspenseQuery(getRecordsQueryOptions())

  if (records.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <FileText className="h-8 w-8 text-muted-foreground" />
        </div>
        <p className="text-muted-foreground">{t("page.empty")}</p>
      </div>
    )
  }

  // The API returns archived records too; the UI separates them (AC-8):
  // actives first, archived under their own heading at the end.
  const active = records.data.filter((record) => !record.archived)
  const archived = records.data.filter((record) => record.archived)

  return (
    // The provider owns the detail/confirm/edit dialogs at page level, by
    // record id: a row re-render (refetch on window focus) or a dropdown
    // unmount can never close them (delta AC8/AC10).
    <RecordDialogsProvider records={records.data}>
      <div className="flex flex-col gap-6">
        <DataTable columns={columns} data={active} />
        {archived.length > 0 && (
          <section className="flex flex-col gap-2">
            <h2 className="text-lg font-semibold">
              {t("page.archivedHeading")}
            </h2>
            <DataTable columns={columns} data={archived} />
          </section>
        )}
      </div>
    </RecordDialogsProvider>
  )
}

function RecordsTable() {
  return (
    <Suspense fallback={<PendingItems />}>
      <RecordsTableContent />
    </Suspense>
  )
}

function Expediente() {
  const { t } = useTranslation("records")
  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t("title")}</h1>
          <p className="text-muted-foreground">{t("page.subtitle")}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <AddDiagnosis />
          <AddPrescription />
        </div>
      </div>
      <RecordsTable />
    </div>
  )
}
