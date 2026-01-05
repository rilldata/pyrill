---
title: Month-to-date (current complete month)
tags:
  - queries
  - rilltime
---

## USER PROMPT

Month-to-date (current complete month) using rilltime expression: `MTD as of watermark/M+1M`

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using rilltime expression: MTD as of watermark/M+1M
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("advertiser_name")
    .measure("overall_spend")
    .time_range({"expression": "MTD as of watermark/M+1M"})
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
