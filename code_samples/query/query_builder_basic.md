---
title: Query Builder - Fluent API
tags:
  - queries
---

## USER PROMPT

Use QueryBuilder's fluent API to construct metrics queries

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Build query using fluent API
query = (
    QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type"])
    .measures(["total_spend", "impressions", "clicks"])
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

`QueryBuilder` provides a fluent interface for constructing metrics queries with a more readable, chainable syntax:

**Key methods:**
- `metrics_view(name)` - Set the metrics view to query
- `dimension(name, compute=None)` - Add a single dimension
- `dimensions(names)` - Add multiple dimensions at once
- `measure(name)` - Add a single measure
- `measures(names)` - Add multiple measures at once
- `time_range(range_dict)` - Set time range (dict with start/end or iso_duration)
- `where(filter_dict)` - Add WHERE filter
- `sort(name, desc=False)` - Add a sort criterion
- `sorts(sort_list)` - Add multiple sort criteria
- `limit(n)` - Set result limit
- `build()` - Generate the final MetricsQuery object

**Benefits of QueryBuilder:**
- More concise than constructing Pydantic models
- Method chaining for readability
- Accepts both dicts and objects
- Still produces type-safe MetricsQuery objects
- IDE autocomplete for method names

**When to use:**
- Building queries programmatically
- Dynamic query construction
- When you prefer fluent syntax over object construction
