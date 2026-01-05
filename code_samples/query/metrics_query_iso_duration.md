---
title: Metrics Query with ISO Duration
tags:
  - queries
---

## USER PROMPT

Use ISO 8601 duration syntax for relative time ranges like "last 7 days"

## CODE SAMPLE

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using ISO 8601 duration (last 7 days) with QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type"])
    .measures(["total_spend", "impressions"])
    .time_range({"iso_duration": "P7D"})
    .sort("total_spend", desc=True)
    .limit(25)
    .build())

# Execute query
result = client.queries.metrics(query)
```

## TEST OUTPUT

```python
for row in result.data:
    print(row)
```

## EXPLANATORY DETAILS

ISO 8601 durations provide a standardized way to specify relative time ranges without calculating exact dates:

**Common ISO duration patterns:**
- `P1D` - Last 1 day
- `P7D` - Last 7 days (1 week)
- `P14D` - Last 14 days (2 weeks)
- `P30D` - Last 30 days (~1 month)
- `P90D` - Last 90 days (~3 months)
- `P1M` - Last 1 month
- `P1Y` - Last 1 year

**Format:** `P[n]Y[n]M[n]DT[n]H[n]M[n]S`
- P = Period (required)
- Y = Years
- M = Months (before T) or Minutes (after T)
- D = Days
- T = Time separator
- H = Hours
- S = Seconds

**Benefits of ISO durations:**
- No need to calculate dates in your code
- Automatically adjusts to "now" when query runs
- Timezone-independent (relative to query execution time)
- More maintainable than hardcoded dates

Use `iso_duration` parameter in `TimeRange` instead of `start`/`end` for rolling time windows.
