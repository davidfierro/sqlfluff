<!-- Title: Snowflake: STREAM gaps (WITH TAG, AT(STREAM =>), ON EVENT TABLE, CREATE OR ALTER, clone COPY GRANTS) -->
<!-- Branch: davidfierro:snowflake-stream   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

- [ WITH ] TAG ( <tag_name> = '<value>' [ , ... ] ) on CREATE STREAM
- CREATE OR ALTER STREAM
- ON EVENT TABLE <name>
- { AT | BEFORE } ( STREAM => '<name>' ), both in CREATE STREAM and in
  time travel queries, since the AT/BEFORE segments are shared
- COPY GRANTS after CREATE ... CLONE

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-stream
- https://docs.snowflake.com/en/sql-reference/sql/alter-stream
- https://docs.snowflake.com/en/sql-reference/constructs/at-before

### Are there any other side effects of this change that we should be aware of?

`FromAtExpressionSegment` and `FromBeforeExpressionSegment` are shared with time travel in queries, so `AT ( STREAM => ... )` becomes valid there too. That matches the AT/BEFORE documentation, and the fixtures cover both positions. `CreateCloneStatementSegment` gains `COPY GRANTS` for every clonable object type it handles, which is what the CREATE ... CLONE docs specify. No existing fixture YAML changes.

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
