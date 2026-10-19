import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import {
  type FamilyHistoryCreate,
  type FamilyHistoryPublic,
  ProfileService,
} from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError, isConflictError } from "@/utils"
import FamilyHistoryFields, {
  CONDITIONS,
  type Condition,
  type HistoryMap,
  RELATIVES,
  type Relative,
} from "./FamilyHistoryFields"

/** Current API entries → editor drafts (first entry wins per condition). */
function draftsFromEntries(entries: FamilyHistoryPublic[]): HistoryMap {
  const map: HistoryMap = {}
  for (const entry of entries) {
    const condition = entry.condition as Condition
    if (!CONDITIONS.includes(condition) || map[condition]) continue
    map[condition] = {
      relatives: entry.relatives.filter((relative): relative is Relative =>
        (RELATIVES as readonly string[]).includes(relative),
      ),
      detail: (condition === "other" ? entry.other_text : entry.note) ?? "",
    }
  }
  return map
}

/**
 * "Editar antecedentes" on /perfil (feedback de Saúl Pérez, 2026-10-19): the
 * SAME condition/relative editor as the wizard's step 2, for accounts that
 * skipped the onboarding. Saving diffs the drafts against the current entries:
 * new condition → POST, kept → PUT, unchecked → DELETE.
 */
function EditFamilyHistory({ entries }: { entries: FamilyHistoryPublic[] }) {
  const { t } = useTranslation("profile")
  const [isOpen, setIsOpen] = useState(false)
  const [history, setHistory] = useState<HistoryMap>({})
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const mutation = useMutation({
    mutationFn: async () => {
      for (const condition of CONDITIONS) {
        const draft = history[condition]
        const existing = entries.find((entry) => entry.condition === condition)
        if (!draft) {
          if (existing) {
            await ProfileService.deleteFamilyHistory({
              path: { id: existing.id },
            })
          }
          continue
        }
        const body: FamilyHistoryCreate = {
          condition,
          relatives: draft.relatives,
        }
        const detail = draft.detail.trim()
        if (detail) {
          if (condition === "other") body.other_text = detail
          else body.note = detail
        }
        if (existing) {
          await ProfileService.updateFamilyHistory({
            path: { id: existing.id },
            body,
          })
        } else {
          try {
            await ProfileService.createFamilyHistory({ body })
          } catch (err) {
            // 409: the condition already exists server-side (e.g. a retry
            // after a network cut landed the POST but lost the response) —
            // "already there" is not a failure; the invalidate refreshes it.
            if (!isConflictError(err)) throw err
          }
        }
      }
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["family-history"] })
      showSuccessToast(t("family.savedToast"))
      setIsOpen(false)
    },
    onError: async (err: Error) => {
      // The batch may have landed partially before failing: refetch so the
      // page (and the next open of this dialog) shows the real server state
      // instead of the pre-save snapshot (finding G3).
      await queryClient.invalidateQueries({ queryKey: ["family-history"] })
      handleError.call(showErrorToast, err)
    },
  })

  const handleOpenChange = (open: boolean) => {
    if (open) {
      // Seed the drafts from the current entries on every open.
      setHistory(draftsFromEntries(entries))
    }
    setIsOpen(open)
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="outline">{t("family.edit")}</Button>
      </DialogTrigger>
      <DialogContent className="max-h-[85vh] overflow-y-auto sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{t("family.edit")}</DialogTitle>
          <DialogDescription>{t("family.editDescription")}</DialogDescription>
        </DialogHeader>
        <div className="py-2">
          <FamilyHistoryFields
            value={history}
            onChange={setHistory}
            idPrefix="edit-ahf"
          />
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline" disabled={mutation.isPending}>
              {t("common:actions.cancel")}
            </Button>
          </DialogClose>
          <LoadingButton
            loading={mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            {t("common:actions.save")}
          </LoadingButton>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default EditFamilyHistory
