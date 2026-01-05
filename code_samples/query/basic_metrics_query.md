---
title: Basic Metrics Query
tags:
  - queries
---

## USER PROMPT

Query metrics with dimensions and measures for a specific time range

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range (last 3 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=3)

# Create metrics query using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type"])
    .measures(["total_spend", "impressions", "clicks"])
    .time_range({"start": start_date, "end": end_date})
    .sort("total_spend", desc=True)
    .limit(20)
    .build())

# Execute query
result = client.queries.metrics(query)
```

## TEST OUTPUT

```python
# Process results
for row in result.data:
    print(row)
```

## EXPLANATORY DETAILS

A basic metrics query consists of:

**Required:**
- `metrics_view` - The name of the metrics view to query

**Optional:**
- `dimensions` - Categorical fields to group by (e.g., advertiser, device type)
- `measures` - Numeric metrics to aggregate (e.g., spend, impressions)
- `time_range` - Filter data to a specific time window
- `sort` - Order results by dimension or measure
- `limit` - Maximum number of rows to return

The query returns a result object with a `data` property containing a list of dictionaries, where each dictionary represents a row with the requested dimensions and measures.

Time ranges can be specified as ISO 8601 datetime strings using the `start` and `end` parameters.
