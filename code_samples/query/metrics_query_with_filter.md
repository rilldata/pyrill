---
title: Metrics Query with Filter
tags:
  - queries
---

## USER PROMPT

Filter metrics query results using WHERE conditions

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range
end_date = datetime.now()
start_date = end_date - timedelta(days=5)

# Create query with filter using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "campaign_name"])
    .measures(["total_spend", "clicks", "ctr"])
    .where({"op": "eq", "field": "device_type", "value": "mobile"})
    .time_range({"start": start_date, "end": end_date})
    .sort("total_spend", desc=True)
    .limit(30)
    .build())

# Execute query
result = client.queries.metrics(query)
```

## TEST OUTPUT

```python
print(f"Found {len(result.data)} mobile campaigns")
for row in result.data:
    print(row)
```

## EXPLANATORY DETAILS

Filters in metrics queries use an expression-based syntax:

**Expression:**
- Can represent a field name (`Expression(name="device_type")`)
- Can represent a value (`Expression(val="mobile")`)
- Can represent a condition (`Expression(cond=Condition(...))`)

**Condition:**
- `op` - Operator (EQ, NE, IN, NOT_IN, LIKE, GT, GTE, LT, LTE)
- `exprs` - List of expressions to evaluate with the operator

**Common operators:**
- `Operator.EQ` - Equal to
- `Operator.IN` - In a list of values
- `Operator.GT` - Greater than
- `Operator.LT` - Less than
- `Operator.AND` - Logical AND
- `Operator.OR` - Logical OR

The filter is applied before aggregation, allowing you to query specific subsets of your data.
