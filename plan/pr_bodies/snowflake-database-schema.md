<!-- Title: Snowflake: ALTER DATABASE replication/failover family, modern schema parameters, contacts, clone clauses -->
<!-- Branch: davidfierro:snowflake-database-schema   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

DATABASE
- The whole replication family of ALTER DATABASE, previously unparsable:
  `{ ENABLE | DISABLE } { REPLICATION | FAILOVER } TO ACCOUNTS <acct> [ , ... ]
  [ IGNORE EDITION CHECK ]`, `ALTER DATABASE <name> REFRESH` and
  `ALTER DATABASE <name> PRIMARY`.
- Bug fix: `ALTER DATABASE <name> UNSET EVENT_TABLE` (the grammar demanded `= <ref>` on UNSET).
- `OAUTH_*` properties on CREATE DATABASE.

SCHEMA
- Modern object parameters on CREATE/ALTER SCHEMA (EXTERNAL_VOLUME, CATALOG, LOG_LEVEL,
  TRACE_LEVEL, STORAGE_SERIALIZATION_POLICY, DEFAULT_DDL_COLLATION, ... — the segment
  previously accepted only 4 of the ~25 documented parameters), including the matching UNSET
  list.
- `WITH CONTACT ( <purpose> = <contact> [ , ... ] )` on CREATE SCHEMA and `SET CONTACT` on
  ALTER SCHEMA, reusing the existing contact grammar.
- `CREATE TRANSIENT SCHEMA <name> CLONE <src>` and the `IGNORE { HYBRID TABLES | TABLES ... }`
  clone clauses.

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/alter-database
- https://docs.snowflake.com/en/sql-reference/sql/create-database
- https://docs.snowflake.com/en/sql-reference/sql/create-schema
- https://docs.snowflake.com/en/sql-reference/sql/alter-schema

### Are there any other side effects of this change that we should be aware of?

None expected: every change makes previously-unparsable documented syntax parse, and the UNSET
EVENT_TABLE fix only removes the spurious `= <ref>` requirement on the UNSET side (SET is
unchanged). No existing fixture YAML changes.

### Pull Request checklist
- [x] Please confirm you have completed any of the necessary steps below.

- Included test cases to demonstrate any code changes:
  - `.sql`/`.yml` parser test cases in `test/fixtures/dialects/snowflake` (YML files generated
    with `python test/generate_parse_fixture_yml.py -d snowflake`, and the full cross-dialect
    regeneration produces no unrelated diffs).
- Added appropriate documentation for the change: the docstrings of the touched segments link
  to the relevant official Snowflake documentation (dialect reference docs are auto-generated).
- No followup issues were needed for this change.

### AI assistance declaration

This change was developed with AI assistance: the grammar changes and the test fixtures were
drafted with an LLM. Every clause was checked against the official Snowflake documentation
linked above, and each statement in the fixtures was verified locally with
`sqlfluff parse --dialect snowflake`. The full dialect suite
(`pytest test/dialects/dialects_test.py -k snowflake` and `pytest test/dialects/snowflake_test.py`)
passes, a full `python test/generate_parse_fixture_yml.py` produces no diff outside the fixtures
listed above, and `ruff format --check` / `ruff check` are clean.
