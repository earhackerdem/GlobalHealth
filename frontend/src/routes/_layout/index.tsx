import { createFileRoute } from "@tanstack/react-router"
import { useTranslation } from "react-i18next"

import ConsentGate from "@/components/Consent/ConsentGate"
import useAuth from "@/hooks/useAuth"
import i18n from "@/i18n"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: i18n.t("layout:dashboard.pageTitle"),
      },
    ],
  }),
})

function Dashboard() {
  const { t } = useTranslation("layout")
  const { user: currentUser } = useAuth()

  return (
    <div>
      <div>
        <h1 className="text-2xl truncate max-w-sm">
          {t("dashboard.greeting", {
            name: currentUser?.full_name || currentUser?.email,
          })}
        </h1>
        <p className="text-muted-foreground">{t("dashboard.welcomeBack")}</p>
      </div>
      <ConsentGate />
    </div>
  )
}
