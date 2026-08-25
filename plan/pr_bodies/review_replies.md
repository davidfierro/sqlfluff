# Respuestas sugeridas a la revisión automática (para pegar como comentario)

Yo no puedo comentar en las PRs desde esta sesión; estos son textos listos para pegar.
Todos los fixes ya están pusheados — cada PR tiene un commit nuevo "Address automated
review feedback: ...".

## #8305 (governance-policies) — commit 95790c2

> Thanks — valid catch. `CopyTagsGrammar` is now referenced by `CREATE TABLE` instead of
> spelling the sequence inline, so there is a single source of truth. Parse trees are
> unchanged (no fixture YAML diffs).

## #8306 (table-gaps) — commit 5ab3578

> All four points were valid and are addressed:
> 1. `ALTER/MODIFY CONSTRAINT` no longer requires a property clause (`min_times=1` removed).
> 2. `DROP/ALTER/RENAME CONSTRAINT` accept quoted constraint names via `SingleIdentifierGrammar`.
> 3. `READ ONLY` is now only accepted after `TEMP`/`TEMPORARY`.
> 4. The `DROP PRIMARY KEY / UNIQUE / FOREIGN KEY` column list is bracketed-only.
> Negative cases verified locally (e.g. `CREATE TABLE t READ ONLY (...)` and an
> unparenthesised column list no longer parse).

## #8307 (materialized-view) — commit 63093e3

> Both points addressed: the two accepted positions of `RECURSIVE` are exclusive
> alternatives now (the keyword cannot appear twice), and `CLUSTER BY` on views only
> accepts the parenthesised expression list. The unbracketed `FunctionSegment` alternative
> had been copied from the table grammar, where it remains as pre-existing behaviour.

## #8308 (dynamic-table-clauses) — commit 11c3202

> Both points addressed: the comma separated table list is now only accepted by the
> `REFRESH` action, and `REFRESH USING` is restricted to DML statements
> (INSERT / MERGE / UPDATE / DELETE). Verified that
> `ALTER DYNAMIC TABLE t1, t2 SET SCHEDULER = DISABLE` and `REFRESH USING (DROP TABLE x)`
> no longer parse.

## #8309 (stream)

> (Sin hallazgos del bot de revisión — no requiere respuesta.)

## #8310 (task) — commit 9e95c98

> Both points addressed: several identifier valued parameters can now be combined in one
> `ALTER TASK ... SET` (both space separated and in the comma separated list), and the
> fixture statement mixing `SCHEDULE` and `AFTER` has been split into two, since Snowflake
> treats them as mutually exclusive.

## #8311 (procedure) — commit aac6f4c

> Both points addressed: the argument direction now lives in a procedure-specific parameter
> list (`CREATE FUNCTION f(x OUT INT)` no longer parses), and the quoted forms of
> LOG_LEVEL / TRACE_LEVEL / METRIC_LEVEL / AUTO_EVENT_LOGGING accept only the documented
> values, following the existing `WarehouseSize` pattern.

## Respuesta al aviso de github-actions ("possible bot"), para cualquiera de las PRs

> Confirming there is a human behind this contribution. AI assistance was used to draft the
> grammar and fixtures, as disclosed in the AI assistance declaration in the description;
> every clause was validated against the official Snowflake documentation and the full
> dialect test suite locally, and I take responsibility for the final result.

---

# Segunda ronda (PRs #8342, #8343, #8344)

## #8342 (view-governance) — commit 7569f68

> Valid catch, addressed. The single-property SET/UNSET alternatives that duplicated the
> unified property clauses are removed (the legacy bare `COMMENT = ...` form stays, as it is
> not covered elsewhere). While fixing it we also noticed the CREATE-side grammars leaked
> their optional `WITH` into the ALTER branches, so `SET WITH AGGREGATION POLICY` parsed;
> the SET branches now spell the sequences explicitly and that form is rejected.

## #8343 (dynamic-table-columns) — commit 16d07d5

> All three points addressed:
> 1. The USING clause of the new segment now takes column references only, per the docs.
> 2. `SET PROJECTION POLICY` is spelled explicitly, so `SET WITH PROJECTION POLICY` no
>    longer parses.
> 3. The masking clause moves to a shared `MaskingPolicyGrammar`. The pre-existing inline
>    `WITH MASKING POLICY` forms of CREATE TABLE / ADD COLUMN are intentionally not rewired:
>    the existing fixtures exercise expressions there (`USING(col, col > 10)`), so
>    tightening those belongs to a separate discussion.

## #8344 (scripting-control-flow) — commit 3bc5b89

