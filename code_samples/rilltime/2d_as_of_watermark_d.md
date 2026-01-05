---
title: Last 2 days at watermark boundary
tags:
  - queries
  - rilltime
---

## USER PROMPT

Last 2 days at watermark boundary using rilltime expression: `2D as of watermark/D`

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using rilltime expression: 2D as of watermark/D
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("advertiser_name")
    .measure("overall_spend")
    .time_range({"expression": "2D as of watermark/D"})
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
