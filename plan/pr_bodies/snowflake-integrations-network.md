<!-- Title: Snowflake: EXTERNAL ACCESS INTEGRATION, ALTER for API/notification/security integrations, NETWORK RULE gaps, CREATE OR ALTER SEQUENCE -->
<!-- Branch: davidfierro:snowflake-integrations-network   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

- `CREATE [ OR REPLACE ] EXTERNAL ACCESS INTEGRATION` with `ALLOWED_NETWORK_RULES`,
  `ALLOWED_API_AUTHENTICATION_INTEGRATIONS`, `ALLOWED_AUTHENTICATION_SECRETS`, `ENABLED` and
  `COMMENT` — new statement segment (the generic CREATE fallback does not list the
  two-keyword `EXTERNAL ACCESS` object type).
- `ALTER { API | NOTIFICATION | EXTERNAL ACCESS | SECURITY } INTEGRATION ... SET / UNSET ...` —
  the existing segment only accepted the optional `STORAGE` keyword, so
  `ALTER API INTEGRATION i SET ENABLED = FALSE` did not parse. Each integration type gets its
  documented property set rather than one shared catch-all.
- NETWORK RULE:
  - `TYPE = { IPV6 | GCPPSCID | COMPUTE_POOL }` and `MODE = SNOWFLAKE_MANAGED_STORAGE_VOLUME`
    on CREATE
  - `ALTER NETWORK RULE <name> SET / UNSET ...` (new segment, mirroring NETWORK POLICY)

The building blocks these statements share (`ENABLED = ...`,
`ALLOWED_AUTHENTICATION_SECRETS = ...`, the tag actions and the property set common to
CREATE and ALTER of external access integrations) are added as reusable dialect grammars
rather than being spelled out in each segment.
- `CREATE OR ALTER SEQUENCE` (the sequence segment only accepted `OR REPLACE`).

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-external-access-integration
- https://docs.snowflake.com/en/sql-reference/sql/alter-api-integration
- https://docs.snowflake.com/en/sql-reference/sql/create-network-rule
- https://docs.snowflake.com/en/sql-reference/sql/alter-network-rule
- https://docs.snowflake.com/en/sql-reference/sql/create-sequence

### Are there any other side effects of this change that we should be aware of?

The ALTER INTEGRATION generalisation keeps the property sets separate per integration type, so
the existing STORAGE behaviour is unchanged and properties of one type are not accepted on
another. Following the docs, UNSET takes a single option for the API, notification, security
and network rule integrations, and only the external access integration accepts the comma
separated list its documentation shows. No existing fixture YAML changes.

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