> All three points addressed:
> 1. WHILE — and, for the same reason, REPEAT ... UNTIL — now require the parenthesised
>    condition; the unbracketed forms no longer parse.
> 2. The loop body statement list moves to a shared private helper used by the four loop
>    segments.
> 3. Fixtures now cover closing labels, ITERATE, labelled BREAK/CONTINUE and
>    multi-statement CASE branches. Writing them surfaced a real bug (a CASE branch with
>    more than one statement did not parse); fixed in the same commit.

---

# Tercera ronda

## #8342 (view-governance) — respuesta al comentario de @alanmcruickshank — commit 692e360

> Good call — done. The SET/UNSET actions for aggregation, join, masking and projection
> policies now live in shared grammars (`AggregationPolicyActionGrammar`,
> `JoinPolicyActionGrammar`, `MaskingPolicyActionGrammar`, `ProjectionPolicyActionGrammar`),
> referenced from the three statements that previously spelled them out:
> `DataGovernancePolicyTagActionSegment` (tables/dynamic tables), `AlterViewStatementSegment`
> and `AlterDynamicTableColumnActionSegment`.
>
> One deliberate parse tree change: the ENTITY KEY column list of `SET AGGREGATION POLICY` on
> ALTER TABLE now parses as column references, aligning it with the CREATE side which already
> used `ColumnReferenceSegment` (that is the small YAML diff in the fixtures). I stopped short
> of unifying the row access policy actions: the view statement names the policy as a function
> reference while the table one uses an object reference, so merging those would ripple
> through pre-existing parse trees — happy to do it as a follow-up if you'd prefer.

## #8344 (scripting-control-flow) — sin respuesta necesaria

> Aprobada por @alanmcruickshank ("LGTM"); el conflicto con main quedo resuelto con el merge
> commit d66a89c y deberia reentrar en la merge queue automaticamente o con un re-queue del
> mantenedor.

---

# Ronda 2 — ola 1 (PRs #8351, #8352, #8353)

## #8351 (query-gaps) — commit f819a88

> Valid catch, addressed. The reused ANSI GroupingSetsClauseSegment let a single grouping
> expression list consume the whole bracketed list, so a ROLLUP / CUBE entry mixed with other
> expressions parsed as a function call. The Snowflake override now matches the elements one
> by one, so those entries get their `cube_rollup_clause` node. This relabels the contents of
> GROUPING SETS in the existing `select_grouping_sets` fixture (elements hang directly off the
> brackets now), in line with the tree changes this PR already declares.

## #8352 (function-gaps) — commit 8947a67

> Valid catch — the docs state OR REPLACE and IF NOT EXISTS are mutually exclusive, so the
> fixture statement was invalid. It is now split into two statements, and while re-checking
> the syntax block we also added the missing SECURE keyword to the segment.

## #8353 (table-variants) — commit a777496

> Done — the external table ROW ACCESS POLICY clause now uses the same
> `Ref.keyword("WITH", optional=True)` pattern as the event table segment. No behaviour
> change (no fixture diffs).

## #8351 (query-gaps), segundo hallazgo — commit 1922f4e

> Done — the alternatives are now passed directly to `Delimited`, which already treats its
> positional arguments as alternatives, so the nested `OneOf` was redundant. No behaviour
> change (no fixture diffs).

## #8351 (query-gaps), CI en rojo — commits ef442e1 y 244f1b6

No hace falta respuesta en el hilo salvo que el revisor pregunte; para contexto:

> The CI failures came from the CUBE / ROLLUP retyping. Reusing the ANSI segment made them
> `function_name_identifier`, which took them out of scope for keyword capitalisation and broke
> `CP01_test_fail_snowflake_group_by_cube`; the Snowflake override now keeps them as keywords
> while retaining the dedicated `cube_rollup_clause` node. A follow-up commit drops the
> `Matchable` annotation on that override, since the ANSI base class leaves `match_grammar`
> unannotated and mypy infers the narrower `Sequence` there.

---

# Ronda 2 — olas 2 y 3 (PRs #8359, #8360, #8361, #8362)

## #8359 (integrations-network) — 3 hallazgos

### 1. Propiedades de cola Azure/GCP en ALTER NOTIFICATION INTEGRATION — VÁLIDO, commit 0f344b2

> Valid catch for the outbound variants. The Azure Event Grid and Google Pub/Sub outbound
> queue pages document AZURE_EVENT_GRID_TOPIC_ENDPOINT, AZURE_TENANT_ID and
> GCP_PUBSUB_TOPIC_NAME as settable, and those are now accepted. The two inbound queue
> variants document no provider specific SET properties beyond ENABLED / COMMENT / TAG, which
> the segment already accepted, so nothing changes there.

### 2. ALTER SECURITY INTEGRATION solo modela ENABLED/COMMENT — INTENCIONADO

