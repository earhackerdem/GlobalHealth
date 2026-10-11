import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { useEffect } from "react"
import { isLoggedIn } from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/google-callback")({
  component: GoogleCallback,
  head: () => ({
    meta: [
      {
        title: "Google - FastAPI Template",
      },
    ],
  }),
})

/**
 * Landing of the backend's Google OIDC callback redirect: the session token
 * arrives in the URL fragment (#access_token=...), which never reaches any
 * server or log. Store it the same way useAuth does, scrub the fragment from
 * the address bar/history and enter the app.
 */
function GoogleCallback() {
  const navigate = useNavigate()
  const { showErrorToast } = useCustomToast()

  useEffect(() => {
    const fragment = new URLSearchParams(window.location.hash.slice(1))
    const accessToken = fragment.get("access_token")
    window.history.replaceState(null, "", window.location.pathname)

    if (accessToken) {
      localStorage.setItem("access_token", accessToken)
      navigate({ to: "/" })
    } else if (isLoggedIn()) {
      // Re-run without fragment (e.g. StrictMode double effect): already in.
      navigate({ to: "/" })
    } else {
      showErrorToast("No se pudo iniciar sesión con Google")
      navigate({ to: "/login" })
    }
  }, [navigate, showErrorToast])

  return null
}
