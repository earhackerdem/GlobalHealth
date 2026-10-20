import {
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from "@tanstack/react-query"
import { Link } from "@tanstack/react-router"
import type { TFunction } from "i18next"
import { useEffect, useId, useRef, useState } from "react"
import { useTranslation } from "react-i18next"

import { type PatientProfilePublic, ProfileService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import BloodTypePicker from "./BloodTypePicker"
import HistoryEntryForm from "./HistoryEntryForm"
import {
  type HistoryEntry,
  type HistorySection as Section,
  sectionStatus,
  whenSummary,
} from "./history"
import { getHistoryQueryOptions, getProfileQueryOptions } from "./queries"

/** Bold first line of an entry in the list (prototype `tituloReg`). */
function entryTitle(entry: HistoryEntry, t: TFunction): string {
  switch (entry.section) {
    case "past":
      if (entry.condition === "other" && entry.other_text) {
        return entry.other_text
      }
      return entry.condition
        ? t(`profile:history.options.condition.${entry.condition}`)
        : ""
    case "surgeries":
      return entry.name ?? ""
    case "fractures":
      return entry.what ?? ""
    case "transfusions":
      return entry.reason
        ? t("profile:history.transfusionTitleWithReason", {
            reason: entry.reason,
          })
        : t("profile:history.transfusionTitle")
  }
}

/** "izquierdo · a los 10 años · requirió cirugía · implante: …" (prototype `resumen`). */
function entrySummary(
  entry: HistoryEntry,
  birthDate: string | null,
  t: TFunction,
): string {
  const parts: string[] = []
  const s = (key: string, options?: Record<string, unknown>) =>
    t(`profile:history.summary.${key}`, options)
  if (
    entry.section === "fractures" &&
    entry.side &&
    entry.side !== "not_applicable"
  ) {
    parts.push(s(`side.${entry.side}`))
  }
  if (entry.when) parts.push(whenSummary(entry.when, birthDate, t))
  if (entry.section === "surgeries" && entry.kind) {
    parts.push(s(`kind.${entry.kind}`))
  }
  if (entry.section === "transfusions" && entry.component) {
    parts.push(s(`component.${entry.component}`))
  }
  if (entry.section === "past" && entry.hospitalized === "yes") {
    parts.push(s("hospitalized"))
  }
  if (entry.section === "fractures" && entry.required_surgery === "yes") {
    parts.push(s("requiredSurgery"))
  }
  if (entry.section === "surgeries" && entry.reason) parts.push(entry.reason)
  if (
    (entry.section === "surgeries" || entry.section === "fractures") &&
    entry.implant
  ) {
    parts.push(s("implant", { implant: entry.implant }))
  }
  if (
    (entry.section === "surgeries" && entry.anesthesia_reaction === "yes") ||
    (entry.section === "transfusions" && entry.reaction === "yes")
  ) {
    parts.push(s("reaction"))
  }
  return parts.join(" · ")
}

type Mode = { kind: "list" } | { kind: "form"; entry: HistoryEntry | null }

/**
 * One section of the medical history on its own screen (Decision 5, prototype
 * v4): status, the list with inline delete confirmation, the "ninguna" mark
 * and its undo, and the add/edit form in place of the list. Focus returns to
 * the list (a region named by the heading) after saving, cancelling,
 * deleting, marking "ninguna" or undoing it; opening a delete confirmation
 * focuses "Sí, eliminar" (described by the question) and cancelling it
 * returns to that row's "Eliminar".
 */
function HistorySection({ section }: { section: Section }) {
  const { t } = useTranslation("profile")
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const headingId = useId()
  const confirmQuestionId = useId()
  const listRef = useRef<HTMLElement>(null)
  // LoadingButton takes no ref: its first button is "Sí, eliminar".
  const confirmRef = useRef<HTMLDivElement>(null)
  const deleteButtons = useRef(new Map<string, HTMLButtonElement>())

  const { data: profile } = useSuspenseQuery(getProfileQueryOptions())
  const { data: history } = useSuspenseQuery(getHistoryQueryOptions())

  const [mode, setMode] = useState<Mode>({ kind: "list" })
  const [confirmingId, setConfirmingId] = useState<string | null>(null)

  const entries = history.data.filter((entry) => entry.section === section)
  const none = profile.sections_none.includes(section)
  const noneKey = section === "transfusions" ? "transfusions" : "default"

  // Where the focus goes once the next render has painted its target (it may
  // not exist yet: the list after the form, "Sí, eliminar" after "Eliminar").
  // Kept until the target exists, so an unrelated render in between (a
  // refetch) does not lose it.
  const pendingFocus = useRef<(() => HTMLElement | null | undefined) | null>(
    null,
  )
  useEffect(() => {
    const target = pendingFocus.current?.()
    if (target) {
      pendingFocus.current = null
      target.focus()
    }
  })
  const [, forceRender] = useState(0)
  const focusAfterRender = (target: () => HTMLElement | null | undefined) => {
    pendingFocus.current = target
    forceRender((n) => n + 1)
  }
  const focusList = () => focusAfterRender(() => listRef.current)

  const backToList = () => {
    setMode({ kind: "list" })
    focusList()
  }

  const noneMutation = useMutation({
    mutationFn: async (value: boolean) =>
      (
        await ProfileService.setHistorySectionNone({
          path: { section },
          body: { none: value },
        })
      ).data,
    onSuccess: (saved: PatientProfilePublic, value) => {
      queryClient.setQueryData(["profile"], saved)
      showSuccessToast(value ? t("history.noneToast") : t("history.undoToast"))
      // The button just pressed is gone: the focus would fall to <body>.
      focusList()
    },
    onError: handleError.bind(showErrorToast),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) =>
      ProfileService.deleteHistoryEntry({ path: { id } }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["history"] })
      setConfirmingId(null)
      showSuccessToast(t("history.deletedToast"))
      focusList()
    },
    onError: handleError.bind(showErrorToast),
  })

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2">
        <h1 id={headingId} className="text-2xl font-bold tracking-tight">
          {t(`pending.sections.${section}`)}
        </h1>
        <Badge variant={entries.length || none ? "secondary" : "outline"}>
          {sectionStatus(entries.length, none, t)}
        </Badge>
      </div>

      {section === "transfusions" && <BloodTypePicker profile={profile} />}

      {mode.kind === "form" ? (
        <HistoryEntryForm
          key={mode.entry?.id ?? "new"}
          section={section}
          entry={mode.entry}
          birthDate={profile.birth_date}
          wasNone={none}
          onDone={backToList}
        />
      ) : (
        <>
          <section
            ref={listRef}
            tabIndex={-1}
            aria-labelledby={headingId}
            data-testid="history-entries"
            className="flex flex-col gap-3 rounded-lg border p-4 outline-none"
          >
            {entries.length > 0 ? (
              entries.map((entry) => {
                const title = entryTitle(entry, t)
                return (
                  <div
                    key={entry.id}
                    data-testid="history-entry"
                    className="flex flex-col gap-2 border-b pb-3 last:border-b-0 last:pb-0 sm:flex-row sm:items-start sm:justify-between"
                  >
                    <div className="min-w-0">
                      <p className="font-medium wrap-break-word">{title}</p>
                      <p className="text-sm text-muted-foreground wrap-break-word">
                        {entrySummary(entry, profile.birth_date, t) ||
                          t("history.noMoreData")}
                      </p>
                    </div>
                    {confirmingId === entry.id ? (
                      <div
                        ref={confirmRef}
                        className="flex flex-wrap items-center gap-2"
                      >
                        <span id={confirmQuestionId} className="text-sm">
                          {t("history.confirmDelete")}
                        </span>
                        <LoadingButton
                          type="button"
                          size="sm"
                          variant="destructive"
                          aria-describedby={confirmQuestionId}
                          loading={deleteMutation.isPending}
                          onClick={() => deleteMutation.mutate(entry.id)}
                        >
                          {t("history.confirmDeleteYes")}
                        </LoadingButton>
                        <Button
                          type="button"
                          size="sm"
                          variant="outline"
                          disabled={deleteMutation.isPending}
                          onClick={() => {
                            setConfirmingId(null)
                            focusAfterRender(() =>
                              deleteButtons.current.get(entry.id),
                            )
                          }}
                        >
                          {t("history.cancel")}
                        </Button>
                      </div>
                    ) : (
                      <div className="flex flex-wrap gap-2">
                        {/* Visible "Editar" / "Eliminar"; the name says which
                            entry, so a screen reader's list of buttons tells
                            the rows apart. */}
                        <Button
                          type="button"
                          size="sm"
                          variant="outline"
                          aria-label={
                            title
                              ? t("history.editEntry", { title })
                              : undefined
                          }
                          onClick={() => {
                            setConfirmingId(null)
                            setMode({ kind: "form", entry })
                          }}
                        >
                          {t("history.edit")}
                        </Button>
                        <Button
                          ref={(el) => {
                            if (el) deleteButtons.current.set(entry.id, el)
                            else deleteButtons.current.delete(entry.id)
                          }}
                          type="button"
                          size="sm"
                          variant="outline"
                          aria-label={
                            title
                              ? t("history.deleteEntry", { title })
                              : undefined
                          }
                          onClick={() => {
                            setConfirmingId(entry.id)
                            focusAfterRender(() =>
                              confirmRef.current?.querySelector("button"),
                            )
                          }}
                        >
                          {t("history.delete")}
                        </Button>
                      </div>
                    )}
                  </div>
                )
              })
            ) : none ? (
              <div className="flex flex-col items-start gap-1">
                <p className="font-medium">
                  {t(`history.noneMarked.${noneKey}`)}
                </p>
                <p className="text-sm text-muted-foreground">
                  {t("history.noneHint")}
                </p>
                <LoadingButton
                  type="button"
                  variant="link"
                  className="h-auto px-0"
                  loading={noneMutation.isPending}
                  onClick={() => noneMutation.mutate(false)}
                >
                  {t("history.undo")}
                </LoadingButton>
              </div>
            ) : (
              <div className="flex flex-col items-start gap-2">
                <p className="text-sm text-muted-foreground">
                  {t("history.emptySection")}
                </p>
                <LoadingButton
                  type="button"
                  variant="outline"
                  className="whitespace-normal"
                  loading={noneMutation.isPending}
                  onClick={() => noneMutation.mutate(true)}
                >
                  {t(`history.noneButton.${noneKey}`)}
                </LoadingButton>
              </div>
            )}
          </section>
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              onClick={() => {
                setConfirmingId(null)
                setMode({ kind: "form", entry: null })
              }}
            >
              {t("history.add")}
            </Button>
          </div>
        </>
      )}
    </div>
  )
}

/** Back link shared by the section screen (kept outside Suspense). */
export function BackToProfile() {
  const { t } = useTranslation("profile")
  return (
    <Link
      to="/perfil"
      className="w-fit text-sm text-primary underline-offset-4 hover:underline"
    >
      {t("history.back")}
    </Link>
  )
}

export default HistorySection