> This is deliberate and called out in the segment docstring. Before this PR the statement did
> not parse at all; it now covers the properties every security integration type shares. The
> type specific sets (OAuth, SAML2, SCIM, External OAuth) are a large surface that deserves its
> own PR — modelling them halfway would either miss properties or accept them on the wrong
> integration type. Happy to follow up with them separately.

### 3. CREATE EXTERNAL ACCESS INTEGRATION admite omitir propiedades obligatorias — INTENCIONADO

> ALLOWED_NETWORK_RULES and ENABLED are indeed required, but Snowflake accepts the properties
> in any order, which AnySetOf models and a Sequence would not. This mirrors the existing
> CreateExternalTableSegment in the same dialect, whose comment reads "The use of AnySetOf is
> not strictly correct here, because LOCATION and FILE_FORMAT are required parameters. They can
> however be in arbitrary order with the other parameters." The comment above the grammar says
> the same.

## #8360 (warehouse-share) — sin hallazgos

## #8361 (database-schema) — 1 hallazgo, VÁLIDO, commit c2fce71

> Good catch. The ALTER SCHEMA docs list DEFAULT_NOTEBOOK_COMPUTE_POOL_CPU and
> DEFAULT_NOTEBOOK_COMPUTE_POOL_GPU under SET but omit them from the UNSET list, so a schema
> that set either could not unset it. ALTER DATABASE documents both on either side, so the
> schema UNSET list now accepts them too.

## #8362 (data-loading) — VÁLIDO, commits abac5af y e031f53

Hallazgo del bot (P2): "LOAD_MODE and CLUSTER_AT_INGEST_TIME are now accepted for
COPY INTO <location> because that grammar expands the shared option list. Keep these
table-only options in a table-specific option list instead of adding them to
CopyOptionsSegment._copy_options_matchables."

> Valid catch, addressed. LOAD_MODE and CLUSTER_AT_INGEST_TIME are documented for
> COPY INTO <table> only, but they had been added to the copy options shared with
> COPY INTO <location>, CREATE STAGE COPY_OPTIONS and CREATE TABLE. They now live in the
> COPY INTO <table> statement and the other three no longer accept them.
>
> Reviewing for the same pattern found a second leak, fixed in the follow-up commit:
> ENDPOINT, AWS_ACCESS_POINT_ARN and USE_PRIVATELINK_ENDPOINT had been added to the stage
> parameter segments that COPY INTO shares, whose documented external location parameters are
> only STORAGE_INTEGRATION / CREDENTIALS / ENCRYPTION. The stage statements now reference per
> cloud grammars that add the stage only parameters on top of the shared ones.

## #8362 (data-loading), tercer hallazgo — VÁLIDO, commit 7b02e0e

Hallazgo del bot (P3): el refactor dejaba ENDPOINT, AWS_ACCESS_POINT_ARN y
USE_PRIVATELINK_ENDPOINT como hijos sueltos de create/alter_stage_statement mientras
STORAGE_INTEGRATION/CREDENTIALS/ENCRYPTION seguían dentro del nodo `stage_parameters`.

> Valid catch, addressed. The parameters shared with the external locations of COPY INTO move
> to grammars, which the segments COPY INTO references keep using unchanged, and the stage
> statements now reference per cloud `stage_parameters` segments (S3StageParameters,
> GCSStageParameters, AzureBlobStorageStageParameters) that group every parameter in a single
> node. Only the stage fixtures added by this PR change: the stage only parameters now sit
> inside the `stage_parameters` node instead of hanging off the statement.

---

# Revisión humana de #8352 (rubytobi) — 6 puntos, todos VÁLIDOS — commit 5b9946f

Respuesta para pegar en la PR:

> Thanks for the thorough review @rubytobi — all six points were fair, and all are addressed
> in 5b9946f:
>
> - **LANGUAGE SQL**: now accepted between the NULL clause and COMMENT, per the docs.
> - **RETURNS**: only accepts NUMBER now; `RETURNS VARCHAR` no longer parses. The node keeps
>   the ordinary `data_type` shape so the capitalisation rules still see it.
> - **Parameters**: the DMF statement gets its own parameter list — one or more named
>   arguments, each with a `TABLE( ... )` type — so bare scalar parameters are rejected.
> - **The TABLE( ... ) leak**: the shared `FunctionParameterGrammar` is back to its previous
>   shape. The `TABLE( ... )` form moves to a dedicated signature parameter list used only
>   where DMFs are addressed by signature: ALTER FUNCTION, DROP FUNCTION and the GRANT/REVOKE
>   object reference. ALTER/DROP PROCEDURE, CREATE FUNCTION and CREATE ROW ACCESS POLICY no
>   longer accept it. One caveat on GRANT: the access statement grammar does not distinguish
>   FUNCTION from PROCEDURE at the signature position (one shared object-reference rule), so
>   `GRANT ... ON PROCEDURE p(TABLE(...))` still parses; splitting that would mean
>   restructuring the whole access statement, which I would rather do as a follow-up if you
>   think it is worth it.
> - **GRANT test**: added GRANT and REVOKE fixtures using a `TABLE(NUMBER, NUMBER)` signature.
> - **OR REPLACE / IF NOT EXISTS**: now mutually exclusive in the grammar itself, matching the
>   docs (the fixture had been fixed earlier, the grammar had not).
>
> Good call on the self-review pass — the later PRs in this series went through one before
> opening, and this one predates that habit. It caught real issues here, so it is staying in
> the workflow. Thanks again!

