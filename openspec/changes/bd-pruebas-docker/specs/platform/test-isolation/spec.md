# platform/test-isolation — delta

## ADDED Requirements

### Requirement: La suite backend corre contra una base de datos de prueba dedicada
La suite de pruebas del backend SHALL ejecutarse contra una base de datos de prueba propia, servida por un
contenedor Docker separado del de desarrollo, de modo que ninguna corrida de tests lea ni modifique los datos de
desarrollo.

#### Scenario: Los datos de desarrollo sobreviven a la suite completa
- **GIVEN** el stack de desarrollo levantado con datos reales (p. ej. el usuario Google de Saúl con su
  consentimiento otorgado) y el contenedor de BD de prueba corriendo
- **WHEN** se ejecuta la suite backend completa hasta verde
- **THEN** la base de desarrollo `app` conserva exactamente los mismos usuarios, identidades OAuth y consentimientos
  que antes de la corrida, verificado consultando la BD de desarrollo antes y después

#### Scenario: La BD de prueba es efímera y se reconstruye sola
- **GIVEN** un contenedor de BD de prueba recién creado (sin datos, sin esquema)
- **WHEN** se ejecuta la suite backend
- **THEN** la suite aplica las migraciones Alembic sobre la BD de prueba antes del primer test y termina
  verdaderamente verde (0 failed / 0 errors / 0 skipped), sin pasos manuales previos

### Requirement: La suite rehúsa ejecutar contra una base que no sea de prueba
El arranque de la suite SHALL fallar de inmediato, con un mensaje claro, cuando la URL de base de datos efectiva
para los tests no identifica una base de prueba, para que un entorno mal configurado nunca degrade en una corrida
contra datos de desarrollo.

#### Scenario: Sin configuración de BD de prueba, la suite no corre
- **GIVEN** un entorno donde la variable de conexión de la BD de prueba no está definida
- **WHEN** se intenta ejecutar pytest
- **THEN** la suite aborta antes de ejecutar cualquier test, con un mensaje que indica qué variable falta y cómo
  definirla, y la base de desarrollo no recibe ninguna conexión de la suite

#### Scenario: Una URL que apunta a la base de desarrollo es rechazada
- **GIVEN** la variable de conexión de prueba definida pero apuntando a la base de desarrollo `app`
- **WHEN** se intenta ejecutar pytest
- **THEN** la suite aborta con un mensaje que explica que la base configurada no es una base de prueba

### Requirement: CI ejecuta el backend contra la base de prueba
El workflow de CI del backend SHALL ejecutar pytest contra el servicio de BD de prueba, con los mismos números de
verde que en local.

#### Scenario: CI verde con la BD de prueba
- **GIVEN** un push a una rama con PR abierto
- **WHEN** corre el workflow `test-backend`
- **THEN** pytest se ejecuta contra el servicio de BD de prueba, la suite pasa con 0 failed / 0 errors / 0 skipped
  y la cobertura sigue cumpliendo el umbral (`--fail-under=90`)
