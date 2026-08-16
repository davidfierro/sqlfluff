# Plan de mejora del dialecto Snowflake — ronda 2

> Documento de trabajo del fork `davidfierro/sqlfluff`. Vive solo en la rama
> `claude/snowflake-language-coverage-fw74db`; **no** forma parte de ninguna PR hacia upstream.
> Continúa el plan de la ronda 1 (`plan/snowflake_dialect_coverage_plan.md`), cuyas convenciones
> upstream y checklist por PR siguen vigentes y no se repiten aquí.

## 1. Contexto y alcance

La segunda auditoría empírica (2026-08-16) contrastó el dialecto Snowflake — con baseline
`upstream/main` (`dfc346c`, que ya incluye 8 de las 11 PRs de la ronda 1) **más** las ramas aún
en vuelo D (`snowflake-view-governance-alter`) y J (`snowflake-scripting-cursors-declare-body`) —
contra la documentación oficial actual de Snowflake, en las seis familias no cubiertas por la
ronda 1. Se ejecutaron ~300 sentencias con `sqlfluff parse --dialect snowflake`; solo cuenta como
gap lo que produjo una sección `unparsable`. Resultado: **65 gaps confirmados**.

Por decisión del propietario del fork quedan **fuera de esta ronda** (sin uso previsto a corto
plazo): todo lo relacionado con **Iceberg**, los objetos **ALERT** y **SECRET**, y las
propiedades por tipo de **SECURITY INTEGRATION** (esfuerzo L, valor moderado). Ver §5.

**Quedan en alcance 56 gaps → 7 PRs acotadas e independientes.** A diferencia de la ronda 1 no
hay código común entre familias: no hacen falta PRs base ni ramas apiladas, y las 7 pueden
abrirse en cualquier orden (las olas de §4 son solo dosificación para los revisores).

Todas las ramas se crean desde `upstream/main` en el momento de implementar. Prerrequisito
recomendado (no bloqueante: no hay solape de gramática): que D y J estén mergeadas, para
branchear de un main que ya las contenga y evitar ruido de conflictos en la zona de keywords.

## 2. Aprendizajes de la ronda 1 (revisiones de cubic-dev-ai y revisores humanos)

Checklist adicional obligatorio por rama, destilado de las tres rondas de revisión de las PRs
#8305–#8311 y #8342–#8344:

1. **No aflojar gramática adyacente.** Cada opción nueva debe seguir rechazando combinaciones
   inválidas (lecciones: `READ ONLY` solo tras `TEMP`; la lista con comas solo en la acción
   `REFRESH`; listas de columnas solo entre paréntesis). Por cada feature, probar 2-3 sentencias
   **negativas** con `sqlfluff parse` antes de commitear.
