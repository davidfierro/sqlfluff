<!-- Title: Snowflake: data governance policies on tables (projection/aggregation/join policy, contacts, COPY TAGS, storage lifecycle) -->
<!-- Branch: davidfierro:snowflake-governance-policies   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

Adds the data governance clauses documented for CREATE TABLE and
ALTER TABLE which previously produced unparsable sections:

CREATE TABLE
- [WITH] AGGREGATION POLICY <name> [ENTITY KEY (<cols>)]
- [WITH] JOIN POLICY <name> [ALLOWED JOIN KEYS (<cols>)]
- [WITH] STORAGE LIFECYCLE POLICY <name> ON (<cols>)
- WITH CONTACT (<purpose> = <contact>, ...)
- COPY TAGS
- [WITH] PROJECTION POLICY <name> at column level

ALTER TABLE
- ADD STORAGE LIFECYCLE POLICY <name> ON (<cols>) / DROP STORAGE LIFECYCLE POLICY
- ADD COLUMN ... [WITH] PROJECTION POLICY <name>
- {ALTER|MODIFY} COLUMN ... SET PROJECTION POLICY <name> [FORCE] / UNSET PROJECTION POLICY

The policy clauses are added as reusable dialect grammars
(ProjectionPolicyGrammar, AggregationPolicyGrammar, JoinPolicyGrammar,
StorageLifecyclePolicyGrammar, ContactBracketedGrammar, CopyTagsGrammar)
because views, materialized views and dynamic tables accept the same
clauses and can reference them in follow-up changes.

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-table
- https://docs.snowflake.com/en/sql-reference/sql/alter-table
- https://docs.snowflake.com/en/sql-reference/sql/alter-table-column

### Are there any other side effects of this change that we should be aware of?

None. The new clauses are added as reusable dialect grammars (`ProjectionPolicyGrammar`, `AggregationPolicyGrammar`, `JoinPolicyGrammar`, `StorageLifecyclePolicyGrammar`, `ContactBracketedGrammar`, `CopyTagsGrammar`) because views, materialized views and dynamic tables accept the same clauses; nothing else references them yet, so no existing parse tree changes. No existing fixture YAML changes.

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
