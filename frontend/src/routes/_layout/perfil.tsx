import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Suspense } from "react"
import { useTranslation } from "react-i18next"

import { ProfileService } from "@/client"
import PendingItems from "@/components/Pending/PendingItems"
import EditBasicData from "@/components/Profile/EditBasicData"
import EditFamilyHistory from "@/components/Profile/EditFamilyHistory"
import { ageFrom, formatDateMx } from "@/components/Profile/format"
import { Badge } from "@/components/ui/badge"
import i18n from "@/i18n"

const PENDING_SECTION_KEYS = [
  "chronic",
  "past",
  "surgeries",
  "fractures",
  "transfusions",
  "habits",
] as const

export const Route = createFileRoute("/_layout/perfil")({
  component: ProfilePage,
  head: () => ({
    meta: [
      {
        title: i18n.t("profile:pageTitle"),
      },
    ],
  }),
})

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-sm">{value}</span>
    </div>
  )
}

function ProfileContent() {
  const { t } = useTranslation("profile")

  const { data: profile } = useSuspenseQuery({
    queryKey: ["profile"],
    queryFn: async () => (await ProfileService.readProfile()).data,
  })
  const { data: familyHistory } = useSuspenseQuery({
    queryKey: ["family-history"],
    queryFn: async () => (await ProfileService.readFamilyHistory()).data,
  })

  const birthDateValue = profile.birth_date
    ? `${formatDateMx(profile.birth_date)} · ${t("age", {
        age: ageFrom(profile.birth_date),
      })}`
    : t("notRecorded")

  return (
    <div className="flex flex-col gap-6">
      <section
        data-testid="profile-basic-data"
        className="flex flex-col gap-4 rounded-lg border p-4"
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-semibold">{t("basic.heading")}</h2>
          <EditBasicData profile={profile} />
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <Row label={t("fields.birthDate")} value={birthDateValue} />
          <Row
            label={t("fields.sex")}
            value={
              profile.sex ? t(`sexOptions.${profile.sex}`) : t("notRecorded")
            }
          />
          <Row
            label={t("fields.allergies")}
            value={profile.allergies || t("notRecorded")}
          />
          <Row
            label={t("measurements.weight")}
            value={
              profile.latest_weight
                ? `${profile.latest_weight.value} kg · ${formatDateMx(
                    profile.latest_weight.measured_on,
                  )}`
                : t("notRecorded")
            }
          />
          <Row
            label={t("measurements.height")}
            value={
              profile.latest_height
                ? `${profile.latest_height.value} cm · ${formatDateMx(
                    profile.latest_height.measured_on,
                  )}`
                : t("notRecorded")
            }
          />
        </div>
      </section>

      <section
        data-testid="profile-family-history"
        className="flex flex-col gap-3 rounded-lg border p-4"
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="text-lg font-semibold">{t("family.heading")}</h2>
          <EditFamilyHistory entries={familyHistory.data} />
        </div>
        {familyHistory.data.length === 0 ? (
          <p className="text-sm text-muted-foreground">{t("noEntries")}</p>
        ) : (
          familyHistory.data.map((entry) => (
            <div key={entry.id} className="flex flex-wrap items-center gap-2">
              <span className="text-sm font-medium">
                {entry.condition === "other" && entry.other_text
                  ? entry.other_text
                  : t(`conditions.${entry.condition}`)}
              </span>
              {entry.relatives.map((relative) => (
                <Badge key={relative} variant="secondary">
                  {t(`relatives.${relative}`)}
                </Badge>
              ))}
              {entry.note && (
                <span className="text-sm text-muted-foreground">
                  {entry.note}
                </span>
              )}
            </div>
          ))
        )}
      </section>

      <section className="flex flex-col gap-3">
        <div>
          <h2 className="text-lg font-semibold">{t("pending.heading")}</h2>
          <p className="text-sm text-muted-foreground">
            {t("pending.description")}
          </p>
        </div>
        {/* Read-only by design (FR-027): the six remaining sections are
            listed without any capture form — no inputs, no save button. */}
        <div
          data-testid="profile-pending-sections"
          className="grid gap-4 sm:grid-cols-2"
        >
          {PENDING_SECTION_KEYS.map((key) => (
            <div key={key} className="rounded-lg border p-4">
              <h3 className="font-medium">{t(`pending.sections.${key}`)}</h3>
              <p className="text-sm text-muted-foreground">{t("noEntries")}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

function ProfilePage() {
  const { t } = useTranslation("profile")
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{t("title")}</h1>
        <p className="text-muted-foreground">{t("subtitle")}</p>
      </div>
      <Suspense fallback={<PendingItems />}>
        <ProfileContent />
      </Suspense>
    </div>
  )
}
