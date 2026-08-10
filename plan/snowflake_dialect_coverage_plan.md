# Plan de mejora de la cobertura del dialecto Snowflake en sqlfluff

> Documento de trabajo del fork `davidfierro/sqlfluff`. Vive solo en la rama
> `claude/snowflake-language-coverage-fw74db`; **no** forma parte de ninguna PR hacia upstream.

## 1. Contexto y metodología

Una auditoría empírica (2026-08-10, base commit `f878214`, sqlfluff 4.3.0) contrastó la gramática
de `src/sqlfluff/dialects/dialect_snowflake.py` con la documentación oficial de Snowflake para
siete objetos: **Table, View, Materialized View, Dynamic Table, Stream, Task y Stored Procedure**.
Se ejecutaron ~290 sentencias con `sqlfluff parse --dialect snowflake`; solo se contó como
deficiencia lo que produjo una sección `unparsable`. Resultado: **86 deficiencias confirmadas**
(Table 21, View+MV 17, Dynamic Table 15, Task 15, Procedure 12, Stream 6).

Este plan las convierte en **11 PRs acotadas contra `sqlfluff/sqlfluff`** (una por objeto siempre
que es posible; el código común se aísla en PRs base). Los números de hallazgo (`Table #14`,
`Proc #6`…) referencian las tablas de la sección 5, que reproducen la auditoría completa.

### Estrategia para el código común

Dos bloques compartidos impiden un "una PR por objeto" puro:

1. **Gobernanza de datos** — `PROJECTION POLICY` (no existe en el dialecto), `AGGREGATION POLICY`
   y `JOIN POLICY` en CREATE, `WITH CONTACT`, `COPY TAGS`, `STORAGE LIFECYCLE POLICY`. Lo usan
   Table, View, Materialized View y Dynamic Table. **Estrategia:** la PR base (A) crea las
   gramáticas reutilizables y las cablea **solo en TABLE**, con sus fixtures (una PR de gramática
   sin uso no es aceptable upstream: los cambios de dialecto se aceptan precisamente porque llevan
   fixtures que demuestran el parseo). Las PRs de View (D) y Dynamic Table (E2) solo *referencian*
   esas gramáticas: quedan pequeñas y triviales de revisar.
2. **Snowflake Scripting** — faltan `WHILE/FOR/LOOP/BREAK/CONTINUE/CASE`, los cursores
   (`OPEN/FETCH/CLOSE`) y aceptar `DECLARE` como inicio de cuerpo. Afecta a Procedure y Task.
   **Estrategia:** dos PRs propias de scripting (I, J); las PRs de Procedure (H) y Task (G)
   excluyen esos hallazgos y no dependen de nada.

Solapes menores que **no** justifican PR base (se resuelven dentro de la PR del objeto):
`AT|BEFORE (STREAM => …)` toca `FromAtExpressionSegment`/`FromBeforeExpressionSegment` (usados
también en consultas) pero va completo en la PR de Stream (F); `COPY GRANTS` tras `CLONE` toca
`CreateCloneStatementSegment` y también va en F.

## 2. Convenciones upstream (verificadas en el repo)

- **CONTRIBUTING.md**: los PRs de dialecto "will normally be accepted directly" si incluyen
  fixtures YAML y la sintaxis coincide con la doc publicada. No hace falta issue previa.
  **Obligatorio declarar la asistencia de IA** en la descripción del PR. El título del PR va
  literal a las release notes.
- **Regla ANSI-first**: si una sintaxis es ANSI-estándar, se añade primero a `dialect_ansi.py`.
  Todo lo de este plan es Snowflake-específico salvo aviso puntual en la PR B (constraints).
- **Labeler automático**: la etiqueta `snowflake` se aplica si la rama o los ficheros contienen
  "snowflake" → todas las ramas llevan prefijo `snowflake-`.
- Los `.yml` de fixtures **nunca se editan a mano** (llevan `_hash`; el job de CI `ymlchecks`
  regenera todo y falla si hay diff).
- Snowflake **no hereda keywords de ANSI** (`clear()` + repoblación): todo keyword usado en una
  gramática debe existir en `dialect_snowflake_keywords.py` o el dialecto revienta al cargar
  (`RuntimeError: Grammar refers to '<X>KeywordSegment' which was not found`). Ante la duda,
  *unreserved*, en orden alfabético.

### Checklist por PR (idéntico para las 11)

```bash
# 0. rama nueva desde upstream/main actualizado
git fetch upstream main && git checkout -b <rama> upstream/main

# 1. fixtures .sql nuevos/ampliados en test/fixtures/dialects/snowflake/
# 2. gramática en src/sqlfluff/dialects/dialect_snowflake.py
#    (docstring con enlace a la doc oficial; Ref("...") por nombre, nunca clases)
# 3. keywords nuevos en src/sqlfluff/dialects/dialect_snowflake_keywords.py
# 4. regenerar YML del dialecto y revisar el árbol A MANO (tipos correctos, no solo "parsea")
python test/generate_parse_fixture_yml.py -d snowflake
# 5. tests del dialecto
pytest test/dialects/dialects_test.py -k snowflake
pytest test/dialects/snowflake_test.py
# 6. regresiones cruzadas + suite y linting antes de abrir la PR
tox -e generate-fixture-yml        # completo; git status no debe mostrar .yml ajenos
tox -e py311                       # o py310..py314 disponible
.venv/bin/pre-commit run --all-files
```

Commitear `.sql` + `.yml` juntos. Si el parser Rust está instalado (`sqlfluff[rs]`), resincronizar
con `python utils/rustify.py build` antes de probar a mano (los ficheros Rust generados no se
commitean).

### Plantilla de cuerpo de PR

