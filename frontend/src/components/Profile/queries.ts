import { ProfileService } from "@/client"

/**
 * Shared ["profile"] query options (same pattern as getRecordsQueryOptions in
 * routes/_layout/expediente.tsx:16): the home and /perfil read the one query.
 */
export function getProfileQueryOptions() {
  return {
    queryKey: ["profile"],
    queryFn: async () => (await ProfileService.readProfile()).data,
  }
}

/**
 * Shared ["history"] query: every entry of the four event sections in one
 * list (GET /profile/history); /perfil counts them per card and each section
 * screen filters its own.
 */
export function getHistoryQueryOptions() {
  return {
    queryKey: ["history"],
    queryFn: async () => (await ProfileService.readHistory()).data,
  }
}
