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
    ],
)
def test_snowflake_rejects_undocumented_forms(sql):
    """Statements outside the documented syntax must not parse cleanly."""
    assert _violations(sql), f"Expected a parse failure for:\n{sql}"
