"""Tests specific to the snowflake dialect."""

import pytest

from sqlfluff.core import Linter
from sqlfluff.core.dialects import dialect_selector


# Deprecated: All new tests should be added as .sql and .yml files under
# `test/fixtures/dialects/snowflake`.
# See test/fixtures/dialects/README.md for more details.
@pytest.mark.parametrize(
    "segment_cls,raw",
    [
        (
            "CreateCloneStatementSegment",
            "create table orders_clone_restore clone orders at (timestamp => "
            "to_timestamp_tz('04/05/2013 01:02:03', 'mm/dd/yyyy hh24:mi:ss'));",
        ),
        ("ShowStatementSegment", "SHOW GRANTS ON ACCOUNT;"),
        ("ShowStatementSegment", "show tables history in tpch.public;"),
        ("ShowStatementSegment", "show future grants in schema sales.public;"),
        (
            "ShowStatementSegment",
            "show replication databases with primary aws_us_west_2.myaccount1.mydb1;",
        ),
        (
            "ShowStatementSegment",
            "SHOW TERSE SCHEMAS HISTORY LIKE '%META%' IN DATABASE MYDB STARTS WITH "
            "'INT' LIMIT 10 FROM 'LAST_SCHEMA';",
        ),
        ("ShowStatementSegment", "SHOW GRANTS TO ROLE SECURITYADMIN;"),
        ("ShowStatementSegment", "SHOW GRANTS OF SHARE MY_SHARE;"),
        # Testing https://github.com/sqlfluff/sqlfluff/issues/634
        (
            "SemiStructuredAccessorSegment",
            "SELECT ID :: VARCHAR as id, OBJ : userId :: VARCHAR as user_id from x",
        ),
        ("DropUserStatementSegment", "DROP USER my_user;"),
        ("AlterSessionStatementSegment", "ALTER SESSION SET TIMEZONE = 'UTC'"),
        (
            "AlterSessionStatementSegment",
            "ALTER SESSION SET ABORT_DETACHED_QUERY = FALSE",
        ),
        ("AlterSessionStatementSegment", "ALTER SESSION SET JSON_INDENT = 5"),
        (
            "AlterSessionStatementSegment",
            "ALTER SESSION UNSET ERROR_ON_NONDETERMINISTIC_MERGE;",
        ),
        (
            "AlterSessionStatementSegment",
            "ALTER SESSION UNSET TIME_OUTPUT_FORMAT, TWO_DIGIT_CENTURY_START;",
        ),
    ],
)
def test_snowflake_queries(segment_cls, raw, caplog):
    """Test snowflake specific queries parse."""
    lnt = Linter(dialect="snowflake")
    parsed = lnt.parse_string(raw)
    print(parsed.violations)
    assert len(parsed.violations) == 0

    # Find any unparsable statements
    typs = parsed.tree.type_set()
    assert "unparsable" not in typs

    # Find the expected type in the parsed segment
    seg_type = dialect_selector("snowflake").get_segment(segment_cls).type
    child_segments = [seg for seg in parsed.tree.recursive_crawl(seg_type)]
    assert len(child_segments) > 0
    # If we get here the raw statement was parsed as expected


def _violations(sql: str) -> list:
    """Return parse errors plus any unparsable nodes anywhere in the tree.

    A statement can fail to parse without raising: the parser then wraps the
    remaining tokens in an ``unparsable`` node. Collect both signals.
    """
    parsed = Linter(dialect="snowflake").parse_string(sql)
    violations: list = list(parsed.violations)
    if parsed.tree:
        violations += list(parsed.tree.recursive_crawl("unparsable"))
    return violations


