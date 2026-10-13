# 2026-10-12 · feedback de Saúl Pérez tras probar expediente + tooling

- Saúl Pérez probó el PR #6 y su expectativa no se cumplió (él mismo: no leyó las delta specs): en México la
  receta trae varias medicinas, fecha y paciente; sin vigencia y sin diagnóstico escrito → quiere receta con
  medicinas[] y dx opcional, y como flujo principal subir FOTO de la receta con OCR+IA llenando campos.
  → fila en inbox (reshape + story de captura foto) y prototipo clickeable publicado para validar el flujo:
  https://claude.ai/artifact/PJUNDJ5d2c8R8YHq6qPXtZ
- Pidió que el ciclo genere prototipos mock para validación no técnica → fila en inbox + meta-mejora (upstream).
- Pidió comandos make de proyecto → project.mk (punto de extensión -include del Makefile del harness, sin fork):
  setup/up/front/down/stop/logs, verificados (up acotado a db db-test backend mailpit: --wait truena con el
  servicio playwright que sale 0). OJO: hasta fusionar el PR #7, `make up` pierde las GOOGLE_* (override local
  del scratchpad las repone en esta sesión).
- Su "no entiendo por qué" del error de Google quedó explicado: hueco de la US-01 (compose.yml nunca cableó las
  GOOGLE_*), no de bd-pruebas; afloró hoy al ocupar Docker el :8000. Fix durable en PR #7.
