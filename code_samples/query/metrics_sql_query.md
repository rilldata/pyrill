---
title: Metrics SQL Query
tags:
  - queries
---

## USER PROMPT

Query pre-aggregated metrics views using SQL syntax

## CODE SAMPLE

```python
from pyrill import RillClient, MetricsSqlQuery

client = RillClient(org="my-org", project="my-project")

# Create metrics SQL query
query = MetricsSqlQuery(
    sql="""
    SELECT
        advertiser_name,
        device_type,
        total_spend,
        impressions,
        clicks
    FROM my_metrics_view
    ORDER BY total_spend DESC
    LIMIT 20
    """
)

# Execute query
result = client.queries.metrics_sql(query)
```

## TEST OUTPUT

```python
for row in result.data:
    print(f"{row['advertiser_name']}: ${row['total_spend']:.2f}")
```

## EXPLANATORY DETAILS

Metrics SQL queries combine SQL syntax with pre-aggregated metrics views:

**Key characteristics:**
- Query metrics views (not raw data models)
- Data is already aggregated - no GROUP BY needed
- Simpler than raw SQL for common analytics
- Faster than raw queries (pre-computed aggregations)
- Still allows SQL flexibility (WHERE, ORDER BY, LIMIT, etc.)

**Differences from raw SQL queries:**
- Use `MetricsSqlQuery` instead of `SqlQuery`
- Query metrics views (e.g., "my_metrics_view")
- No `connector` parameter needed
- Data is pre-aggregated at the metrics layer

**Differences from metrics queries:**
- Use SQL syntax instead of query objects
- More flexible for complex SELECT statements
- Can use SQL functions and expressions
- Useful when you know SQL but prefer not to construct query objects

**When to use:**
- You prefer SQL syntax
- You need SQL expressions or functions
- The metrics view has the data you need
- You don't need complex filters (use metrics queries for that)

Note: Not all projects may have metrics SQL enabled - check with your Rill administrator if you encounter errors.
