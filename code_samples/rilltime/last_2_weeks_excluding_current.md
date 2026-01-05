---
title: Last 2 weeks, excluding current week
tags:
  - queries
  - rilltime
---

## USER PROMPT

Last 2 weeks, excluding current week using rilltime expression: `2W as of watermark/W`

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using rilltime expression: 2W as of watermark/W
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("advertiser_name")
    .measure("overall_spend")
    .time_range({"expression": "2W as of watermark/W"})
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
