<!-- Title: Snowflake: PROCEDURE gaps (TEMP, argument direction, RESTRICTED CALLER, anonymous procedures, CALL INTO) -->
<!-- Branch: davidfierro:snowflake-procedure   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

CREATE PROCEDURE
- TEMP / TEMPORARY
- argument direction { IN | INPUT | OUT | OUTPUT } for SQL procedures
- EXECUTE AS RESTRICTED CALLER
- RETURNS <type> NULL, not only 'NOT NULL'
- ARTIFACT_REPOSITORY = <name>

The option list is extracted into ProcedureDefinitionOptionsGrammar so
that the anonymous procedure form can share it.

CALL
- CALL <procedure>( ... ) INTO :<variable>
- anonymous procedures: WITH <name> AS PROCEDURE ( ... ) RETURNS ...
  AS <body> CALL <name>( ... )

ALTER PROCEDURE
- EXECUTE AS RESTRICTED CALLER
- SET METRIC_LEVEL, which already had a segment that nothing referenced
- SET AUTO_EVENT_LOGGING
- LOG_LEVEL, TRACE_LEVEL and METRIC_LEVEL also accept the quoted value
  used by the documentation, in addition to the bare keyword

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-procedure
- https://docs.snowflake.com/en/sql-reference/sql/alter-procedure
- https://docs.snowflake.com/en/sql-reference/sql/call
- https://docs.snowflake.com/en/sql-reference/sql/call-with

### Are there any other side effects of this change that we should be aware of?

Two shared pieces are touched:

1. `FunctionParameterGrammar` is shared with functions, so the optional argument direction is accepted there too. It stays optional, so nothing that parsed before stops parsing.
2. `LOG_LEVEL`, `TRACE_LEVEL` and `METRIC_LEVEL` now also accept the quoted value used by the documentation, in addition to the bare keyword. This is additive and shared with tasks, dynamic tables and databases.

The CREATE PROCEDURE option list is extracted into `ProcedureDefinitionOptionsGrammar` so the anonymous procedure form can share it. No existing fixture YAML changes.

### Pull Request checklist
- [x] Please confirm you have completed any of the necessary steps below.

- Included test cases to demonstrate any code changes, which may be one or more of the following:
  - `.yml` rule test cases in `test/fixtures/rules/std_rule_cases`.
  - [x] `.sql`/`.yml` parser test cases in `test/fixtures/dialects` (note YML files can be auto generated with `tox -e generate-fixture-yml`).
  - Full autofix test cases in `test/fixtures/linter/autofix`.
  - Other.
- [x] Added appropriate documentation for the change.
- [x] Created GitHub issues for any relevant followups/future enhancements if appropriate.

### AI assistance declaration

This change was developed with AI assistance: the grammar changes and the test fixtures were
drafted with an LLM. Every clause was checked against the official Snowflake documentation linked
above, and each statement in the fixtures was verified locally with
`sqlfluff parse --dialect snowflake`. The full dialect suite
(`pytest test/dialects/dialects_test.py -k snowflake` and `pytest test/dialects/snowflake_test.py`)
passes, a full `python test/generate_parse_fixture_yml.py` produces no diff outside the fixtures
listed above, and `ruff format --check` / `ruff check` are clean.