```markdown
### Brief summary of the change made

<qué sintaxis de Snowflake se soporta ahora, con enlaces a la doc oficial de cada cláusula>

### Are there any other side effects of this change that we should be aware of?

<p. ej. "none", o segmentos compartidos tocados y por qué es seguro>

### Pull Request checklist
- [x] Please confirm you have completed any of the necessary steps below.

- Included test cases to demonstrate any code changes, which may be one or more of the following:
  - `.yml` rule test cases in `test/fixtures/rules/std_rule_cases`.
  - [x] `.sql`/`.yml` parser test cases in `test/fixtures/dialects` (note YML files can be auto generated with `tox -e generate-fixture-yml`).
  - Full autofix test cases in `test/fixtures/linter/autofix`.
  - Other.
- [x] Added appropriate documentation for the change.
- [x] Created GitHub issues for any relevant followups/future enhancements if appropriate.

### AI assistance declaration
This change was developed with AI assistance (grammar implementation and test fixtures drafted
with an LLM). All syntax was validated against the official Snowflake documentation (links above)
and every fixture was verified locally with `sqlfluff parse` and the full dialect test suite.
```

## 3. Tabla de PRs, ramas y dependencias

| PR | Rama | Título de PR propuesto (inglés) | Hallazgos | Depende de |
|----|------|--------------------------------|-----------|------------|
| A | `snowflake-governance-policies` | Snowflake: data governance policies on tables (projection/aggregation/join policy, contacts, COPY TAGS, storage lifecycle) | Table #3,4,5,7,8,13,15,17,21 | — |
| B | `snowflake-table-gaps` | Snowflake: CREATE/ALTER TABLE gaps (schema evolution, generated columns, constraint actions, search optimization ON) | Table #1,2,6,9,10,11,12,14,16,18,19,20 | — |
| C | `snowflake-materialized-view` | Snowflake: MATERIALIZED VIEW gaps (CLUSTER BY, INTERACTIVE, UNSET COMMENT/TAG fixes) | MV #13-17, View #1 | — |
| D | `snowflake-view-governance-alter` | Snowflake: governance policies on views and ALTER VIEW gaps | View #2-12 | A |
| E1 | `snowflake-dynamic-table-clauses` | Snowflake: new DYNAMIC TABLE clauses (SCHEDULER, FROZEN WHERE, REFRESH USING, EXECUTE AS USER, iceberg options) | DT #1,3,4,5,6,9,10,11,12,13 | — |
| E2 | `snowflake-dynamic-table-columns-governance` | Snowflake: DYNAMIC TABLE column-level actions and governance clauses | DT #2,7,8,14,15 | A |
| F | `snowflake-stream` | Snowflake: STREAM gaps (WITH TAG, AT(STREAM =>), ON EVENT TABLE, CREATE OR ALTER, clone COPY GRANTS) | Stream #1-6 | — |
| G | `snowflake-task` | Snowflake: TASK gaps (identifier-valued parameters, ALTER TASK actions, EXECUTE TASK options) | Task #1-5,7-15 | — |
| H | `snowflake-procedure` | Snowflake: PROCEDURE gaps (TEMP, arg direction, RESTRICTED CALLER, anonymous procedures, CALL INTO) | Proc #1-5,7-11 | — |
| I | `snowflake-scripting-control-flow` | Snowflake Scripting: WHILE/FOR/LOOP/CASE control flow | Proc #12 (parte) | — |
| J | `snowflake-scripting-cursors-declare-body` | Snowflake Scripting: cursor statements and DECLARE-prefixed procedure/task bodies | Proc #6, #12 (resto), Task #6 | I (recomendado) |

### Olas de ejecución

```
Ola 1 (paralelizable, sin dependencias):  A   B   C   E1   F   G   H
                                          │
Ola 2 (tras merge de A en upstream):      ├─→ D
                                          └─→ E2
Ola 3 (mayor esfuerzo, independientes):   I ─→ J
```

- **Anti-bloqueo para D y E2**: se pueden desarrollar en local apiladas sobre la rama de A
  (rebase cuando A se mergee), pero **no se abren en upstream hasta que A esté mergeada**, para
  que su diff sea solo suyo.
- I y J pueden empezar en cualquier momento (no dependen de nadie); van en ola 3 solo porque son
  el mayor esfuerzo de diseño. J reutiliza decisiones de I (registro de sentencias de scripting),
  por eso se recomienda ese orden.
- Cada rama parte de `upstream/main` **actualizado en el momento de empezar**, no de f878214.

## 4. Detalle por PR

Convenciones de las tablas: "Dónde" = clase y línea aproximada en `dialect_snowflake.py` a commit
`f878214` (las líneas se desplazarán; la clase es la referencia real). Cada PR debe añadir el
enlace a la doc oficial en el docstring de los segmentos que toque.

---

### PR A — `snowflake-governance-policies` (base de gobernanza + Table)

