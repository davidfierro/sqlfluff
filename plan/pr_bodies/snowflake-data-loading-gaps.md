<!-- Title: Snowflake: stage, file format and COPY INTO gaps (directory tables, s3-compatible URLs, LOAD_MODE, FILE_PROCESSOR, GCS encryption) -->
<!-- Branch: davidfierro:snowflake-data-loading-gaps   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

STAGE
- The six inline `DIRECTORY = ( ... )` blocks of CREATE STAGE are extracted into shared,
  per-cloud directory-table grammars (they had drifted apart), and gain the documented
  parameters that were missing: `AUTO_REFRESH` on internal stages, `REFRESH_ON_CREATE` on all
  external stages, and `NOTIFICATION_INTEGRATION` on the GCS and Azure branches.
- `CREATE TEMP STAGE` (only TEMPORARY was accepted).
- `s3gov://`, `s3china://` and `s3compat://` URLs, plus the `ENDPOINT = '...'` parameter for
  S3-compatible storage.
- `USE_PRIVATELINK_ENDPOINT = TRUE | FALSE`, `AWS_ACCESS_POINT_ARN = '...'`.
- `ALTER STAGE ... SET DIRECTORY = ( ENABLE = TRUE )` and `ALTER STAGE ... UNSET TAG ...`.

FILE FORMAT
- `CREATE { TEMP | TEMPORARY | VOLATILE } FILE FORMAT`.
- JSON `MULTI_LINE`, and `REPLACE_INVALID_CHARACTERS` on AVRO / ORC / XML.

COPY INTO
- Copy options `LOAD_MODE = { FULL_INGEST | ADD_FILES_COPY }` and `CLUSTER_AT_INGEST_TIME`.
- `FILE_PROCESSOR = ( SCANNER = <type> SCANNER_OPTIONS = ( ... ) )`.
- GCS encryption on external locations (`ENCRYPTION = ( TYPE = 'GCS_SSE_KMS' ... )` — the
  location grammar only offered the S3 and Azure parameter sets).
- `VALIDATION_MODE = RETURN_ROWS` (the number-suffixed forms already parsed).

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/sql/create-stage
- https://docs.snowflake.com/en/sql-reference/sql/alter-stage
- https://docs.snowflake.com/en/sql-reference/sql/create-file-format
- https://docs.snowflake.com/en/sql-reference/sql/copy-into-table
- https://docs.snowflake.com/en/sql-reference/sql/copy-into-location

### Are there any other side effects of this change that we should be aware of?

The directory-table refactor is behaviour-preserving for existing syntax (verified by the
unchanged parse trees of the existing stage fixtures); the new parameters are only accepted on
the branches where the docs list them. Everything else makes previously-unparsable documented
syntax parse. No existing fixture YAML changes beyond the fixtures listed.

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
