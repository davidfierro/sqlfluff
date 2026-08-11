<!-- Title: Snowflake: TASK gaps (identifier valued parameters, ALTER TASK actions, EXECUTE TASK options) -->
<!-- Branch: davidfierro:snowflake-task   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

CREATE TASK
- ERROR_INTEGRATION, SUCCESS_INTEGRATION and FINALIZE take an
  identifier, which the generic '<param> = <literal>' rule could not
  match. They are handled by a dedicated grammar so that parameters with
  their own segment, such as LOG_LEVEL, keep it.
- OVERLAP_POLICY = { NO_OVERLAP | ALLOW_CHILD_OVERLAP | ALLOW_ALL_OVERLAP }
- EXECUTE AS USER <user_name>
- WITH CONTACT ( <purpose> = <contact_name>, ... )

ALTER TASK
- SET of the identifier valued parameters above, plus OVERLAP_POLICY and
  CONTACT
- SET SCHEDULE = <variable>, for parity with CREATE TASK
- SET TAG / UNSET TAG
- MODIFY WHEN now takes the same boolean expression as CREATE TASK
  instead of only a boolean literal, so
  'MODIFY WHEN SYSTEM(...)' parses
- REMOVE WHEN
- MODIFY AS accepts the same bodies as CREATE TASK, including Snowflake
  Scripting blocks

EXECUTE TASK
- RETRY LAST, RETRY GRAPH RUN GROUP '<id>' and USING CONFIG = <config>

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-task
- https://docs.snowflake.com/en/sql-reference/sql/alter-task
- https://docs.snowflake.com/en/sql-reference/sql/execute-task

### Are there any other side effects of this change that we should be aware of?

The identifier valued parameters are handled by a dedicated grammar rather than by widening the generic `<param> = <value>` rule. Widening the generic rule made it win over `LogLevelEqualsSegment`, so `LOG_LEVEL = TRACE` lost its dedicated segment; the dedicated grammar avoids that.

`alter_task_modify_when.yml` changes: `MODIFY WHEN` now nests under the same expression segment that `CREATE TASK ... WHEN` already used, which is what allows `MODIFY WHEN SYSTEM$STREAM_HAS_DATA(...)` to parse.

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
