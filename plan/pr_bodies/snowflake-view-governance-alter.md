<!-- Title: Snowflake: governance policies on views and ALTER VIEW gaps -->
<!-- Branch: davidfierro:snowflake-view-governance-alter   Base: sqlfluff/sqlfluff@main   (depends on `snowflake-governance-policies`, open only after it is merged) -->

### Brief summary of the change made

CREATE VIEW
- [ WITH ] AGGREGATION POLICY <name> [ ENTITY KEY ( <cols> ) ]
- [ WITH ] JOIN POLICY <name> [ ALLOWED JOIN KEYS ( <cols> ) ]
- WITH CONTACT ( <purpose> = <contact>, ... )
- COPY TAGS
- [ WITH ] PROJECTION POLICY <name> at column level

ALTER VIEW
- SET with the documented property list: SECURE, CHANGE_TRACKING,
  CONTACT <purpose> = <contact_name> and COMMENT = '<literal>'
  (previously only the bare 'COMMENT = ...' form without SET parsed)
- UNSET SECURE / COMMENT / CONTACT <purpose> / DCM PROJECT
- SET/UNSET AGGREGATION POLICY and JOIN POLICY, with ENTITY KEY and FORCE
- DROP ALL ROW ACCESS POLICIES
- { ALTER | MODIFY } COLUMN ... SET PROJECTION POLICY <name> [ FORCE ]
  and UNSET PROJECTION POLICY

The policy clauses reuse the grammars introduced for tables so the two
statements cannot drift apart.

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-view
- https://docs.snowflake.com/en/sql-reference/sql/alter-view

### Are there any other side effects of this change that we should be aware of?

None. The policy clauses reuse the grammars introduced for tables so the two statements cannot drift apart. No existing fixture YAML changes.

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
