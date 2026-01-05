---
title: Week 2 of previous month at latest boundary
tags:
  - queries
  - rilltime
---

## USER PROMPT

Week 2 of previous month at latest boundary using rilltime expression: `W2 as of -1M as of latest/M`

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using rilltime expression: W2 as of -1M as of latest/M
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("advertiser_name")
    .measure("overall_spend")
    .time_range({"expression": "W2 as of -1M as of latest/M"})
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
