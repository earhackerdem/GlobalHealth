import { AxiosError } from "axios"

import i18n from "@/i18n"

function extractErrorMessage(err: Error): string {
  if (err instanceof AxiosError) {
    const errDetail = (err.response?.data as any)?.detail
    if (Array.isArray(errDetail) && errDetail.length > 0) {
      // Pydantic 422 validation messages come in English; show es-MX instead.
      return i18n.t("common:errors.validation")
    }
    if (typeof errDetail === "string") {
      // Backend details are already es-MX; pass them through.
      return errDetail
    }
    return i18n.t("common:errors.generic")
  }
  // t() runs at call time, after i18n init in main.tsx.
  return i18n.t("common:errors.generic")
}

export const handleError = function (this: (msg: string) => void, err: Error) {
  const errorMessage = extractErrorMessage(err)
  this(errorMessage)
}

export const getInitials = (name: string): string => {
  return name
    .split(" ")
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase()
}
