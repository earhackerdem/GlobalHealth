import { createFileRoute } from "@tanstack/react-router"
import { Suspense } from "react"

import PendingItems from "@/components/Pending/PendingItems"
import HabitsForm from "@/components/Profile/HabitsForm"
import { BackToProfile } from "@/components/Profile/HistorySection"
import i18n from "@/i18n"

/**
 * /perfil/habitos: the habits questionnaire (perfil-habitos). A static route,
 * so it wins over perfil_.$seccion.tsx (habits is not a history section); the
 * trailing `_` keeps it out of perfil.tsx's layout, like the sections.
 */
export const Route = createFileRoute("/_layout/perfil_/habitos")({
  component: HabitsPage,
  head: () => ({
    meta: [
      {
        title: i18n.t("profile:habits.title"),
      },
    ],
  }),
})

function HabitsPage() {
  return (
    <div className="flex flex-col gap-4">
      <BackToProfile />
      <Suspense fallback={<PendingItems />}>
        <HabitsForm />
      </Suspense>
    </div>
  )
}
