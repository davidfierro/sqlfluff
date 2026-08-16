<!-- Title: Snowflake: event table WITH-less clauses, external table gaps (DELTA, USING TEMPLATE, row access ON), SHOW/DESC table variants -->
<!-- Branch: davidfierro:snowflake-table-variants-gaps   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

CREATE EVENT TABLE
- `COMMENT = '...'` and `ROW ACCESS POLICY ... ON (...)` without the leading `WITH`
  (the docs mark `WITH` as optional; the grammar required it).

CREATE EXTERNAL TABLE
- `TABLE_FORMAT = DELTA`
- `[ WITH ] ROW ACCESS POLICY <name> ON (VALUE)` (the `ON (...)` part was missing)
- `CREATE EXTERNAL TABLE ... USING TEMPLATE (<query>)`

SHOW / DESCRIBE
- `SHOW { ICEBERG | HYBRID | EVENT } TABLES [ LIKE ... ] [ IN ... ]`
- `DESCRIBE { EVENT | ICEBERG } TABLE <name>`

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-event-table
- https://docs.snowflake.com/en/sql-reference/sql/create-external-table
- https://docs.snowflake.com/en/sql-reference/sql/show-tables
- https://docs.snowflake.com/en/sql-reference/sql/desc-event-table

### Are there any other side effects of this change that we should be aware of?

None expected: all changes make previously-unparsable documented syntax parse. Making `WITH`
optional on event tables does not loosen anything else, since the clauses that follow it are
unchanged. No existing fixture YAML changes.

### Pull Request checklist
- [x] Please confirm you have completed any of the necessary steps below.

- Included test cases to demonstrate any code changes:
  - `.sql`/`.yml` parser test cases in `test/fixtures/dialects/snowflake` (YML files generated
    with `python test/generate_parse_fixture_yml.py -d snowflake`, and the full cross-dialect
    regeneration produces no unrelated diffs).
- Added appropriate documentation for the change: the docstrings of the touched segments link
  to the relevant official Snowflake documentation (dialect reference docs are auto-generated).
- No followup issues were needed for this change.

### AI assistance declaration

This change was developed with AI assistance: the grammar changes and the test fixtures were
drafted with an LLM. Every clause was checked against the official Snowflake documentation
linked above, and each statement in the fixtures was verified locally with
`sqlfluff parse --dialect snowflake`. The full dialect suite
(`pytest test/dialects/dialects_test.py -k snowflake` and `pytest test/dialects/snowflake_test.py`)
passes, a full `python test/generate_parse_fixture_yml.py` produces no diff outside the fixtures
listed above, and `ruff format --check` / `ruff check` are clean.
