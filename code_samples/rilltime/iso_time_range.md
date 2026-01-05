---
title: Explicit ISO 8601 time range
tags:
  - queries
  - rilltime
---

## USER PROMPT

Explicit ISO 8601 time range using rilltime expression: `2025-02-20T01:23:45Z to 2025-07-15T02:34:50Z`

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using rilltime expression: 2025-02-20T01:23:45Z to 2025-07-15T02:34:50Z
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("advertiser_name")
    .measure("overall_spend")
    .time_range({"expression": "2025-02-20T01:23:45Z to 2025-07-15T02:34:50Z"})
    .limit(10)
    .build())

# Execute query
result = client.queries.metrics(query)
```

## TEST OUTPUT

```python
for row in result.data:
    print(row)
```
