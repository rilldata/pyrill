---
title: Query Builder with Filters
tags:
  - queries
---

## USER PROMPT

Use QueryBuilder to create queries with filters using simplified dict syntax

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range
end_date = datetime.now()
start_date = end_date - timedelta(days=4)

# Build query with complex filter using dict syntax
query = (
    QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type", "device_region"])
    .measures(["total_spend", "impressions", "clicks"])
    .where({
        "op": "and",
        "conditions": [
            {"op": "eq", "field": "device_type", "value": "mobile"},
            {"op": "in", "field": "device_region", "values": ["US", "GB", "CA"]}
        ]
    })
    .time_range({
        "start": start_date,
        "end": end_date
    })
    .sort("total_spend", desc=True)
    .limit(50)
    .build()
)

# Execute query
result = client.queries.metrics(query)
```

## TEST OUTPUT

```python
for row in result.data:
    print(row)
```

## EXPLANATORY DETAILS

QueryBuilder's `where()` method accepts a simplified dictionary format for filters, making complex conditions easier to write:

**Simple equality:**
```python
.where({"op": "eq", "field": "device_type", "value": "mobile"})
```

**IN operator:**
```python
.where({"op": "in", "field": "region", "values": ["US", "GB", "CA"]})
```

**AND conditions:**
```python
.where({
    "op": "and",
    "conditions": [
        {"op": "eq", "field": "field1", "value": "value1"},
        {"op": "in", "field": "field2", "values": ["a", "b", "c"]}
    ]
})
```

**OR conditions:**
```python
.where({
    "op": "or",
    "conditions": [
        {"op": "eq", "field": "field1", "value": "value1"},
        {"op": "eq", "field": "field2", "value": "value2"}
    ]
})
```

The QueryBuilder automatically converts this simplified dict syntax into the proper Expression/Condition structure required by the API, reducing boilerplate and improving readability.
