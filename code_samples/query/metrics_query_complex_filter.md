---
title: Metrics Query with Complex Filter
tags:
  - queries
---

## USER PROMPT

Use AND/OR logic to create complex filters in metrics queries

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range
end_date = datetime.now()
start_date = end_date - timedelta(days=4)

# Create query with complex AND filter using QueryBuilder
query = (QueryBuilder()
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
    .time_range({"start": start_date, "end": end_date})
    .sort("total_spend", desc=True)
    .limit(50)
    .build())

# Execute query
result = client.queries.metrics(query)
```

## TEST OUTPUT

```python
print(f"Mobile campaigns in US/GB/CA: {len(result.data)} results")
for row in result.data:
    print(row)
```

## EXPLANATORY DETAILS

Complex filters combine multiple conditions using logical operators:

**AND operator:**
```python
Expression(
    cond=Condition(
        op=Operator.AND,
        exprs=[condition1, condition2, ...]
    )
)
```

**OR operator:**
```python
Expression(
    cond=Condition(
        op=Operator.OR,
        exprs=[condition1, condition2, ...]
    )
)
```

**IN operator for multiple values:**
```python
Expression(
    cond=Condition(
        op=Operator.IN,
        exprs=[
            Expression(name="field_name"),
            Expression(val=["value1", "value2", "value3"])
        ]
    )
)
```

Complex filters can be nested to create sophisticated query logic:
- (A AND B) OR (C AND D)
- (A OR B) AND (C OR D)
- Multiple levels of nesting

This enables precise data filtering for analytical queries without post-processing results.
