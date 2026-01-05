---
title: Previous complete hour at watermark boundary
tags:
  - queries
  - rilltime
---

## USER PROMPT

Previous complete hour at watermark boundary using rilltime expression: `1h as of watermark/h`

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using rilltime expression: 1h as of watermark/h
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("advertiser_name")
    .measure("overall_spend")
    .time_range({"expression": "1h as of watermark/h"})
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
