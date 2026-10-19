import { createContext, useContext } from "react"

/**
 * Page-level API to open the record dialogs (detail / edit) BY ID.
 *
 * Root-cause constraint (delta 2026-10-18, AC8): the open/closed state of
 * these dialogs must NOT live inside a table cell or a dropdown menu. Those
 * components unmount on their own lifecycle (the list refetch on window
 * focus re-renders the rows; Radix closes the dropdown on focus loss) and an
 * unmount takes the open dialog — and everything typed in it — with it. The
 * dialogs render once at page level and the cells only ask for them by id.
 */
export interface RecordDialogsApi {
  openDetail: (recordId: string) => void
  /** Opens the "¿Modificar este registro?" confirmation; "Sí, editar" leads
   * to the edit form. Every edit entry point goes through it (finding C7). */
  openConfirm: (recordId: string) => void
  openEdit: (recordId: string) => void
}

export const RecordDialogsContext = createContext<RecordDialogsApi | null>(null)

export function useRecordDialogs(): RecordDialogsApi {
  const api = useContext(RecordDialogsContext)
  if (!api) {
    throw new Error("useRecordDialogs requires a RecordDialogsProvider")
  }
  return api
}
