<!-- Title: Snowflake Scripting: WHILE/LOOP/REPEAT/CASE control flow -->
<!-- Branch: davidfierro:snowflake-scripting-control-flow   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

Adds the Snowflake Scripting control flow statements which had no
grammar at all:

- WHILE ( <condition> ) { DO | LOOP } ... END { WHILE | LOOP } [ <label> ]
- LOOP ... END LOOP [ <label> ]
- REPEAT ... UNTIL ( <condition> ) END REPEAT [ <label> ]
- BREAK / CONTINUE / ITERATE, with an optional label
- the CASE statement, in both its simple and searched forms, whose
  branches hold statements rather than expressions

FOR loops gain the documented counter form
'FOR <var> IN [ REVERSE ] <start> TO <end>', the LOOP spelling of DO and
END, and the optional closing label.

Loop bodies now use the same statement list construction as
ScriptingBlockStatementSegment instead of Delimited. Delimited treated
the semicolons inside a nested statement as its own delimiters, so a
loop containing an IF block did not parse; that also affected the
existing FOR loop.

Reference documentation:

- https://docs.snowflake.com/en/developer-guide/snowflake-scripting/loops
- https://docs.snowflake.com/en/sql-reference/snowflake-scripting/while
- https://docs.snowflake.com/en/sql-reference/snowflake-scripting/loop
- https://docs.snowflake.com/en/sql-reference/snowflake-scripting/repeat
- https://docs.snowflake.com/en/sql-reference/snowflake-scripting/case

### Are there any other side effects of this change that we should be aware of?

Loop bodies are rebuilt with the same statement list construction that `ScriptingBlockStatementSegment` already uses, instead of `Delimited`. `Delimited` treated the semicolons inside a nested statement as its own delimiters, so a loop containing an `IF` block did not parse. That bug also affected the existing `FOR` loop and is fixed here. `ScriptingBlockStatementSegment` also had to stop treating `; END` as its terminator when the `END` closes a nested loop or CASE. No existing fixture YAML changes.

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
