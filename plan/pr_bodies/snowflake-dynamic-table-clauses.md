<!-- Title: Snowflake: new DYNAMIC TABLE clauses (SCHEDULER, FROZEN WHERE, REFRESH USING, EXECUTE AS USER, iceberg options) -->
<!-- Branch: davidfierro:snowflake-dynamic-table-clauses   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

CREATE DYNAMIC TABLE
- SCHEDULER = { DISABLE | ENABLE }
- FROZEN WHERE ( <expr> )
- EXECUTE AS USER <user> [ USE SECONDARY ROLES { ALL | NONE | <role>... } ]
- ROW_TIMESTAMP = { TRUE | FALSE }
- REFRESH USING ( <dml_statement> ) as an alternative to AS <query>
- iceberg options TARGET_FILE_SIZE, PATH_LAYOUT, ICEBERG_VERSION and
  PARTITION BY

ALTER DYNAMIC TABLE
- a REFRESH may target a comma separated list of dynamic tables
- SET SCHEDULER / INITIALIZATION_WAREHOUSE / EXECUTE AS USER /
  ROW_TIMESTAMP / FROZEN WHERE
- UNSET INITIALIZATION_WAREHOUSE / ROW_TIMESTAMP / FROZEN WHERE /
  EXECUTE AS USER / DCM PROJECT

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-dynamic-table
- https://docs.snowflake.com/en/sql-reference/sql/alter-dynamic-table

### Are there any other side effects of this change that we should be aware of?

None. No existing fixture YAML changes.

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
