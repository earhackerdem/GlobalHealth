import { Briefcase, ClipboardList, FileText, Home, Users } from "lucide-react"

import { SidebarAppearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
} from "@/components/ui/sidebar"
import useAuth from "@/hooks/useAuth"
import i18n from "@/i18n"
import { type Item, Main } from "./Main"
import { User } from "./User"

const baseItems: Item[] = [
  { icon: Home, title: i18n.t("layout:sidebar.dashboard"), path: "/" },
  { icon: Briefcase, title: i18n.t("layout:sidebar.items"), path: "/items" },
  {
    icon: FileText,
    title: i18n.t("layout:sidebar.expediente"),
    path: "/expediente",
  },
  {
    icon: ClipboardList,
    title: i18n.t("layout:sidebar.perfil"),
    path: "/perfil",
  },
]

export function AppSidebar() {
  const { user: currentUser } = useAuth()

  const items = currentUser?.is_superuser
    ? [
        ...baseItems,
        { icon: Users, title: i18n.t("layout:sidebar.admin"), path: "/admin" },
      ]
    : baseItems

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader className="px-4 py-6 group-data-[collapsible=icon]:px-0 group-data-[collapsible=icon]:items-center">
        <Logo variant="responsive" />
      </SidebarHeader>
      <SidebarContent>
        <Main items={items} />
      </SidebarContent>
      <SidebarFooter>
        <SidebarAppearance />
        <User user={currentUser} />
      </SidebarFooter>
    </Sidebar>
  )
}

export default AppSidebar
