import { createFileRoute } from "@tanstack/react-router"
import { useTranslation } from "react-i18next"

import ChangePassword from "@/components/UserSettings/ChangePassword"
import DeleteAccount from "@/components/UserSettings/DeleteAccount"
import UserInformation from "@/components/UserSettings/UserInformation"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import useAuth from "@/hooks/useAuth"
import i18n from "@/i18n"

const tabsConfig = [
  { value: "my-profile", title: "tabs.myProfile", component: UserInformation },
  { value: "password", title: "tabs.password", component: ChangePassword },
  { value: "danger-zone", title: "tabs.dangerZone", component: DeleteAccount },
]

export const Route = createFileRoute("/_layout/settings")({
  component: UserSettings,
  head: () => ({
    meta: [
      {
        title: i18n.t("settings:page.pageTitle"),
      },
    ],
  }),
})

function UserSettings() {
  const { t } = useTranslation("settings")
  const { user: currentUser } = useAuth()
  const finalTabs = currentUser?.is_superuser
    ? tabsConfig.slice(0, 3)
    : tabsConfig

  if (!currentUser) {
    return null
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t("page.title")}</h1>
        <p className="text-muted-foreground">{t("page.subtitle")}</p>
      </div>

      <Tabs defaultValue="my-profile">
        <TabsList>
          {finalTabs.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value}>
              {t(tab.title)}
            </TabsTrigger>
          ))}
        </TabsList>
        {finalTabs.map((tab) => (
          <TabsContent key={tab.value} value={tab.value}>
            <tab.component />
          </TabsContent>
        ))}
      </Tabs>
    </div>
  )
}
