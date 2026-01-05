---
title: Previous complete quarter
tags:
  - queries
  - rilltime
---

## USER PROMPT

Previous complete quarter using rilltime expression: `1Q as of watermark/Q`

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using rilltime expression: 1Q as of watermark/Q
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("advertiser_name")
    .measure("overall_spend")
    .time_range({"expression": "1Q as of watermark/Q"})
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
