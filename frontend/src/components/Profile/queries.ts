import { HealthRecordsService, ProfileService } from "@/client"

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
 * Shared ["history"] query: every entry of the history sections in one list
 * (GET /profile/history); /perfil counts them per card and each section
 * screen filters its own.
 */
export function getHistoryQueryOptions() {
  return {
    queryKey: ["history"],
    queryFn: async () => (await ProfileService.readHistory()).data,
  }
}

/**
 * Shared ["habits"] query (GET /profile/habits, perfil-habitos): /perfil
 * reads it for the card's badge and /perfil/habitos for the questionnaire;
 * saving invalidates it.
 */
export function getHabitsQueryOptions() {
  return {
    queryKey: ["habits"],
    queryFn: async () => (await ProfileService.readHabits()).data,
  }
}

/**
 * Shared ["work"] query (GET /profile/work, perfil-trabajo): /perfil reads it
 * for the "Trabajo" row of the basic-data card and seeds "Editar trabajo";
 * saving invalidates it.
 */
export function getWorkQueryOptions() {
  return {
    queryKey: ["work"],
    queryFn: async () => (await ProfileService.readWork()).data,
  }
}

/**
 * The patient's diagnoses (id and title), the only records a chronic entry
 * may be backed by (Story B, B-4). Under the ["health-records"] prefix, so
 * creating, editing or deleting a record refreshes it too.
 */
export function getDiagnosesQueryOptions() {
  return {
    queryKey: ["health-records", "diagnoses"],
    queryFn: async () => {
      const records = (
        await HealthRecordsService.recordsReadHealthRecords({
          query: { skip: 0, limit: 1000 },
        })
      ).data
      return records.data
        .filter((record) => record.record_type === "diagnosis")
        .map((record) => ({
          id: record.id,
          title: record.title ?? record.occurred_on,
        }))
    },
  }
}
