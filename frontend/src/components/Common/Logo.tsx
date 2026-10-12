import { Link } from "@tanstack/react-router"
import { useTranslation } from "react-i18next"

import { useTheme } from "@/components/theme-provider"
import { cn } from "@/lib/utils"
import icon from "/assets/images/fastapi-icon.svg"
import iconLight from "/assets/images/fastapi-icon-light.svg"
import logo from "/assets/images/fastapi-logo.svg"
import logoLight from "/assets/images/fastapi-logo-light.svg"

interface LogoProps {
  variant?: "full" | "icon" | "responsive"
  className?: string
  asLink?: boolean
}

export function Logo({
  variant = "full",
  className,
  asLink = true,
}: LogoProps) {
  const { t } = useTranslation("common")
  const { resolvedTheme } = useTheme()
  const isDark = resolvedTheme === "dark"

  const fullLogo = isDark ? logoLight : logo
  const iconLogo = isDark ? iconLight : icon

  const content =
    variant === "responsive" ? (
      <>
        <img
          src={fullLogo}
          alt={t("logoAlt")}
          className={cn(
            "h-6 w-auto group-data-[collapsible=icon]:hidden",
            className,
          )}
        />
        <img
          src={iconLogo}
          alt={t("logoAlt")}
          className={cn(
            "size-5 hidden group-data-[collapsible=icon]:block",
            className,
          )}
        />
      </>
    ) : (
      <img
        src={variant === "full" ? fullLogo : iconLogo}
        alt={t("logoAlt")}
        className={cn(variant === "full" ? "h-6 w-auto" : "size-5", className)}
      />
    )

  if (!asLink) {
    return content
  }

  return <Link to="/">{content}</Link>
}
