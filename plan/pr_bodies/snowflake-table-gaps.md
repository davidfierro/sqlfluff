<!-- Title: Snowflake: CREATE/ALTER TABLE gaps (schema evolution, generated columns, constraint actions, search optimization ON) -->
<!-- Branch: davidfierro:snowflake-table-gaps   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

CREATE TABLE
- ENABLE_SCHEMA_EVOLUTION, ERROR_LOGGING, ROW_TIMESTAMP and
  ICEBERG_DEFAULT_DDL_COLLATION parameters
- [ GENERATED ALWAYS ] AS ( <expr> ) [ VIRTUAL ] computed columns
- READ ONLY for temporary tables cloning another table
- out-of-line CHECK constraints (outoflineCH)
- inline REFERENCES with MATCH / ON UPDATE / ON DELETE and the
  constraint properties documented for inlineFK

ALTER TABLE
- SET now accepts the documented comma separated parameter list, plus
  CONTACT <purpose> = <contact_name>
- searchOptimizationAction is now wired to SearchOptimizationActionSegment
  so 'ON <search_method>( <target> )' is accepted, and the misplaced
  optional marker which made the ON clause mandatory for
  DROP/SUSPEND/RESUME SEARCH OPTIMIZATION is fixed
- constraintAction: DROP ... [ CASCADE | RESTRICT ], DROP of a
  parenthesised column list, and { ALTER | MODIFY } CONSTRAINT with
  [ NOT ] ENFORCED / VALIDATE / RELY
- { ALTER | MODIFY } COLUMN ... UNSET COMMENT

The alter_table.sql fixture contained 'DROP CONSTRAINT constraint1
UNIQUE pk_col, pk_col2', which is not valid Snowflake syntax (the
column list belongs to the PRIMARY KEY / UNIQUE / FOREIGN KEY forms,
not to DROP CONSTRAINT <name>). It has been replaced by the two valid
statements it was presumably meant to cover.

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-table
- https://docs.snowflake.com/en/sql-reference/sql/alter-table
- https://docs.snowflake.com/en/sql-reference/sql/create-table-constraint

### Are there any other side effects of this change that we should be aware of?

Two things worth flagging:

1. `SearchOptimizationActionSegment` had a misplaced `optional=True` that made the `ON` clause mandatory for `DROP`/`SUSPEND`/`RESUME SEARCH OPTIMIZATION`. That is fixed here because ALTER TABLE now delegates to that segment. The segment is shared with `ALTER DYNAMIC TABLE`, where the fix is equally correct per the docs.
2. One statement in `test/fixtures/dialects/snowflake/alter_table.sql` asserted `DROP CONSTRAINT constraint1 UNIQUE pk_col, pk_col2`, which is not valid Snowflake syntax (the column list belongs to the `PRIMARY KEY` / `UNIQUE` / `FOREIGN KEY` forms, not to `DROP CONSTRAINT <name>`). It is replaced by the two valid statements it appears to have been meant to cover, so `alter_table.yml` changes accordingly.

### Pull Request checklist
- [x] Please confirm you have completed any of the necessary steps below.

- Included test cases to demonstrate any code changes:
  - `.sql`/`.yml` parser test cases in `test/fixtures/dialects/snowflake` (YML files generated with `python test/generate_parse_fixture_yml.py -d snowflake`, and the full cross-dialect regeneration produces no unrelated diffs).
- Added appropriate documentation for the change: the docstrings of the touched segments link to the relevant official Snowflake documentation (dialect reference docs are auto-generated).
- No followup issues were needed for this change.

### AI assistance declaration

This change was developed with AI assistance: the grammar changes and the test fixtures were
drafted with an LLM. Every clause was checked against the official Snowflake documentation linked
above, and each statement in the fixtures was verified locally with
`sqlfluff parse --dialect snowflake`. The full dialect suite
(`pytest test/dialects/dialects_test.py -k snowflake` and `pytest test/dialects/snowflake_test.py`)
passes, a full `python test/generate_parse_fixture_yml.py` produces no diff outside the fixtures
listed above, and `ruff format --check` / `ruff check` are clean.
