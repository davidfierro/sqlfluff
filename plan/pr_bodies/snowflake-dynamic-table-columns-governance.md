<!-- Title: Snowflake: DYNAMIC TABLE column level actions and governance clauses -->
<!-- Branch: davidfierro:snowflake-dynamic-table-columns-governance   Base: sqlfluff/sqlfluff@main   (depends on `snowflake-governance-policies`, open only after it is merged) -->

### Brief summary of the change made

ALTER DYNAMIC TABLE accepted no column level governance action, which
was flagged by a TODO in the dialect. It now supports the documented
dataGovnPolicyTagAction on columns through a dedicated segment:

- { ALTER | MODIFY } [ COLUMN ] <col> SET MASKING POLICY <name>
  [ USING ( <cols> ) ] [ FORCE ] / UNSET MASKING POLICY
- { ALTER | MODIFY } [ COLUMN ] <col> SET PROJECTION POLICY <name>
  [ FORCE ] / UNSET PROJECTION POLICY
- { ALTER | MODIFY } [ COLUMN ] <col> SET TAG <tag> = '<value>' [ , ... ]
  / UNSET TAG <tag> [ , ... ]

Also adds fixtures covering the governance clauses that dynamic tables
share with tables (COPY TAGS, aggregation policy, column projection
policy and WITH CONTACT), so the shared grammars stay exercised for
this statement too.

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-dynamic-table
- https://docs.snowflake.com/en/sql-reference/sql/alter-dynamic-table

### Are there any other side effects of this change that we should be aware of?

None. The column level actions live in a dedicated segment rather than being folded into `DataGovernancePolicyTagActionSegment`, so the parse trees of `ALTER TABLE` are untouched. No existing fixture YAML changes.

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
