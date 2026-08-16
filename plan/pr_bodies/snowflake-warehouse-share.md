<!-- Title: Snowflake: adaptive warehouses (TYPE, GENERATION, ADD/DROP TABLES), name-less ALTER WAREHOUSE, ALTER SHARE SET COMMENT, CREATE OR ALTER SHARE -->
<!-- Branch: davidfierro:snowflake-warehouse-share   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

WAREHOUSE
- `WAREHOUSE_TYPE = ADAPTIVE`
- `GENERATION = '1' | '2'` (quoted enumerated values, WarehouseSize-style)
- `WITH TAG ( ... )` followed by further properties in CREATE WAREHOUSE
- `ALTER WAREHOUSE [ IF EXISTS ] { SUSPEND | RESUME | ABORT ALL QUERIES }` with the warehouse
  name omitted (the optional name reference used to swallow the action keyword)
- `ALTER WAREHOUSE <name> { ENABLE | DISABLE }`
- Adaptive warehouse actions: `ADD TABLES (...)`, `DROP TABLES (...)`, `UNSET DCM PROJECT`

SHARE
- `ALTER SHARE <name> SET COMMENT = '...'` without the `ACCOUNTS` clause
- `CREATE OR ALTER SHARE`

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-warehouse
- https://docs.snowflake.com/en/sql-reference/sql/alter-warehouse
- https://docs.snowflake.com/en/sql-reference/sql/alter-share
- https://docs.snowflake.com/en/sql-reference/sql/create-share

### Are there any other side effects of this change that we should be aware of?

The name-less ALTER WAREHOUSE forms are restricted to the actions the docs allow without a name
(SUSPEND / RESUME / ABORT ALL QUERIES): property-setting forms still require the name, and
`ALTER WAREHOUSE SET ...` remains unparsable. No existing fixture YAML changes.

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
