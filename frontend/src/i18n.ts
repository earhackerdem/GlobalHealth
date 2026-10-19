// App localization: es-MX is the ONLY shipped locale (NFR-012, ADR D15).
// Resources are bundled statically; adding a locale later means adding its
// JSON files here and a language selector — no HTTP translation backend.
import i18n from "i18next"
import { initReactI18next } from "react-i18next"

import admin from "./locales/es-MX/admin.json"
import auth from "./locales/es-MX/auth.json"
import common from "./locales/es-MX/common.json"
import consent from "./locales/es-MX/consent.json"
import items from "./locales/es-MX/items.json"
import layout from "./locales/es-MX/layout.json"
import profile from "./locales/es-MX/profile.json"
import records from "./locales/es-MX/records.json"
import settings from "./locales/es-MX/settings.json"

i18n.use(initReactI18next).init({
  lng: "es-MX",
  fallbackLng: "es-MX",
  defaultNS: "common",
  resources: {
    "es-MX": {
      common,
      auth,
      layout,
      items,
      admin,
      settings,
      consent,
      records,
      profile,
    },
  },
  interpolation: {
    // React already escapes rendered values.
    escapeValue: false,
  },
})

export default i18n
