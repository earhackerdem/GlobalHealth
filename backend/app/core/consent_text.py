"""Texto del consentimiento expreso (NFR-004).

El texto v1 es un **placeholder** redactado en es-MX, marcado
"v1-placeholder — pendiente de revisión legal": no abrir el producto a
usuarios distintos del autor antes de esa revisión (design.md §Risks).
Cada otorgamiento guarda el sha256 del texto vigente como evidencia de
qué se aceptó exactamente (consentimiento como dato, no como flag).
"""

import hashlib
from typing import Final

CONSENT_VERSION_V1: Final[str] = "v1"

CONSENT_TEXT_V1: Final[str] = (
    "Consentimiento expreso v1-placeholder — pendiente de revisión legal.\n"
    "\n"
    "Al aceptar, otorgas tu consentimiento expreso para que esta aplicación "
    "almacene y procese los datos de salud que tú mismo captures (notas, "
    "diagnósticos, estudios y recordatorios) con el único fin de mostrártelos "
    "y ayudarte a gestionarlos. Tus datos se guardan cifrados, no se comparten "
    "con terceros sin tu autorización y puedes solicitar su eliminación en "
    "cualquier momento. Este texto es un borrador (v1) y será sustituido por "
    "la versión revisada legalmente antes de abrir el servicio a más personas."
)

# Known consent texts by version; POST /consent only accepts these.
CONSENT_TEXTS: Final[dict[str, str]] = {CONSENT_VERSION_V1: CONSENT_TEXT_V1}


def consent_text_sha256(version: str) -> str:
    """Return the sha256 hex digest of the consent text for ``version``."""
    return hashlib.sha256(CONSENT_TEXTS[version].encode("utf-8")).hexdigest()