2. **Dominios de valores cerrados.** Valores enumerados entrecomillados via `MultiStringParser`
   (patrón `WarehouseSize`), nunca string genérico (lección de LOG_LEVEL/TRACE_LEVEL en #8311).
3. **Factorizar desde el principio.** Secuencia repetida ≥2 veces → gramática nombrada compartida
   en `dialect.add()`. El revisor humano lo pidió explícitamente en #8342 (`*PolicyActionGrammar`);
   en esta ronda aplica directo al refactor de los bloques `DIRECTORY` de `CreateStageSegment`
   (repetidos 6×) en la PR R7.
4. **El `WITH` opcional del lado CREATE no puede filtrarse a ALTER** (lección del leak
   `SET WITH AGGREGATION POLICY` en #8342): en las ramas ALTER, escribir las secuencias
   explícitas en vez de reutilizar la gramática del CREATE.
5. **`ColumnReferenceSegment` donde la doc dice columnas**, no expresiones genéricas (lección del
   `USING` de #8343 y del ENTITY KEY de #8342).
6. **Trampas conocidas del motor de gramática**: gramáticas nuevas en `add()` (no en `replace()`);
   `optional=True` en el sitio exacto (lección SearchOptimization); ninguna rama de un `OneOf`
   puede matchear vacío; `Delimited` no sirve para listas de sentencias con `;` anidados (usar el
   patrón sentencia + `AnyNumberOf(Sequence(Delimiter, sentencia), terminators=[...])`).
7. **Parámetros mutuamente excluyentes → sentencias fixture separadas** (lección SCHEDULE vs
   AFTER en #8310).
8. **Convenciones upstream**: título de PR = línea literal de release notes; declaración de
   asistencia de IA obligatoria en el cuerpo; nunca referencias a sesiones de herramientas en los
   commits (solo el trailer `Co-Authored-By`); para reconciliar PRs abiertas con main, commit de
   **merge** (upstream hace squash: el merge commit desaparece y los hilos de revisión
   sobreviven), nunca rebase + force-push.
9. **Anclas de inserción distintas por rama** en `dialect_snowflake.py` y zonas alfabéticas de
   keywords lo más separadas posible: la mayoría de conflictos de la ronda 1 vinieron de varias
   PRs insertando tras el mismo ancla.
10. **Arreglos de fixtures preexistentes inválidos** van en la misma PR, explicados en el cuerpo
    (lección de `alter_table.sql` y `alter_materialized_view.sql`).
11. **Cambios de árbol esperados** (re-etiquetados) se anuncian en el cuerpo de la PR con el
    porqué, para que el diff YML no sorprenda al revisor (lección del ENTITY KEY de #8342).

El pipeline de validación por rama es el de la ronda 1 (§2 del plan anterior): regenerar YML de
snowflake revisando el árbol a mano, `pytest test/dialects/dialects_test.py -k snowflake` +
`pytest test/dialects/snowflake_test.py`, bucle de negativos, regeneración cross-dialecto
completa sin diffs ajenos, `ruff format --check` + `ruff check`.

## 3. Las 7 PRs

Numeración R1–R7 (ronda 2). "Gap" referencia la tabla del informe de la segunda auditoría
(sección § familia · fila). Esfuerzo S/M/L por gap según el informe.

### R1 · `snowflake-query-gaps` — DML y superficie de consulta [S]

| Gap | Sintaxis | Dónde | Doc |
|---|---|---|---|
| DML·1 | GROUP BY mixto con GROUPING SETS; además ROLLUP/CUBE hoy parsean como llamada a función (árbol mal etiquetado) | `GroupByClauseSegment`: mover CUBE/ROLLUP/GROUPING SETS **dentro** del `Delimited` (patrón ya existente en `dialect_postgres.py`) | [GROUP BY](https://docs.snowflake.com/en/sql-reference/constructs/group-by) |
| DML·2 | Alias del agregado en PIVOT: `PIVOT (SUM(x) AS total FOR ...)` | `FromPivotExpressionSegment` | [PIVOT](https://docs.snowflake.com/en/sql-reference/constructs/pivot) |
| DML·3 | Alias en la lista IN de UNPIVOT: `IN (jan AS 'JANUARY')` | `FromUnpivotExpressionSegment` | [UNPIVOT](https://docs.snowflake.com/en/sql-reference/constructs/unpivot) |

Notas: el re-etiquetado de ROLLUP/CUBE **cambia árboles de fixtures existentes** → aplicar
aprendizaje 11 (anunciarlo en el cuerpo). Fixtures: `select_group_by_grouping_sets_mixed.sql` +
ampliación de los de pivot/unpivot. Keywords: ninguna nueva prevista (GROUPING/SETS existen —
verificar).

### R2 · `snowflake-table-variants-gaps` — Event Table, External Table, SHOW/DESCRIBE [S]

| Gap | Sintaxis | Dónde | Doc |
|---|---|---|---|
| Tablas·8 y 9 | Bug: `WITH` obligatorio ante `COMMENT =` y `ROW ACCESS POLICY` en CREATE EVENT TABLE | `CreateEventTableStatementSegment`: `WITH` opcional | [CREATE EVENT TABLE](https://docs.snowflake.com/en/sql-reference/sql/create-event-table) |
| Tablas·5 | `TABLE_FORMAT = DELTA` | `CreateExternalTableSegment` | [CREATE EXTERNAL TABLE](https://docs.snowflake.com/en/sql-reference/sql/create-external-table) |
| Tablas·6 | `ROW ACCESS POLICY p ON (VALUE)` (falta el `ON (...)`) | `CreateExternalTableSegment` | ídem |
| Tablas·7 | `CREATE EXTERNAL TABLE ... USING TEMPLATE (query)` | `CreateExternalTableSegment` | ídem |
| Tablas·10 | `SHOW ICEBERG\|HYBRID\|EVENT TABLES` | `ShowStatementSegment` (lista de plurales) | [SHOW TABLES](https://docs.snowflake.com/en/sql-reference/sql/show-tables) |
| Tablas·11 | `DESCRIBE EVENT\|ICEBERG TABLE` | `DescribeStatementSegment` | [DESC EVENT TABLE](https://docs.snowflake.com/en/sql-reference/sql/desc-event-table) |

Notas: la palabra `ICEBERG` en las listas de SHOW/DESCRIBE se incluye por completitud de la
lista (coste cero, misma línea); es la **única** mención a Iceberg de toda la ronda. Keywords:
ninguna nueva prevista (EVENT/HYBRID/ICEBERG/TEMPLATE/DELTA existen — verificar).

### R3 · `snowflake-function-gaps` — UDF y Data Metric Functions [M]

| Gap | Sintaxis | Dónde | Doc |
|---|---|---|---|
| Func·1 | `MEMOIZABLE` | `AnySetOf` de `CreateFunctionStatementSegment`; keyword nueva | [CREATE FUNCTION](https://docs.snowflake.com/en/sql-reference/sql/create-function) |
| Func·2 | `RETURNS <tipo> NULL` (sin NOT) | mismo fix ya aplicado a procedures en la ronda 1 | ídem |
| Func·3 | `ARTIFACT_REPOSITORY` (Python) | copiar de `ProcedureDefinitionOptionsGrammar` | ídem |
| Func·4 | `RESOURCE_CONSTRAINT = (architecture='x86')` | mismo `AnySetOf` (keyword ya existe) | ídem |
| Func·5 | `CREATE DATA METRIC FUNCTION` | segmento nuevo + registro en `StatementSegment`; keyword `METRIC` | [CREATE DMF](https://docs.snowflake.com/en/sql-reference/sql/create-data-metric-function) |
| Func·6 | Firma `TABLE(col tipo, ...)` como tipo de parámetro en ALTER/DROP FUNCTION | `FunctionParameterGrammar` — desbloquea ALTER/DROP sobre DMFs sin tocar esos segmentos | [DROP FUNCTION](https://docs.snowflake.com/en/sql-reference/sql/drop-function) |

### R4 · `snowflake-integrations-network` — integraciones y network rules [M]

| Gap | Sintaxis | Dónde | Doc |
|---|---|---|---|
| Auto·5 | `CREATE EXTERNAL ACCESS INTEGRATION` (`ALLOWED_NETWORK_RULES`, `ALLOWED_API_AUTHENTICATION_INTEGRATIONS`, `ALLOWED_AUTHENTICATION_SECRETS`, `ENABLED`, `COMMENT`) | segmento nuevo (el fallback de CREATE no lista EXTERNAL ACCESS); las referencias a secrets son identificadores — no requieren el objeto SECRET | [doc](https://docs.snowflake.com/en/sql-reference/sql/create-external-access-integration) |
| Auto·6 | `ALTER {API\|NOTIFICATION\|EXTERNAL ACCESS\|SECURITY} INTEGRATION` (hoy solo STORAGE parsea) | generalizar `AlterStorageIntegrationSegment`; aprendizaje 1: propiedades **por tipo**, no un cajón común | [doc](https://docs.snowflake.com/en/sql-reference/sql/alter-api-integration) |
| Auto·8 | NETWORK RULE: TYPE `IPV6\|GCPPSCID\|COMPUTE_POOL`, MODE `SNOWFLAKE_MANAGED_STORAGE_VOLUME` | ampliar el bloque de CREATE NETWORK RULE + keywords | [doc](https://docs.snowflake.com/en/sql-reference/sql/create-network-rule) |
| Auto·9 | `ALTER NETWORK RULE SET/UNSET` | segmento nuevo, análogo al de NETWORK POLICY | [doc](https://docs.snowflake.com/en/sql-reference/sql/alter-network-rule) |
| Auto·10 | `CREATE OR ALTER SEQUENCE` | `CreateSequenceStatementSegment`: admitir también `OR ALTER` | [doc](https://docs.snowflake.com/en/sql-reference/sql/create-sequence) |

### R5 · `snowflake-warehouse-share` — Warehouse y Share [M]

| Gap | Sintaxis | Dónde | Doc |
|---|---|---|---|
| Cont·1 | `WAREHOUSE_TYPE = ADAPTIVE` | set de tipos de warehouse | [CREATE WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/create-warehouse) |
| Cont·2 | `GENERATION = '1'\|'2'` | `WarehouseObjectPropertiesSegment` (aprendizaje 2: `MultiStringParser`) | ídem |
| Cont·3 | `WITH TAG (...)` seguido de más parámetros | bloque warehouse del fallback CREATE | ídem |
| Cont·4 | Nombre omitido: `ALTER WAREHOUSE [IF EXISTS] SUSPEND` / `ABORT ALL QUERIES` | `AlterWarehouseStatementSegment` — la ref opcional hoy se traga el keyword de acción; resolver anteponiendo las ramas de acción sin nombre | [ALTER WAREHOUSE](https://docs.snowflake.com/en/sql-reference/sql/alter-warehouse) |
| Cont·5 | `ALTER WAREHOUSE n ENABLE\|DISABLE` | `AlterWarehouseStatementSegment` | ídem |
| Cont·6 | `ADD\|DROP TABLES (...)`, `UNSET DCM PROJECT` (adaptive) | `AlterWarehouseStatementSegment` | ídem |
| Cont·15 | `ALTER SHARE SET COMMENT` sin `ACCOUNTS`; `CREATE OR ALTER SHARE` | `AlterShareStatementSegment` + fallback CREATE | [ALTER SHARE](https://docs.snowflake.com/en/sql-reference/sql/alter-share) |

### R6 · `snowflake-database-schema` — Database y Schema [M]

| Gap | Sintaxis | Dónde | Doc |
|---|---|---|---|
| Cont·7-9 | Replicación de ALTER DATABASE: `ENABLE\|DISABLE REPLICATION\|FAILOVER TO ACCOUNTS ...` (con `IGNORE EDITION CHECK`), `REFRESH`, `PRIMARY` | `OneOf` de `AlterDatabaseSegment` (familia entera ausente) | [ALTER DATABASE](https://docs.snowflake.com/en/sql-reference/sql/alter-database) |
| Cont·10 | Bug: `UNSET EVENT_TABLE` exige `= ref` | `AlterDatabaseSegment` (quitar `=` + ref del UNSET) | ídem |
| Cont·11 | Params `OAUTH_*` en CREATE DATABASE (los `ICEBERG_*` del mismo gap quedan pospuestos, §5) | `AnySetOf` de `CreateDatabaseStatementSegment` | [CREATE DATABASE](https://docs.snowflake.com/en/sql-reference/sql/create-database) |
| Cont·12 | `TRANSIENT` y cláusulas `IGNORE ...` en CLONE de schema | `CreateCloneStatementSegment` | [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema) |
| Cont·13 | Params modernos de SCHEMA (hoy 4 de ~25: EXTERNAL_VOLUME, CATALOG, LOG_LEVEL, TRACE_LEVEL, STORAGE_SERIALIZATION_POLICY, DEFAULT_DDL_COLLATION, ...) — son params genéricos de objeto y se incluyen completos | `SchemaObjectParamsSegment` + rama UNSET de `AlterSchemaStatementSegment` | [ALTER SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/alter-schema) |
| Cont·14 | `WITH CONTACT` en CREATE SCHEMA / `SET CONTACT` en ALTER | reusar `ContactBracketedGrammar` (ronda 1) | [CREATE SCHEMA](https://docs.snowflake.com/en/sql-reference/sql/create-schema) |

### R7 · `snowflake-data-loading-gaps` — Stage, File Format, COPY INTO [M/L, la mayor]

Empezar por el **refactor** (aprendizaje 3): extraer los 6 bloques `DIRECTORY = (...)` de
`CreateStageSegment` a gramáticas compartidas por familia de cloud, y sobre ellas añadir los
parámetros nuevos. Si la revisión pidiera trocear la PR, el corte natural es
stage/file-format vs copy-into.

| Gap | Sintaxis | Dónde |
|---|---|---|
| Carga·1 | `CREATE TEMP STAGE` (solo acepta TEMPORARY) | `CreateStageSegment` |
| Carga·2 | `DIRECTORY=(ENABLE=TRUE AUTO_REFRESH=TRUE)` en stage interno | bloque DIRECTORY interno |
| Carga·3 | URLs `s3gov://`, `s3china://` | regex `S3Path` |
| Carga·4 | `s3compat://` + parámetro `ENDPOINT` | regex `S3Path` + parámetro nuevo |
| Carga·5 | `REFRESH_ON_CREATE` en DIRECTORY externo; `NOTIFICATION_INTEGRATION` (rama S3) | bloques DIRECTORY (post-refactor) |
| Carga·6 | `USE_PRIVATELINK_ENDPOINT = TRUE` | `CreateStageSegment` + ALTER SET |
| Carga·7 | `AWS_ACCESS_POINT_ARN` | `S3ExternalStageParameters` |
| Carga·8 | `ALTER STAGE ... SET DIRECTORY = (ENABLE=TRUE)` | `AlterStageSegment` |
| Carga·9 | `ALTER STAGE ... UNSET TAG` (no hay rama UNSET) | `AlterStageSegment` |
| Carga·10-11 | `CREATE TEMP\|TEMPORARY\|VOLATILE FILE FORMAT` | `CreateFileFormatSegment` |
| Carga·12 | JSON `MULTI_LINE` | `JsonFileFormatTypeParameters` |
| Carga·13-15 | `REPLACE_INVALID_CHARACTERS` en AVRO/ORC/XML | `{Avro,Orc,Xml}FileFormatTypeParameters` |
| Carga·16 | `LOAD_MODE = FULL_INGEST\|ADD_FILES_COPY` | `CopyOptionsSegment` |
| Carga·17 | `FILE_PROCESSOR = (SCANNER=... SCANNER_OPTIONS=(...))` | `CopyIntoTableStatementSegment` |
| Carga·18 | Encriptación GCS en localización externa de COPY | añadir `GCSExternalStageParameters` al `OneOf` (hoy solo S3/Azure) |
| Carga·19 | `CLUSTER_AT_INGEST_TIME` | `CopyOptionsSegment` |
| Carga·20 | `VALIDATION_MODE = RETURN_ROWS` (sin número) | regex de `ValidationModeOptionSegment` |

Docs: [CREATE STAGE](https://docs.snowflake.com/en/sql-reference/sql/create-stage) ·
[ALTER STAGE](https://docs.snowflake.com/en/sql-reference/sql/alter-stage) ·
[CREATE FILE FORMAT](https://docs.snowflake.com/en/sql-reference/sql/create-file-format) ·
[COPY INTO tabla](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table) ·
[COPY INTO localización](https://docs.snowflake.com/en/sql-reference/sql/copy-into-location).

## 4. Olas de apertura

Las 7 PRs son independientes; las olas solo dosifican la carga de revisión (3+3+1, como en la
ronda 1):

1. **Ola 1 — valor diario**: R1 query-gaps, R3 function-gaps, R2 table-variants-gaps.
2. **Ola 2 — objetos y familias ausentes**: R4 integrations-network, R5 warehouse-share,
   R6 database-schema.
3. **Ola 3 — volumen**: R7 data-loading-gaps (la mayor, mejor en solitario).

Keywords nuevas previstas por PR (verificar al implementar; regla: keyword ausente =
`RuntimeError` al cargar el dialecto): R3 `MEMOIZABLE`, `METRIC`; R4 `IPV6`, `GCPPSCID`,
`SNOWFLAKE_MANAGED_STORAGE_VOLUME`-related; R5 `ADAPTIVE`, `GENERATION`, `DCM`; R6 `FAILOVER`,
`EDITION` (si no existen); R7 `ENDPOINT`, `SCANNER`, `SCANNER_OPTIONS`, `LOAD_MODE`,
`CLUSTER_AT_INGEST_TIME`, `MULTI_LINE`... Inserciones alfabéticas, zonas separadas por rama
(aprendizaje 9).

## 5. Pospuesto (fuera de esta ronda, trazabilidad)

| Gap | Qué | Motivo |
|---|---|---|
| Auto·1-2 | CREATE/ALTER ALERT | Sin uso previsto a corto plazo |
| Auto·3-4 | CREATE/ALTER SECRET | Sin uso previsto a corto plazo |
| Auto·7 | Propiedades por TYPE de CREATE SECURITY INTEGRATION | Esfuerzo L, valor moderado para linting |
| Tablas·1 | ALTER ICEBERG TABLE (REFRESH, CONVERT TO MANAGED) | Iceberg fuera de alcance |
| Tablas·2-4 | Params de CREATE ICEBERG (CATALOG_SYNC, STORAGE_SERIALIZATION_POLICY, merge-on-read) | Iceberg fuera de alcance |
| Cont·11 (parcial) | Params `ICEBERG_*` de CREATE DATABASE | Iceberg fuera de alcance |

Recuento: 65 gaps = 56 en alcance (R1: 3, R2: 7, R3: 6, R4: 5, R5: 7, R6: 8, R7: 20) + 9
pospuestos.

### Desviaciones detectadas durante la implementación (2026-08-16)

Al contrastar cada gap contra la doc oficial antes de implementarlo, dos resultaron no estar
respaldados por la documentación vigente y se descartaron (habrían provocado exactamente el
feedback de revisión que queremos evitar):

- **Func·4 `RESOURCE_CONSTRAINT` en CREATE FUNCTION**: la cadena no aparece hoy ni en
  create-function ni en create-procedure. Descartado.
- **Cont·10 "bug" de `UNSET EVENT_TABLE`**: la doc actual de ALTER DATABASE muestra
  `UNSET EVENT_TABLE = <nombre>` (con valor); la gramática actual ya coincide. Descartado.
- **Carga·5 (corrección)**: según la doc, `NOTIFICATION_INTEGRATION` en el bloque DIRECTORY
  es de GCS y Azure (no de S3); S3 admite ENABLE / REFRESH_ON_CREATE / AUTO_REFRESH. Se
  implementó doc-fiel.
- La lista de params de SCHEMA (Cont·13) se implementó completa **salvo** los 4 `ICEBERG_*`
  (ICEBERG_DEFAULT_DDL_COLLATION, ICEBERG_VERSION_DEFAULT, ICEBERG_MERGE_ON_READ_BEHAVIOR,
  ENABLE_ICEBERG_MERGE_ON_READ), excluidos de la ronda por decisión de alcance.

Total implementado: **54 gaps en 7 ramas**, todas pusheadas y validadas (suite snowflake,
negativos por feature, regeneración cross-dialecto sin diffs ajenos, ruff).

## 6. Estado de la ronda 1 (a fecha de este documento)

Mergeadas: #8305 (A), #8306 (B), #8307 (C), #8308 (E1), #8309 (F), #8310 (G), #8311 (H),
#8343 (E2). Abiertas: #8342 (D, refactor de gramáticas de acción pusheado, pendiente de
re-revisión) y #8344 (I, aprobada y mergeable). Pendiente de abrir: J
(`snowflake-scripting-cursors-declare-body`), en cuanto se mergee I.
