import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"

import { ConsentService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

/**
 * Express-consent gate (NFR-004): shown on the dashboard while the session
 * user has no consent grant. The backend already rejects any health-data
 * write without consent (403 CONSENT_REQUIRED); this card is the UX that
 * collects it. Applies to both signup methods (password and Google).
 */
function ConsentGate() {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: consent, isLoading: consentLoading } = useQuery({
    queryKey: ["consent"],
    queryFn: async () =>
      (await ConsentService.readConsent({ throwOnError: false })).data ?? null,
    retry: false,
  })

  const { data: consentText } = useQuery({
    queryKey: ["consentText"],
    queryFn: async () => (await ConsentService.readConsentText()).data,
    enabled: !consentLoading && !consent,
  })

  const grantMutation = useMutation({
    mutationFn: (version: string) =>
      ConsentService.grantConsent({ body: { version } }),
    onSuccess: () => {
      showSuccessToast("Consentimiento registrado")
      queryClient.invalidateQueries({ queryKey: ["consent"] })
    },
    onError: handleError.bind(showErrorToast),
  })

  if (consentLoading || consent || !consentText) {
    return null
  }

  return (
    <Card className="mt-6 max-w-2xl" data-testid="consent-gate">
      <CardHeader>
        <CardTitle>
          Consentimiento para el tratamiento de datos de salud
        </CardTitle>
        <CardDescription>
          Antes de capturar cualquier dato de salud necesitamos tu
          consentimiento expreso (versión {consentText.version}).
        </CardDescription>
      </CardHeader>
      <CardContent>
        <p className="whitespace-pre-wrap text-sm text-muted-foreground">
          {consentText.text}
        </p>
      </CardContent>
      <CardFooter>
        <Button
          data-testid="consent-accept-button"
          disabled={grantMutation.isPending}
          onClick={() => grantMutation.mutate(consentText.version)}
        >
          Acepto el tratamiento de mis datos sensibles
        </Button>
      </CardFooter>
    </Card>
  )
}

export default ConsentGate