# Forms the Snowflake docs do not allow. The fixture suite under
# test/fixtures/dialects/snowflake only asserts that statements parse, so the
# guards against over-permissive grammar live here.
@pytest.mark.parametrize(
    "sql",
    [
        # OBJECT_VISIBILITY = <object_visibility_spec> is a database option;
        # CREATE SCHEMA and ALTER SCHEMA document only PRIVILEGED.
        pytest.param(
            "CREATE SCHEMA s1 OBJECT_VISIBILITY = $$ organization_targets: [x] $$;",
            id="create_schema_object_visibility_spec",
        ),
        pytest.param(
            "ALTER SCHEMA s1 SET OBJECT_VISIBILITY = $$ organization_targets: [x] $$;",
            id="alter_schema_object_visibility_spec",
        ),
        # FEATURE POLICY is documented for ALTER DATABASE only.
        pytest.param(
            "ALTER SCHEMA s1 SET FEATURE POLICY p1;",
            id="alter_schema_set_feature_policy",
        ),
        pytest.param(
            "ALTER SCHEMA s1 UNSET FEATURE POLICY;",
            id="alter_schema_unset_feature_policy",
        ),
        # TRANSIENT is documented for database, schema and plain table clones.
        pytest.param(
            "CREATE TRANSIENT SEQUENCE x CLONE y;",
            id="transient_sequence_clone",
        ),
        pytest.param(
            "CREATE TRANSIENT STAGE x CLONE y;",
            id="transient_stage_clone",
        ),
        pytest.param(
            "CREATE TRANSIENT EVENT TABLE x CLONE y;",
            id="transient_event_table_clone",
        ),
        pytest.param(
            "CREATE TRANSIENT ALERT x CLONE y;",
            id="transient_alert_clone",
        ),
        # The IGNORE ... and INCLUDE INTERNAL STAGES clauses are documented
        # for database and schema clones only.
        pytest.param(
            "CREATE TABLE t1 CLONE t0 IGNORE HYBRID TABLES;",
            id="table_clone_ignore_hybrid_tables",
        ),
        pytest.param(
            "CREATE TABLE t1 CLONE t0 INCLUDE INTERNAL STAGES;",
            id="table_clone_include_internal_stages",
        ),
        # WITH MANAGED ACCESS is a schema clause.
        pytest.param(
            "CREATE DATABASE d1 CLONE d0 WITH MANAGED ACCESS;",
            id="database_clone_with_managed_access",
        ),
        # FROM BACKUP SET is a standalone form.
        pytest.param(
            "CREATE SCHEMA s1 FROM BACKUP SET bs IDENTIFIER 'x' CLONE s0;",
            id="schema_from_backup_set_with_clone",
        ),
        # SET FEATURE POLICY needs a policy name; UNSET takes none.
        pytest.param(
            "ALTER DATABASE d1 SET FEATURE POLICY;",
            id="alter_database_set_feature_policy_without_name",
        ),
        pytest.param(
            "ALTER DATABASE d1 UNSET FEATURE POLICY p1;",
            id="alter_database_unset_feature_policy_with_name",
        ),
        # A database role clone takes no COMMENT.
        pytest.param(
            "CREATE DATABASE ROLE r1 CLONE r0 COMMENT = 'x';",
            id="database_role_clone_with_comment",
        ),
        # DEFAULT_METADATA_WRITE_FORMAT: CREATE only, and only the two
        # documented values.
        pytest.param(
            "CREATE SCHEMA s1 DEFAULT_METADATA_WRITE_FORMAT = PARQUET;",
            id="create_schema_default_metadata_write_format_bad_value",
        ),
        pytest.param(
            "ALTER SCHEMA s1 SET DEFAULT_METADATA_WRITE_FORMAT = ICEBERG;",
            id="alter_schema_default_metadata_write_format",
        ),
        pytest.param(
            "ALTER DATABASE d1 SET DEFAULT_METADATA_WRITE_FORMAT = ICEBERG;",
            id="alter_database_default_metadata_write_format",
        ),
    ],
)
def test_snowflake_rejects_undocumented_forms(sql):
    """Statements outside the documented syntax must not parse cleanly."""
    assert _violations(sql), f"Expected a parse failure for:\n{sql}"
