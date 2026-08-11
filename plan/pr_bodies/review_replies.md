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
