import { useEffect, useRef, useState } from "react"

/** Pause without changes before sending (design.md, Guardado automático). */
const DEBOUNCE_MS = 600

/** What the status line says: "" until something is sent or blocked. */
export type SaveStatus = "" | "saving" | "saved" | "blocked" | "failed"

/**
 * Autosave of a whole questionnaire with one replacing PUT (perfil-habitos-
 * ajustes, design.md → Guardado automático and Decision 4):
 * - `schedule()` after a change: sends 600 ms later, only when `build()` says
 *   the whole draft is valid (otherwise status "blocked" and nothing goes);
 * - one PUT at a time: a change while one is in flight is sent, as the latest
 *   draft, when it ends;
 * - `flush()` sends what is pending now ("Guardar") and resolves true when
 *   everything is stored;
 * - `restore(body)` puts back what was there at opening ("Cancelar") and
 *   drops anything pending;
 * - a change still waiting when the screen unmounts (menu, back) is sent then.
 * Bodies are compared as JSON with the last one stored, so an unchanged
 * draft sends nothing. `busy` is true while a PUT is in flight (D20).
 */
export function useAutosave<B, R>(options: {
  build: () => { body: B; valid: boolean }
  initialBody: B
  put: (body: B) => Promise<R>
  /** `mounted` false: the screen is gone, refresh instead of writing over it. */
  onSaved: (response: R, mounted: boolean) => void
  /** Places a 422 and says "blocked", or "failed" for any other error. */
  onFailed: (err: unknown) => SaveStatus
}) {
  const latest = useRef(options)
  latest.current = options

  const [status, setStatus] = useState<SaveStatus>("")
  const [busy, setBusy] = useState(false)
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null)
  const inFlight = useRef<Promise<boolean> | null>(null)
  const queued = useRef(false)
  // After "Cancelar" starts restoring, later changes are not sent.
  const closed = useRef(false)
  const [initialJson] = useState(() => JSON.stringify(options.initialBody))
  const lastSaved = useRef(initialJson)
  const savedOnce = useRef(false)
  const mounted = useRef(true)

  const clearTimer = () => {
    if (timer.current === null) return
    clearTimeout(timer.current)
    timer.current = null
  }

  /** Sends `explicit` (or the latest valid draft), then the queued one. */
  const chain = async (explicit: { body: B; json: string } | null) => {
    let next = explicit
    let ok = true
    do {
      queued.current = false
      let body: B
      let json: string
      if (next) {
        ;({ body, json } = next)
        next = null
      } else {
        if (closed.current) break
        const built = latest.current.build()
        if (!built.valid) {
          setStatus("blocked")
          ok = false
          break
        }
        body = built.body
        json = JSON.stringify(body)
      }
      if (json === lastSaved.current) {
        ok = true
        setStatus(savedOnce.current ? "saved" : "")
        continue
      }
      setStatus("saving")
      setBusy(true)
      try {
        const response = await latest.current.put(body)
        lastSaved.current = json
        savedOnce.current = true
        latest.current.onSaved(response, mounted.current)
        ok = true
        setStatus("saved")
      } catch (err) {
        ok = false
        setStatus(latest.current.onFailed(err))
      }
    } while (queued.current && !closed.current)
    setBusy(false)
    return ok
  }

  const start = (explicit: { body: B; json: string } | null) => {
    const run = chain(explicit).finally(() => {
      inFlight.current = null
    })
    inFlight.current = run
    return run
  }

  const flush = (): Promise<boolean> => {
    clearTimer()
    if (inFlight.current) {
      queued.current = true
      return inFlight.current
    }
    return start(null)
  }

  const schedule = () => {
    if (closed.current) return
    if (inFlight.current) {
      queued.current = true
      return
    }
    clearTimer()
    if (!latest.current.build().valid) {
      setStatus("blocked")
      return
    }
    timer.current = setTimeout(() => {
      timer.current = null
      void flush()
    }, DEBOUNCE_MS)
  }

  /** Typing is a change too: a send already waiting waits again. */
  const postpone = () => {
    if (timer.current !== null) schedule()
  }

  const restore = async (body: B): Promise<boolean> => {
    clearTimer()
    closed.current = true
    const ok = await start({ body, json: initialJson })
    if (!ok) closed.current = false
    return ok
  }

  /** Drops what is pending without sending it ("Cancelar" with no changes). */
  const discard = () => {
    clearTimer()
    closed.current = true
  }

  // flush only reads refs and setters: the first render's is as good as the
  // latest, and this must run on unmount only.
  // biome-ignore lint/correctness/useExhaustiveDependencies: unmount only
  useEffect(() => {
    mounted.current = true
    return () => {
      mounted.current = false
      if (timer.current !== null) void flush()
    }
  }, [])

  return {
    status,
    busy,
    /** A PUT is in flight (sync, for the D20 guard against double clicks). */
    sending: () => inFlight.current !== null,
    /** What is stored differs from what was there at opening. */
    changed: () => lastSaved.current !== initialJson,
    schedule,
    postpone,
    flush,
    restore,
    discard,
  }
}
