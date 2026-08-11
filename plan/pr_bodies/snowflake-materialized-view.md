<!-- Title: Snowflake: MATERIALIZED VIEW gaps (CLUSTER BY, INTERACTIVE, UNSET COMMENT/TAG fixes) -->
<!-- Branch: davidfierro:snowflake-materialized-view   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

CREATE MATERIALIZED VIEW is parsed by CreateViewStatementSegment, which
did not accept the clauses that are specific to materialized views:

- CLUSTER BY ( <expr> [ , <expr> ... ] )
- the INTERACTIVE keyword
- RECURSIVE in its documented position, after the temporary keywords

ALTER MATERIALIZED VIEW reused the SET grammar for UNSET, so
'UNSET COMMENT' and 'UNSET TAG <name>' required an '= <value>' that
Snowflake does not accept. SET and UNSET are now separate, and both
gained the documented CONTACT and DATA_METRIC_SCHEDULE clauses. SET
accepts the documented space separated list, so 'SET SECURE COMMENT =
...' parses.

The alter_materialized_view.sql fixture asserted the invalid form
'unset tag my_tag = <value>'; it now uses 'unset tag my_tag'.

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-materialized-view
- https://docs.snowflake.com/en/sql-reference/sql/alter-materialized-view
- https://docs.snowflake.com/en/sql-reference/sql/create-view

### Are there any other side effects of this change that we should be aware of?

`CREATE MATERIALIZED VIEW` is parsed by `CreateViewStatementSegment`, so `CLUSTER BY` and `INTERACTIVE` are accepted for plain views too. That is the same trade-off the segment already makes for `MATERIALIZED` itself; splitting the two statements would be a much larger change.

`test/fixtures/dialects/snowflake/alter_materialized_view.sql` asserted `unset tag my_tag = '<value>'`. `UNSET TAG` does not take a value, so the fixture is corrected to `unset tag my_tag` and its YAML changes accordingly.

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
