---
title: Week 1 when boundary is on Thursday
tags:
  - queries
  - rilltime
---

## USER PROMPT

Week 1 when boundary is on Thursday using rilltime expression: `W1 as of 2025-05-01T00:00:00Z`

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using rilltime expression: W1 as of 2025-05-01T00:00:00Z
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("advertiser_name")
    .measure("overall_spend")
    .time_range({"expression": "W1 as of 2025-05-01T00:00:00Z"})
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
