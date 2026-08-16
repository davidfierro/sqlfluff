<!-- Title: Snowflake: CREATE DATA METRIC FUNCTION, TABLE(...) parameter signatures, MEMOIZABLE and other CREATE FUNCTION options -->
<!-- Branch: davidfierro:snowflake-function-gaps   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

- `CREATE [ OR REPLACE ] DATA METRIC FUNCTION <name> (arg TABLE(<col> <type>, ...))
  RETURNS <type> AS '<expr>'` — new statement segment.
- `TABLE( <type> [ , ... ] )` / `TABLE( <col> <type> [ , ... ] )` accepted as a parameter type
  in function signatures, which is how ALTER FUNCTION and DROP FUNCTION identify a data metric
  function (`DROP FUNCTION dmf(TABLE(NUMBER))`).
- CREATE FUNCTION options previously unparsable:
  - `MEMOIZABLE` (SQL UDFs)
  - `RETURNS <type> NULL` (the grammar only accepted `NOT NULL`; same fix procedures already
    received)
  - `ARTIFACT_REPOSITORY = ...` and related Python options (mirroring the procedure grammar)
  - `RESOURCE_CONSTRAINT = (architecture = 'x86')`

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-data-metric-function
- https://docs.snowflake.com/en/sql-reference/sql/create-function
- https://docs.snowflake.com/en/sql-reference/sql/drop-function

### Are there any other side effects of this change that we should be aware of?

The `TABLE(...)` parameter form is added to the shared function parameter grammar, so it is
accepted anywhere a function signature is parsed (ALTER/DROP/GRANT positions); that matches the
docs, since DMFs are addressed through their signature in all those statements. No existing
fixture YAML changes.

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
