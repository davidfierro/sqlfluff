<!-- Title: Snowflake: custom incremental dynamic tables (CUSTOM_INCREMENTAL, unbounded CHANGES, BACKFILL FROM, START AT) -->
<!-- Branch: davidfierro:snowflake-dynamic-table-custom-incremental   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

Adds the syntax introduced by Snowflake's custom incremental dynamic
tables (Public Preview 2026-05-26), which previously produced
unparsable sections:

CREATE DYNAMIC TABLE
- REFRESH_MODE = CUSTOM_INCREMENTAL as a new refresh mode value
- BACKFILL FROM <table>
- START AT ( { STREAM | TIMESTAMP | STATEMENT | OFFSET } => <expr> )

CHANGES clause
- INFORMATION is now optional, so CHANGES() parses
- the AT / BEFORE time bounds are now optional: inside a custom
  incremental dynamic table the change interval is bound automatically
  and no time bounds are allowed there

The REFRESH USING ( MERGE/INSERT INTO SELF ... ) body used by custom
incremental dynamic tables was already covered by #8308.

Reference documentation:

- https://docs.snowflake.com/en/user-guide/dynamic-tables/custom-incrementalization
- https://docs.snowflake.com/en/sql-reference/sql/create-dynamic-table

### Are there any other side effects of this change that we should be aware of?

None. The CHANGES grammar relaxation only wraps the existing content in transparent optional grammars, so all pre-existing parse trees are identical: a full cross-dialect fixture regeneration produces no diffs outside the new fixture. No existing fixture YAML changes.

### Pull Request checklist
- [x] Please confirm you have completed any of the necessary steps below.

- Included test cases to demonstrate any code changes:
  - `.sql`/`.yml` parser test cases in `test/fixtures/dialects/snowflake` (`create_dynamic_table_custom_incremental.sql`/`.yml`, generated with `python test/generate_parse_fixture_yml.py -d snowflake`, and the full cross-dialect regeneration produces no unrelated diffs).
- Added appropriate documentation for the change: the docstring of `ChangesClauseSegment` links to the official custom incrementalization documentation (dialect reference docs are auto-generated).
- No followup issues were needed for this change.

### AI assistance declaration

This change was developed with AI assistance: the grammar changes and the test fixtures were
drafted with an LLM. Every clause was checked against the official Snowflake documentation
linked above, and each statement in the fixtures was verified locally with
`sqlfluff parse --dialect snowflake`, including a real production custom incremental dynamic
table definition (58 columns, MERGE INTO SELF with two WHEN MATCHED branches and
CHANGES(INFORMATION => APPEND_ONLY)) which parses with no unparsable sections. The full
Snowflake dialect suite (`pytest test/dialects -k snowflake`, 708 tests) passes, a full
`python test/generate_parse_fixture_yml.py` produces no diff outside the fixtures listed
above, and `ruff format --check` / `ruff check` are clean.
