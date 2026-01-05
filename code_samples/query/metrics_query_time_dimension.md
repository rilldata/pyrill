---
title: Time-Series Metrics Query
tags:
  - queries
---

## USER PROMPT

Query metrics with daily time granularity for time-series analysis

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range (last 7 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Create time-series query with daily granularity using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("timestamp_day", {
        "time_floor": {
            "dimension": "__time",
            "grain": "day"
        }
    })
    .dimension("advertiser_name")
    .measures(["total_spend", "impressions"])
    .time_range({"start": start_date, "end": end_date})
    .sort("timestamp_day", desc=False)
    .sort("total_spend", desc=True)
    .limit(100)
    .build())

# Execute query
result = client.queries.metrics(query)
```

## TEST OUTPUT

```python
for row in result.data:
    print(f"{row['timestamp_day']}: {row['advertiser_name']} - ${row['total_spend']}")
```

## EXPLANATORY DETAILS

Time-series queries use computed dimensions to aggregate data at specific time granularities. The key components are:

**DimensionCompute:**
- Defines how to compute a dimension value

**DimensionComputeTimeFloor:**
- `dimension` - Usually "__time" (the special time field)
- `grain` - Time granularity (DAY, HOUR, WEEK, MONTH, QUARTER, YEAR)

**Available TimeGrain values:**
- `TimeGrain.MILLISECOND`
- `TimeGrain.SECOND`
- `TimeGrain.MINUTE`
- `TimeGrain.HOUR`
- `TimeGrain.DAY`
- `TimeGrain.WEEK`
- `TimeGrain.MONTH`
- `TimeGrain.QUARTER`
- `TimeGrain.YEAR`

The computed dimension name (e.g., "timestamp_day") is used in the result rows and can be used for sorting.

This pattern is essential for creating time-series charts, trend analysis, and temporal comparisons.
