import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { useTranslation } from "react-i18next"

import { ConsentService } from "@/client"
import ConsentGate from "@/components/Consent/ConsentGate"
import OnboardingWizard from "@/components/Profile/OnboardingWizard"
import { getProfileQueryOptions } from "@/components/Profile/queries"
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
  const navigate = useNavigate()

  const { data: consent, isLoading: consentLoading } = useQuery({
    queryKey: ["consent"],
    queryFn: async () =>
      (await ConsentService.readConsent({ throwOnError: false })).data ?? null,
    retry: false,
  })

  // GET /profile sits behind require_consent: only ask once consent exists.
  const { data: profile } = useQuery({
    ...getProfileQueryOptions(),
    enabled: !consentLoading && !!consent,
  })

  // Home sequence (design decision 5): no consent → ConsentGate; consent and
  // onboarding pending → wizard; onboarding closed → straight to expediente.
  useEffect(() => {
    if (profile && profile.onboarding !== "pending") {
      navigate({ to: "/expediente" })
    }
  }, [profile, navigate])

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
      {consent && profile?.onboarding === "pending" && <OnboardingWizard />}
    </div>
  )
}
