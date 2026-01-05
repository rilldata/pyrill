---
title: Day 2 of last 2 weeks
tags:
  - queries
  - rilltime
---

## USER PROMPT

Day 2 of last 2 weeks using rilltime expression: `D2 as of -2W/W as of watermark/W`

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using rilltime expression: D2 as of -2W/W as of watermark/W
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("advertiser_name")
    .measure("overall_spend")
    .time_range({"expression": "D2 as of -2W/W as of watermark/W"})
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
