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