Doc oficial: [create-table](https://docs.snowflake.com/en/sql-reference/sql/create-table),
[alter-table](https://docs.snowflake.com/en/sql-reference/sql/alter-table),
[alter-table-column](https://docs.snowflake.com/en/sql-reference/sql/alter-table-column).

| Hallazgo | Sintaxis | Ejemplo mínimo | Dónde |
|---|---|---|---|
| Table #3 | `[WITH] AGGREGATION POLICY p [ENTITY KEY (…)]` en CREATE | `CREATE TABLE t (a INT) WITH AGGREGATION POLICY agp ENTITY KEY (a);` | `CreateTableStatementSegment` (AnySetOf L5289-5399); reutilizar patrón de `DataGovernancePolicyTagActionSegment` L2296 |
| Table #4 | `[WITH] JOIN POLICY p [ALLOWED JOIN KEYS (…)]` en CREATE | `CREATE TABLE t (a INT) WITH JOIN POLICY jp ALLOWED JOIN KEYS (a);` | ídem; `ALLOWED JOIN KEYS` no existe en el dialecto |
| Table #5 | `[WITH] PROJECTION POLICY p` en columna | `CREATE TABLE t (c2 STRING WITH PROJECTION POLICY pp);` | `ColumnConstraintSegment` L4697-4760 (junto a MASKING POLICY L4724) |
| Table #7 | `WITH CONTACT (proposito = contacto, …)` | `CREATE TABLE t (a INT) WITH CONTACT (STEWARD = my_contact);` | `CreateTableStatementSegment` |
| Table #8 | `COPY TAGS` | `CREATE TABLE t CLONE s COPY TAGS;` | `CreateTableStatementSegment` L5363 y `CreateCloneStatementSegment` L3539 |
| Table #13 | `ALTER TABLE … SET CONTACT proposito = contacto` | `ALTER TABLE t SET CONTACT STEWARD = my_contact;` | `AlterTableStatementSegment` L2204-2216 |
| Table #15 | `ADD COLUMN … [WITH] PROJECTION POLICY` | `ALTER TABLE t ADD COLUMN c6 STRING WITH PROJECTION POLICY pp;` | `AlterTableTableColumnActionSegment` L2353-2420 |
| Table #17 | `ALTER COLUMN … SET/UNSET PROJECTION POLICY` | `ALTER TABLE t MODIFY COLUMN c SET PROJECTION POLICY pp;` | `AlterTableTableColumnActionSegment` L2464-2507 |
| Table #21 | `ADD STORAGE LIFECYCLE POLICY p ON (col)` | `ALTER TABLE t ADD STORAGE LIFECYCLE POLICY slp ON (a);` | `DataGovernancePolicyTagActionSegment` L2243 |

**Diseño**: crear gramáticas nombradas reutilizables (p. ej. `ProjectionPolicyGrammar`,
`AggregationPolicyGrammar` con `ENTITY KEY`, `JoinPolicyGrammar` con `ALLOWED JOIN KEYS`,
`ContactBracketedGrammar`, `Sequence("COPY","TAGS")`) en la sección de gramáticas del dialecto, y
referenciarlas desde los segmentos de Table. D y E2 solo añadirán `Ref(...)`.

**Keywords a verificar/añadir** (grep antes de implementar): `PROJECTION`, `CONTACT`, `ALLOWED`,
`LIFECYCLE`, `ENTITY` (unreserved).

**Fixtures**: `create_table_governance_policies.sql`, `alter_table_governance_policies.sql`
(nuevos); ampliar `create_table_clone.sql` con `COPY TAGS` si existe, o incluirlo en el nuevo.

**Hecho cuando**: los 9 ejemplos parsean sin `unparsable`, YML regenerados, suite Snowflake verde,
`tox -e generate-fixture-yml` completo sin diffs ajenos.

---

### PR B — `snowflake-table-gaps`

Doc oficial: create-table, alter-table, alter-table-column,
[create-table-constraint](https://docs.snowflake.com/en/sql-reference/sql/create-table-constraint).

| Hallazgo | Sintaxis | Ejemplo mínimo | Dónde |
|---|---|---|---|
| #1 | `ENABLE_SCHEMA_EVOLUTION = TRUE\|FALSE` | `CREATE TABLE t (c INT) ENABLE_SCHEMA_EVOLUTION = TRUE;` | `CreateTableStatementSegment` L5289-5399 (junto a CHANGE_TRACKING L5351) |
| #2 | `ROW_TIMESTAMP = TRUE\|FALSE` | `CREATE TABLE t (a INT) ROW_TIMESTAMP = TRUE;` | ídem |
| #6 | `GENERATED ALWAYS AS (expr)` | `CREATE TABLE t (a INT, b INT GENERATED ALWAYS AS (a + 1));` | `CreateTableStatementSegment` L5299-5309 (la forma sin prefijo ya parsea) |
| #9 | `READ ONLY` en CLONE temporal | `CREATE TEMP TABLE t READ ONLY CLONE s;` | `CreateTableStatementSegment` / `TemporaryGrammar` L763 |
| #10 | `CHECK` out-of-line | `CREATE TABLE t (a INT, CONSTRAINT chk CHECK (a < 100));` | `OutOfLineConstraintPropertiesSegment` L4618-4667 (OneOf L4631 solo PK/UK/FK) |
| #11 | `REFERENCES` inline con `MATCH`/`ON DELETE` | `CREATE TABLE t (c INT REFERENCES o (x) MATCH FULL ON DELETE CASCADE);` | rama REFERENCES de `ColumnConstraintSegment` L4754-4759 |
| #12 | `SET` con lista delimitada por comas | `ALTER TABLE t SET DATA_RETENTION_TIME_IN_DAYS = 30, CHANGE_TRACKING = TRUE;` | `AlterTableStatementSegment` L2204-2216 (UNSET ya usa `Delimited`) |
| #14 | `ADD/DROP SEARCH OPTIMIZATION ON método(cols)` | `ALTER TABLE t ADD SEARCH OPTIMIZATION ON EQUALITY(c1, c2);` | cablear `SearchOptimizationActionSegment` (L2623, hoy solo usado por Dynamic Table) en `AlterTableStatementSegment` L2190-2197 |
| #16 | `ALTER/MODIFY COLUMN … UNSET COMMENT` | `ALTER TABLE t MODIFY COLUMN c1 UNSET COMMENT;` | cablear `TableColumnCommentActionSegment` (L2663) o añadir rama en L2439-2462 |
| #18 | `DROP CONSTRAINT n CASCADE\|RESTRICT` | `ALTER TABLE t DROP CONSTRAINT uq1 CASCADE;` | `AlterTableConstraintActionSegment` L2597-2620 |
| #19 | `DROP UNIQUE/FOREIGN KEY (col, …)` con paréntesis | `ALTER TABLE t DROP FOREIGN KEY (a);` | ídem L2603-2612 (`Delimited` sin `Bracketed`) |
| #20 | `ALTER/MODIFY CONSTRAINT … [NOT] ENFORCED …` | `ALTER TABLE t MODIFY CONSTRAINT c1 NOT ENFORCED;` | `AlterTableConstraintActionSegment` — rama nueva (resuelve el TODO de L2200) |

**Nota ANSI**: #10/#11/#18 son sintaxis con equivalente ANSI; comprobar al implementar si el fix
natural va en `dialect_ansi.py` (y evaluar impacto en todos los dialectos con
`tox -e generate-fixture-yml` completo) o en el override de Snowflake. Si toca ANSI, considerar
separar ese trocito en PR propia — decisión al implementar, mencionándolo en la descripción.

**Keywords a verificar/añadir**: `ENABLE_SCHEMA_EVOLUTION`, `ROW_TIMESTAMP`, `GENERATED`,
`ALWAYS`, `EVOLUTION` (según cómo se modele), `READ` (existe casi seguro).

**Fixtures**: ampliar `create_table.sql` / `alter_table.sql` / `alter_table_column.sql`; nuevo
`alter_table_constraint_actions.sql`.

---

### PR C — `snowflake-materialized-view`

Doc oficial: [create-materialized-view](https://docs.snowflake.com/en/sql-reference/sql/create-materialized-view),
[alter-materialized-view](https://docs.snowflake.com/en/sql-reference/sql/alter-materialized-view),
[create-view](https://docs.snowflake.com/en/sql-reference/sql/create-view).

Contexto clave: `CREATE MATERIALIZED VIEW` se parsea por `CreateViewStatementSegment` (L6271,
`MATERIALIZED` opcional en L6287), no por el fallback genérico. Las cláusulas exclusivas de MV
deben añadirse ahí, idealmente condicionadas o al menos documentadas como MV-only.

| Hallazgo | Sintaxis | Ejemplo mínimo | Dónde |
|---|---|---|---|
| MV #13 | `CLUSTER BY (…)` — la cláusula distintiva de las MV | `CREATE MATERIALIZED VIEW mv1 CLUSTER BY (a, b) AS SELECT a, b FROM t;` | `CreateViewStatementSegment` AnySetOf L6302-6350 |
| MV #14 | `INTERACTIVE` | `CREATE SECURE INTERACTIVE MATERIALIZED VIEW mv1 AS SELECT a FROM t;` | L6282-6287 |
| MV #15 | `UNSET COMMENT` | `ALTER MATERIALIZED VIEW mv1 UNSET COMMENT;` | `AlterMaterializedViewStatementSegment` L6465-6472: UNSET reutiliza `CommentEqualsClauseSegment` (exige `= 'literal'`) — separar ramas SET/UNSET |
| MV #16 | `UNSET TAG t1 [, t2 …]` | `ALTER MATERIALIZED VIEW mv1 UNSET TAG t1;` | ídem: UNSET reutiliza `TagEqualsSegment`. **Bugfix**: el fixture `test/fixtures/dialects/snowflake/alter_materialized_view.sql` consagra la forma inválida `unset tag my_tag = '…'` — corregirlo y regenerar su YML |
| MV #17 | `SET/UNSET DATA_METRIC_SCHEDULE` | `ALTER MATERIALIZED VIEW mv1 SET DATA_METRIC_SCHEDULE = '5 MINUTE';` | OneOf L6457-6473 |
| View #1 | Orden de prefijos documentado (`RECURSIVE` tras TEMP) | `CREATE SECURE TEMPORARY RECURSIVE VIEW v1 AS SELECT a FROM t;` | `CreateViewStatementSegment` L6282-6287: unificar SECURE/RECURSIVE/temporal en un `AnySetOf` o reordenar |

**Keywords a verificar/añadir**: `INTERACTIVE`, `DATA_METRIC_SCHEDULE`.

**Fixtures**: ampliar `alter_materialized_view.sql` (corrigiendo la sentencia inválida) y
`create_view.sql`; nuevo `create_materialized_view.sql` si no existe.

---

### PR D — `snowflake-view-governance-alter` (tras merge de A)

Doc oficial: create-view, [alter-view](https://docs.snowflake.com/en/sql-reference/sql/alter-view).

| Hallazgo | Sintaxis | Ejemplo mínimo | Dónde |
|---|---|---|---|
| #2 | `PROJECTION POLICY` en columna | `CREATE VIEW v1 (c1 WITH PROJECTION POLICY pp1) AS SELECT c1 FROM t;` | lista de columnas L6305-6328 — `Ref` a gramática de PR A |
| #3 | `WITH AGGREGATION POLICY [ENTITY KEY (…)]` | `CREATE VIEW v1 WITH AGGREGATION POLICY p AS SELECT a FROM t;` | AnySetOf L6302-6350 — `Ref` a PR A |
| #4 | `WITH JOIN POLICY [ALLOWED JOIN KEYS (…)]` | `CREATE VIEW v1 WITH JOIN POLICY jp1 AS SELECT a FROM t;` | ídem |
| #5 | `COPY TAGS` | `CREATE VIEW v1 COPY GRANTS COPY TAGS AS SELECT a FROM t;` | ídem (junto a COPY GRANTS L6348) |
| #6 | `WITH CONTACT (…)` | `CREATE VIEW v1 WITH CONTACT (STEWARD = c1) AS SELECT a FROM t;` | ídem |
| #7 | `ALTER VIEW SET COMMENT` (la forma documentada) | `ALTER VIEW v1 SET COMMENT = 'x';` | `AlterViewStatementSegment` L6375 |
| #8 | `SET CHANGE_TRACKING` | `ALTER VIEW v1 SET CHANGE_TRACKING = TRUE;` | OneOf L6369-6440 |
| #9 | `DROP ALL ROW ACCESS POLICIES` | `ALTER VIEW v1 DROP ALL ROW ACCESS POLICIES;` | Delimited L6386-6403 |
| #10 | `SET/UNSET AGGREGATION POLICY` | `ALTER VIEW v1 UNSET AGGREGATION POLICY;` | OneOf L6369-6440 |
| #11 | `SET JOIN POLICY [FORCE]` | `ALTER VIEW v1 SET JOIN POLICY jp1 FORCE;` | ídem |
| #12 | `MODIFY COLUMN SET/UNSET PROJECTION POLICY` | `ALTER VIEW v1 MODIFY COLUMN c1 SET PROJECTION POLICY pp1;` | rama columna L6404-6438 |

**Fixtures**: ampliar `create_view.sql` y `alter_view.sql` (o nuevos
`create_view_governance.sql` / `alter_view_governance.sql`).

---

### PR E1 — `snowflake-dynamic-table-clauses`

Doc oficial: [create-dynamic-table](https://docs.snowflake.com/en/sql-reference/sql/create-dynamic-table),
[alter-dynamic-table](https://docs.snowflake.com/en/sql-reference/sql/alter-dynamic-table).

| Hallazgo | Sintaxis | Ejemplo mínimo | Dónde |
|---|---|---|---|
| #1 | `SCHEDULER = DISABLE\|ENABLE` en CREATE | `CREATE DYNAMIC TABLE t TARGET_LAG='5 minutes' SCHEDULER = DISABLE WAREHOUSE=wh AS SELECT a FROM b;` | `DynamicTableOptionsSegment` L5097 |
| #3 | `FROZEN WHERE (expr)` en CREATE | `… WAREHOUSE=wh FROZEN WHERE (ts < '2020-01-01') AS SELECT …;` | ídem (ALTER ya soporta `SET IMMUTABLE WHERE`) |
| #4 | `EXECUTE AS USER u [USE SECONDARY ROLES …]` | `… WAREHOUSE=wh EXECUTE AS USER my_user AS SELECT …;` | ídem |
| #5 | `ROW_TIMESTAMP = TRUE\|FALSE` | `… WAREHOUSE=wh ROW_TIMESTAMP = TRUE AS SELECT …;` | ídem |
| #6 | `REFRESH USING (dml)` como alternativa a `AS query` | `… WAREHOUSE=wh REFRESH USING (INSERT INTO t SELECT a FROM b);` | `CreateTableStatementSegment`, OneOf final L5382-5398 |
| #9 | `TARGET_FILE_SIZE` (+ `PARTITION BY`, `PATH_LAYOUT`, `ICEBERG_VERSION`) en dynamic iceberg | `CREATE DYNAMIC ICEBERG TABLE t … TARGET_FILE_SIZE = 'AUTO' AS SELECT …;` | `IcebergTableOptionsSegment` L5201 |
| #10 | Refresh multi-tabla | `ALTER DYNAMIC TABLE t1, t2, t3 REFRESH;` | `AlterDynamicTableStatementSegment` L2699 (`Delimited` de referencias) |
| #11 | `ALTER … SET SCHEDULER = DISABLE\|ENABLE` | `ALTER DYNAMIC TABLE t SET SCHEDULER = DISABLE;` | bloque SET L2712-2763 |
| #12 | `SET/UNSET INITIALIZATION_WAREHOUSE` | `ALTER DYNAMIC TABLE t SET INITIALIZATION_WAREHOUSE = wh;` | bloques SET L2712 y UNSET L2764 (CREATE ya lo soporta, L5126) |
| #13 | `ALTER … SET EXECUTE AS USER` (y `ROW_TIMESTAMP` en SET/UNSET) | `ALTER DYNAMIC TABLE t SET EXECUTE AS USER my_user;` | bloque SET L2712 |

**Extra opcional (cosmético, detectado en la auditoría)**: el regex de
`DynamicTableLagIntervalSegment` (L397) contiene `DYNAMIC|'.*'` donde `DYNAMIC` parece errata por
`DOWNSTREAM`; corregirlo aquí si no altera fixtures.

**Keywords a verificar/añadir**: `SCHEDULER`, `FROZEN`, `ROW_TIMESTAMP`, `TARGET_FILE_SIZE`,
`PATH_LAYOUT`, `ICEBERG_VERSION`, `INITIALIZATION_WAREHOUSE`, `SECONDARY` (probable existente).

**Fixtures**: ampliar `create_dynamic_table.sql` (o equivalente existente) y
`alter_dynamic_table.sql`.

---

### PR E2 — `snowflake-dynamic-table-columns-governance` (tras merge de A)

| Hallazgo | Sintaxis | Ejemplo mínimo | Dónde |
|---|---|---|---|
| #2 | `COPY TAGS` | `CREATE OR REPLACE DYNAMIC TABLE t TARGET_LAG='5 minutes' WAREHOUSE=wh COPY TAGS AS SELECT a FROM b;` | `CreateTableStatementSegment` — `Ref` a PR A |
| #7 | `WITH AGGREGATION POLICY [ENTITY KEY]` en CREATE | `… WITH AGGREGATION POLICY ap ENTITY KEY (c1) AS SELECT …;` | ídem |
| #8 | `[WITH] PROJECTION POLICY` en columna | `CREATE DYNAMIC TABLE t (c1 STRING WITH PROJECTION POLICY pp) … AS SELECT …;` | `ColumnConstraintSegment` (ya cubierto por PR A si el constraint es compartido — verificar) |
| #14 | Masking policy por columna en ALTER | `ALTER DYNAMIC TABLE t ALTER COLUMN c1 SET MASKING POLICY mp;` | resolver el TODO de L2708-2709: cablear `DataGovernancePolicyTagActionSegment` (L2243) con soporte de columna en `AlterDynamicTableStatementSegment` |
| #15 | Tags por columna en ALTER | `ALTER DYNAMIC TABLE t MODIFY COLUMN c1 SET TAG tg = 'v';` | ídem #14 |

**Fixtures**: ampliar `alter_dynamic_table.sql` y el de CREATE con columnas con políticas.

---

### PR F — `snowflake-stream`

Doc oficial: [create-stream](https://docs.snowflake.com/en/sql-reference/sql/create-stream),
[alter-stream](https://docs.snowflake.com/en/sql-reference/sql/alter-stream),
[at-before](https://docs.snowflake.com/en/sql-reference/constructs/at-before).

| Hallazgo | Sintaxis | Ejemplo mínimo | Dónde |
|---|---|---|---|
| #1 | `[WITH] TAG (t = 'v', …)` en CREATE STREAM | `CREATE OR REPLACE STREAM s WITH TAG (cost_center = 'sales') COPY GRANTS ON TABLE t;` | `CreateStreamStatementSegment` L7948 (entre nombre L7961 y COPY GRANTS L7962; reutilizar `TagBracketedEqualsSegment`) |
| #2 | `AT\|BEFORE (STREAM => 'nombre')` en CREATE STREAM | `CREATE STREAM s ON TABLE t AT (STREAM => 'oldstream');` | `FromAtExpressionSegment` L1858 y `FromBeforeExpressionSegment` L1872: añadir `STREAM` al `OneOf("TIMESTAMP","OFFSET","STATEMENT")` |
| #3 | `ON EVENT TABLE` | `CREATE STREAM s ON EVENT TABLE et;` | `CreateStreamStatementSegment` L7964-7966 (añadir `Sequence("EVENT","TABLE")`) |
| #4 | `COPY GRANTS` tras CLONE | `CREATE OR REPLACE STREAM s CLONE s2 COPY GRANTS;` | `CreateCloneStatementSegment` L3532/L3555 |
| #5 | `CREATE OR ALTER STREAM` | `CREATE OR ALTER STREAM s ON TABLE t APPEND_ONLY = TRUE;` | L7957-7958: usar `AlterOrReplaceGrammar` (patrón de `CreateDatabaseStatementSegment` L3573) |
| #6 | `AT (STREAM => …)` en consultas (time travel) | `SELECT * FROM mytable AT (STREAM => 'mystream');` | mismo fix que #2 (los segmentos se usan en el FROM de consultas) |

**Nota**: #2/#6 tocan segmentos usados por consultas generales — incluir fixtures de `SELECT` con
`AT (STREAM => …)` además de los de CREATE STREAM, y vigilar diffs de YML en fixtures ajenos.

**Fixtures**: ampliar `create_stream.sql`, `alter_stream.sql`; nuevo
`select_at_before_stream.sql` (o ampliar el fixture de time travel existente).

---

### PR G — `snowflake-task`

Doc oficial: [create-task](https://docs.snowflake.com/en/sql-reference/sql/create-task),
[alter-task](https://docs.snowflake.com/en/sql-reference/sql/alter-task),
[execute-task](https://docs.snowflake.com/en/sql-reference/sql/execute-task).

| Hallazgo | Sintaxis | Ejemplo mínimo | Dónde |
|---|---|---|---|
| #1 | `ERROR_INTEGRATION = nombre` | `CREATE TASK t1 WAREHOUSE = wh1 ERROR_INTEGRATION = my_int AS SELECT 1;` | `CreateTaskSegment` L5403: la rama genérica L5459-5469 solo acepta literales → admitir `ObjectReferenceSegment`/`NakedIdentifierSegment` como valor |
| #2 | `SUCCESS_INTEGRATION = nombre` | `… SUCCESS_INTEGRATION = my_int …` | ídem |
| #3 | `FINALIZE = tarea` | `CREATE TASK tf WAREHOUSE = wh1 FINALIZE = my_root_task AS SELECT 1;` | ídem |
| #4 | `OVERLAP_POLICY = NO_OVERLAP\|ALLOW_CHILD_OVERLAP\|ALLOW_ALL_OVERLAP` | `… OVERLAP_POLICY = ALLOW_ALL_OVERLAP …` | `CreateTaskSegment` y `AlterTaskSpecialSetClauseSegment` L8785 |
| #5 | `EXECUTE AS USER usuario` | `CREATE TASK t1 … EXECUTE AS USER admin_user AS SELECT 1;` | `CreateTaskSegment` (cláusula nueva entre AFTER y WHEN) + ALTER SET/UNSET |
| #7 | `ALTER TASK … SET` integraciones/FINALIZE | `ALTER TASK t1 SET ERROR_INTEGRATION = my_int;` | `AlterTaskSetClauseSegment` L8826 |
| #8 | `MODIFY WHEN <boolean_expr>` real | `ALTER TASK t1 MODIFY WHEN SYSTEM$STREAM_HAS_DATA('my_stream');` | `AlterTaskStatementSegment` L8780: sustituir `BooleanLiteralGrammar` por `TaskExpressionSegment` |
| #9 | `REMOVE WHEN` | `ALTER TASK t1 REMOVE WHEN;` | L8767-8781: alternativa nueva |
| #10 | `SET TAG / UNSET TAG` | `ALTER TASK t1 SET TAG env = 'prod';` | `AlterTaskStatementSegment`: rama TAG (reutilizar `TagEqualsSegment`) |
| #11 | `MODIFY AS` con bloque de scripting | `ALTER TASK t1 MODIFY AS BEGIN INSERT INTO t VALUES (1); END;` | L8778: ampliar a los cuerpos que CREATE ya admite (`TaskExpressionSegment`/bloques) |
| #12 | `SET SCHEDULE = $variable` | `ALTER TASK t1 SET SCHEDULE = $schedule_var;` | `AlterTaskSpecialSetClauseSegment` L8810-8814 (paridad con CREATE) |
| #13 | `EXECUTE TASK … RETRY LAST` | `EXECUTE TASK t1 RETRY LAST;` | `ExecuteTaskClauseSegment` L8917 |
| #14 | `EXECUTE TASK … USING CONFIG = 'json'` | `EXECUTE TASK t1 USING CONFIG = '{"k":"v"}';` | ídem |
| #15 | `EXECUTE TASK … RETRY GRAPH RUN GROUP 'id'` | `EXECUTE TASK t1 RETRY GRAPH RUN GROUP 'abc-123';` | ídem |

Extra documentado sin probar (incluir si es barato): `WITH CONTACT` en CREATE TASK y
`SET/UNSET CONTACT` en ALTER (si A ya está mergeada, es un `Ref`; si no, dejarlo para una
follow-up — no crea dependencia dura).

**Keywords a verificar/añadir**: `OVERLAP_POLICY`, `NO_OVERLAP`, `ALLOW_CHILD_OVERLAP`,
`ALLOW_ALL_OVERLAP`, `RETRY`, `GRAPH`, `GROUP` (existe), `SUCCESS_INTEGRATION`,
`ERROR_INTEGRATION` (verificar).

**Fixtures**: ampliar la familia `alter_task_*.sql` y `create_task*.sql`; nuevo
`execute_task_options.sql`.

---

### PR H — `snowflake-procedure`

Doc oficial: [create-procedure](https://docs.snowflake.com/en/sql-reference/sql/create-procedure),
[alter-procedure](https://docs.snowflake.com/en/sql-reference/sql/alter-procedure),
[call](https://docs.snowflake.com/en/sql-reference/sql/call),
[call-with](https://docs.snowflake.com/en/sql-reference/sql/call-with).

| Hallazgo | Sintaxis | Ejemplo mínimo | Dónde |
|---|---|---|---|
| #1 | `TEMP/TEMPORARY` | `CREATE OR REPLACE TEMPORARY PROCEDURE p() RETURNS VARCHAR LANGUAGE JAVASCRIPT AS 'return 1;';` | `CreateProcedureStatementSegment` L3717-3721 (`Ref("TemporaryGrammar")`) |
| #2 | Dirección de argumento `IN/INPUT/OUT/OUTPUT` | `CREATE PROCEDURE p(a IN INT, b OUT VARCHAR) RETURNS INT LANGUAGE SQL AS BEGIN RETURN a; END;` | `FunctionParameterGrammar` (override Snowflake) L866-872 |
| #3 | `EXECUTE AS RESTRICTED CALLER` | `… EXECUTE AS RESTRICTED CALLER AS BEGIN RETURN 1; END;` | L3827 (CREATE) y L3860 (ALTER) |
| #4 | `RETURNS tipo NULL` (sin NOT) | `… RETURNS VARCHAR NULL LANGUAGE PYTHON …` | L3734-3735 |
| #5 | `ARTIFACT_REPOSITORY = nombre` (Python) | `… ARTIFACT_REPOSITORY = snowflake.snowpark.pypi_shared_repository PACKAGES=('urllib3') …` | AnySetOf L3734-3829 |
| #7 | Procedimiento anónimo `WITH n AS PROCEDURE … CALL n(…)` | `WITH myproc AS PROCEDURE (x INT) RETURNS INT LANGUAGE SQL AS $$…$$ CALL myproc(1);` | segmento nuevo (p. ej. `CallWithStatementSegment`) registrado en `StatementSegment`, junto a `CallStatementSegment` L9413 |
| #8 | `CALL … INTO :var` | `CALL sv_proc1('x', 1) INTO :ret1;` | `CallStatementSegment` L9413-9426 (`Sequence("INTO", Ref("BindVariableSegment"), optional=True)`) |
| #9 | `ALTER … SET METRIC_LEVEL` | `ALTER PROCEDURE p(VARCHAR) SET METRIC_LEVEL = ALL;` | L3861-3894: referenciar `MetricLevelEqualsSegment` (L3126, ya existe) |
| #10 | `SET AUTO_EVENT_LOGGING = '…'` | `ALTER PROCEDURE p() SET AUTO_EVENT_LOGGING = 'TRACING';` | L3861-3894 |
| #11 | `LOG_LEVEL/TRACE_LEVEL` con valor entre comillas | `ALTER PROCEDURE p(INT) SET LOG_LEVEL = 'INFO';` | `LogLevelEqualsSegment` L3086 / `TraceLevelEqualsSegment` L3108 (admitir `QuotedLiteralSegment`) — **ojo**: segmentos compartidos con otros objetos (functions, etc.); vigilar diffs de YML |
| — | (excluidos: #6 cuerpo DECLARE y #12 control de flujo → PRs I/J) | | |

**Keywords a verificar/añadir**: `RESTRICTED`, `ARTIFACT_REPOSITORY`, `AUTO_EVENT_LOGGING`,
`INPUT`, `OUTPUT`, `METRIC_LEVEL` (existe si `MetricLevelEqualsSegment` funciona).

**Fixtures**: ampliar `create_procedure*.sql`, `alter_procedure.sql`, `call_procedure*.sql`;
nuevos `call_with_anonymous_procedure.sql`, `call_into.sql`.

---

### PR I — `snowflake-scripting-control-flow`

Doc oficial: [snowflake-scripting](https://docs.snowflake.com/en/developer-guide/snowflake-scripting/index):
[while](https://docs.snowflake.com/en/sql-reference/snowflake-scripting/while),
[for](https://docs.snowflake.com/en/sql-reference/snowflake-scripting/for),
[loop](https://docs.snowflake.com/en/sql-reference/snowflake-scripting/loop),
[break](https://docs.snowflake.com/en/sql-reference/snowflake-scripting/break),
[continue](https://docs.snowflake.com/en/sql-reference/snowflake-scripting/continue),
[case](https://docs.snowflake.com/en/sql-reference/snowflake-scripting/case).

Alcance (Proc #12, parte): segmentos nuevos
`ScriptingWhileStatementSegment` (`WHILE cond [DO] … END WHILE [label]`),
`ScriptingForStatementSegment` (for-range `FOR i IN [REVERSE] a TO b [DO|LOOP] … END FOR` y
for-cursor `FOR rec IN cursor DO … END FOR`),
`ScriptingLoopStatementSegment` (`LOOP … END LOOP`),
`ScriptingBreakContinueSegment` (`BREAK|CONTINUE [label]`),
`ScriptingCaseStatementSegment` (`CASE [expr] WHEN … THEN … [ELSE …] END [CASE]`).
Registro en el conjunto de sentencias de scripting (~L1560-1575, donde ya están
`ScriptingIfStatementSegment` etc.) para que funcionen dentro de `BEGIN…END`, anidados, y con el
`ForInLoopSegment` existente (L10081) como referencia de estilo.

Ejemplo mínimo que debe pasar:
```sql
BEGIN
    LET x INT := 0;
    WHILE (x < 10) DO
        x := x + 1;
    END WHILE;
    RETURN x;
END;
```

**Keywords a verificar/añadir**: `WHILE`, `LOOP`, `BREAK`, `CONTINUE`, `REVERSE`, `DO` (verificar
todos: Snowflake no hereda de ANSI).

**Fixtures**: nuevos `scripting_while.sql`, `scripting_for.sql`, `scripting_loop.sql`,
`scripting_case.sql` (bloques anónimos de nivel superior, que es donde el parser analiza
scripting; los cuerpos `$$…$$` son opacos por diseño del lexer).

---

### PR J — `snowflake-scripting-cursors-declare-body` (tras I, recomendado)

Doc oficial: [open](https://docs.snowflake.com/en/sql-reference/snowflake-scripting/open),
[fetch](https://docs.snowflake.com/en/sql-reference/snowflake-scripting/fetch),
[close](https://docs.snowflake.com/en/sql-reference/snowflake-scripting/close),
create-procedure, create-task.

| Hallazgo | Alcance | Dónde |
|---|---|---|
| Proc #12 (resto) | `OPEN cur [USING (…)]`, `FETCH cur INTO v1, v2`, `CLOSE cur` | segmentos nuevos registrados junto a los de la PR I; `DECLARE … CURSOR FOR` ya existe en `ScriptingDeclareStatementSegment` L10131 |
| Proc #6 | Cuerpo sin comillas que empieza por `DECLARE` | `CreateProcedureStatementSegment` L3830-3841: el `AS` solo admite `ScriptingBlockStatementSegment`; añadir la secuencia `DECLARE … BEGIN … END` (reutilizar `ScriptingDeclareStatementSegment`) |
| Task #6 | Ídem como cuerpo de task | `CreateTaskSegment` L5493 (`Ref("StatementSegment")` del cuerpo) — misma solución que Proc #6 |

Ejemplos mínimos: `CREATE PROCEDURE … LANGUAGE SQL AS DECLARE x INT DEFAULT 1; BEGIN RETURN x; END;`
y un bloque con `OPEN/FETCH/CLOSE` sobre un cursor declarado.

**Keywords a verificar/añadir**: `OPEN`, `FETCH`, `CLOSE` (verificar existencia).

**Fixtures**: nuevos `scripting_cursor.sql`, `create_procedure_declare_body.sql`,
`create_task_declare_body.sql`.

---

## 5. Registro completo de hallazgos de la auditoría

Para referencia autocontenida: las tablas de la sección 4 cubren los 86 hallazgos; la numeración
es la de la auditoría original por objeto (Table #1-21, View #1-12 + MV #13-17, DT #1-15,
Stream #1-6, Task #1-15, Proc #1-12). El informe completo con lo que **sí** está cubierto por
objeto está publicado como artifact de la sesión de auditoría; las ~290 sentencias de prueba
usadas quedaron en el scratchpad de esa sesión y deben reutilizarse como semilla de los fixtures
de cada PR (regenerándolas es trivial: cada tabla incluye el ejemplo mínimo).

## 6. Notas operativas

- **Flujo de PRs**: ramas en el fork `davidfierro/sqlfluff` → PR hacia `sqlfluff/sqlfluff`
  (upstream usa "Squash and Merge"; el título del PR acaba en las release notes). La sesión de
  implementación necesitará acceso al upstream para abrir las PRs vía API, o el usuario las abre
  desde la UI de GitHub.
- **Remoto upstream** en local: `git remote add upstream https://github.com/sqlfluff/sqlfluff.git`
  y partir cada rama de `upstream/main` recién fetcheado.
- **Una PR = un commit lógico** (squash al final si hace falta); mensaje y título en inglés.
- **Riesgo principal de review**: diffs de `.yml` ajenos al objeto (por tocar segmentos
  compartidos: `LogLevelEqualsSegment` en H, `FromAtExpressionSegment` en F,
  `ColumnConstraintSegment` en A/B). Ejecutar siempre `tox -e generate-fixture-yml` completo y,
  si hay diffs en otros dialectos/fixtures, explicarlos en la descripción del PR o replantear el
  cambio a un override más local.
- **Declaración de IA**: obligatoria en cada PR (plantilla en la sección 2).
- **Seguimiento**: marcar cada hallazgo como cerrado en este documento (o en un issue del fork)
  al mergearse la PR correspondiente.
