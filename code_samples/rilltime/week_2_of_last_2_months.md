---
title: Week 2 of last 2 months
tags:
  - queries
  - rilltime
---

## USER PROMPT

Week 2 of last 2 months using rilltime expression: `W2 as of -2M/M as of watermark/M`

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using rilltime expression: W2 as of -2M/M as of watermark/M
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("advertiser_name")
    .measure("overall_spend")
    .time_range({"expression": "W2 as of -2M/M as of watermark/M"})
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
