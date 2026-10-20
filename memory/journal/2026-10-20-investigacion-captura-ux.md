# 2026-10-20 · Investigación: captura de diagnósticos y medicinas, y experiencia "casi como Duolingo"

**Quién:** Saúl Pérez (author) lo pidió al validar perfil-cronicas (PR #26). Quería saber si ligar recetas con
diagnósticos y crónicas obliga a un catálogo, y cómo lo resuelven apps y organismos mexicanos. También pidió
investigar la mascota de onboarding, la paleta de colores y el expediente de los hijos (este último, fuera de
alcance).

**Decisiones de Saúl Pérez del mismo día:**
1. Para ligar no hace falta catálogo.
2. Las crónicas van fuera del onboarding.
3. El enlace va por medicina, no por receta.

La investigación no cambió las specs del PR #26.

**Qué se hizo:**
- **Tres investigaciones en paralelo:**
  - apps mexicanas e internacionales;
  - normas y catálogos de México, y FHIR;
  - mascota, gamificación y color.
- **Lectura del catálogo CIE-10 de la DGIS:** Saúl Pérez dejó el archivo en Descargas. Se leyó en una carpeta
  aislada del scratchpad y no se agregó al repo.
- **Hechos con fuente** en `memory/research.md#captura-catalogos` y `#mascota-color`.
- **Inbox:** tres filas nuevas, más la tabla de pendientes abiertos reparada (estaba partida por líneas en blanco).

**Hallazgo central:** el modelo híbrido (texto obligatorio más código opcional) lo respaldan tres fuentes:
- el criterio de la DGIS, según el cual el código no sustituye al texto;
- FHIR e IPS;
- las apps revisadas, que usan catálogo con salida a texto libre.

Además, el catálogo CIE-10 no reconoce cómo habla el paciente: "presión alta" y "colesterol alto" dan 0
coincidencias.

**Pendiente:**
- la decisión de Saúl Pérez sobre el modelo;
- la ronda 2 del dominio (`/product-discovery`);
- pedir a DGIS/CEMECE los términos de uso antes de embarcar el catálogo.