## #8352, hallazgo del bot tras la revisión humana — VÁLIDO, commit del fix el último de la rama

Hallazgo (P3): el TABLE(...) compartido aceptaba datatypes sin nombre también en CREATE,
aunque su sintaxis exige TABLE(<col> <tipo>, ...).

> Valid catch — the CREATE syntax names every column (`TABLE( <col_arg> <data_type>, ... )`),
> while the type-only form belongs to the signature positions. The CREATE parameter list now
> uses a named-column-only table type, so `TABLE(NUMBER)` no longer parses there, and the
> signature positions (ALTER / DROP / GRANT) keep accepting the type-only form. No fixture
> changes: the existing fixtures already used named columns on CREATE.

## #8403, hallazgo del bot sobre la relajación de CHANGES — VÁLIDO el hecho; acotarlo no es viable, se plantean alternativas al mantenedor (sin cambios de código de momento)

Hallazgo (P2, confianza 4/5): hacer opcionales INFORMATION y AT/BEFORE en
`ChangesClauseSegment` aplica a toda cláusula CHANGES del dialecto, no solo a las dynamic
tables custom incremental; `CHANGES()` pasa a parsear en cualquier SELECT.

Validación: cierto. La doc de la cláusula estándar exige INFORMATION y declara "The
AT | BEFORE clause is required"; la de custom incremental permite `CHANGES()` vacío y
prohíbe los bounds. Acotar la relajación es impracticable: `ChangesClauseSegment` solo se
alcanza vía `JoinLikeClauseGrammar` (compartida por todo FROM), el cuerpo de la DT es el
`SelectableGrammar` común y `REFRESH_MODE` vive en el AnySetOf de propiedades — una
gramática libre de contexto no puede condicionar la forma de CHANGES a esa propiedad, y
duplicar la cadena de SELECT para cuerpos de DT seguiría recursando al árbol compartido en
subqueries/CTEs. Decisión: comentario exponiendo alternativas para que el mantenedor asesore.

> The observation is factually right: the relaxation applies to every `CHANGES` clause, so
> `CHANGES()` (or `CHANGES(INFORMATION => DEFAULT)` without `AT`/`BEFORE`) now parses in any
> `SELECT`, while outside custom incremental dynamic tables the docs require both
> `INFORMATION` and `AT | BEFORE`
> (https://docs.snowflake.com/en/sql-reference/constructs/changes).
>
> Scoping the relaxation to dynamic table bodies doesn't look feasible with the current
> grammar architecture, though. `ChangesClauseSegment` is only reachable through
> `JoinLikeClauseGrammar`, which is shared by every FROM expression in the dialect, and the
> body of a dynamic table is a plain `SelectableGrammar` inside `CreateTableStatementSegment`,
> with `REFRESH_MODE` sitting in an `AnySetOf` of properties elsewhere in the statement — the
> grammar can't make the shape of `CHANGES` conditional on that property. A dedicated
> select-grammar variant for dynamic table bodies would mean duplicating the whole chain
> (`SelectableGrammar` → select statement → FROM clause → from-expression element), and
> nested subqueries/CTEs would still recurse into the shared tree, so the lenient form would
> leak back in anyway.
>
> Options I can see:
>
> 1. Keep the relaxed grammar and make the docstring explicit that the permissiveness is
>    dialect-wide (parse a documented superset, as the dialect already does in similar
>    cases), leaving semantic enforcement to a potential lint rule.
> 2. Drop the `CHANGES` relaxation from this PR (keeping `CUSTOM_INCREMENTAL`,
>    `BACKFILL FROM` and `START AT`), which keeps the strict clause everywhere but leaves
>    the documented custom incremental bodies unparsable.
>
> I'd lean towards 1 as the smallest change that keeps the feature, but happy to hear how
> the maintainers would prefer to handle it.
