<!-- Title: Snowflake Scripting: cursor statements and DECLARE prefixed procedure/task bodies -->
<!-- Branch: davidfierro:snowflake-scripting-cursors-declare-body   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

- OPEN <cursor> [ USING ( <bind> [ , ... ] ) ], FETCH <cursor> INTO
  <var> [ , ... ] and CLOSE <cursor>. Only DECLARE ... CURSOR FOR and
  the FOR cursor loop were supported, so a cursor driven explicitly did
  not parse.
- The body of CREATE PROCEDURE and CREATE TASK may declare variables
  before its block, i.e. 'AS DECLARE ... ; BEGIN ... END'. Both bodies
  accepted only a bare block, because the semicolon separating the
  declarations from the block is not a statement terminator there.

Reference documentation:

- https://docs.snowflake.com/en/developer-guide/snowflake-scripting/cursors
- https://docs.snowflake.com/en/sql-reference/sql/create-procedure
- https://docs.snowflake.com/en/sql-reference/sql/create-task

### Are there any other side effects of this change that we should be aware of?

None. `ScriptingDeclareStatementSegment` is left untouched: the combined `DECLARE ... ; BEGIN ... END` form is a separate grammar used only by procedure and task bodies, so top level `DECLARE` statements keep their current parse tree. No existing fixture YAML changes.

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
