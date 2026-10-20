import { createFileRoute, notFound } from "@tanstack/react-router"
import { Suspense } from "react"

import PendingItems from "@/components/Pending/PendingItems"
import HistorySection, {
  BackToProfile,
} from "@/components/Profile/HistorySection"
import { sectionFromSlug } from "@/components/Profile/history"
import i18n from "@/i18n"

/**
 * /perfil/pasadas · /perfil/cirugias · /perfil/fracturas · /perfil/transfusiones:
 * one screen per history section (Decision 5). The trailing `_` in the file
 * name keeps it out of perfil.tsx's layout (it is a sibling page, not a child).
 */
export const Route = createFileRoute("/_layout/perfil_/$seccion")({
  component: SectionPage,
  beforeLoad: ({ params }) => {
    if (!sectionFromSlug(params.seccion)) throw notFound()
  },
  head: ({ params }) => {
    const section = sectionFromSlug(params.seccion)
    return {
      meta: [
        {
          title: section
            ? i18n.t(`profile:pending.sections.${section}`)
            : i18n.t("profile:page.pageTitle"),
        },
      ],
    }
  },
})

function SectionPage() {
  const { seccion } = Route.useParams()
  const section = sectionFromSlug(seccion)
  if (!section) return null
  return (
    <div className="flex flex-col gap-4">
      <BackToProfile />
      <Suspense fallback={<PendingItems />}>
        <HistorySection key={section} section={section} />
      </Suspense>
    </div>
  )
}
