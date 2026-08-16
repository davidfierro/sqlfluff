<!-- Title: Snowflake: mixed GROUPING SETS in GROUP BY, PIVOT aggregate alias, UNPIVOT IN-list aliases -->
<!-- Branch: davidfierro:snowflake-query-gaps   Base: sqlfluff/sqlfluff@main -->

### Brief summary of the change made

- GROUP BY mixing ordinary expressions with GROUPING SETS / CUBE / ROLLUP in the same list
  (`GROUP BY a, GROUPING SETS (b, ())`), by moving the CUBE / ROLLUP / GROUPING SETS
  alternatives inside the delimited list of `GroupByClauseSegment`, following the pattern
  already used in the postgres dialect. As a side effect, `ROLLUP (...)` and `CUBE (...)` now
  parse as proper grouping constructs instead of ordinary function calls, which corrects the
  parse tree labels.
- Optional alias for the aggregate in PIVOT: `PIVOT (SUM(amount) AS total FOR ...)`.
- Aliases in the UNPIVOT IN-list: `UNPIVOT (sales FOR month IN (jan AS 'JANUARY', feb))`.

Reference documentation:

- https://docs.snowflake.com/en/sql-reference/constructs/group-by
- https://docs.snowflake.com/en/sql-reference/constructs/pivot
- https://docs.snowflake.com/en/sql-reference/constructs/unpivot

### Are there any other side effects of this change that we should be aware of?

The GROUP BY restructuring changes the parse tree of existing fixtures that use
`GROUP BY ROLLUP (...)` / `CUBE (...)`: those previously parsed as function calls and now
parse as dedicated grouping clauses. The regenerated YAML diffs in this PR are exactly that
relabelling; no statement that parsed before stops parsing.

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
