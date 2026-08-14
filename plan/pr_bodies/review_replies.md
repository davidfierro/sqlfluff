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
