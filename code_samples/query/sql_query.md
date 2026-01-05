---
title: Raw SQL Query
tags:
  - queries
---

## USER PROMPT

Execute a raw SQL query against a project's data sources

## CODE SAMPLE

```python
from pyrill import RillClient, SqlQuery

client = RillClient(org="my-org", project="my-project")

# Create raw SQL query
query = SqlQuery(
    sql="""
    SELECT
        COUNT(*) as total_rows,
        COUNT(DISTINCT advertiser_name) as unique_advertisers,
        MIN(__time) as earliest_date,
        MAX(__time) as latest_date
    FROM my_data_model
    """,
    connector="duckdb"
)

# Execute query
result = client.queries.sql(query)
```

## TEST OUTPUT

```python
# Print summary statistics
if result.data:
    stats = result.data[0]
    print(f"Total rows: {stats['total_rows']}")
    print(f"Unique advertisers: {stats['unique_advertisers']}")
    print(f"Date range: {stats['earliest_date']} to {stats['latest_date']}")
```

## EXPLANATORY DETAILS

Raw SQL queries allow direct access to the underlying data models and sources, bypassing the metrics layer:

**When to use SQL queries:**
- Complex analytical queries not supported by metrics queries
- Ad-hoc data exploration
- Custom aggregations and window functions
- Joining multiple data models
- Statistical analysis requiring raw data access

**SqlQuery parameters:**
- `sql` - The SQL query string (required)
- `connector` - The connector type (usually "duckdb")

**Key differences from metrics queries:**
- Query data models directly, not metrics views
- Write standard SQL (SELECT, FROM, WHERE, GROUP BY, etc.)
- No automatic aggregation - you control the SQL
- More flexible but requires SQL knowledge
- Results may not be pre-aggregated

**Use `__time` field** for time-based filtering:
```sql
WHERE __time >= '2024-01-01' AND __time < '2024-02-01'
```

The result structure is the same as metrics queries - a result object with a `data` property containing rows.
