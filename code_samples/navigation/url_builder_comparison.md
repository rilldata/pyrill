---
title: Generate URL with Time Comparison
tags:
  - urls
---

## USER PROMPT

Create a Rill UI URL with prior period comparison enabled

## CODE SAMPLE

```python
from pyrill import UrlBuilder, QueryBuilder

# Initialize URL builder
url_builder = UrlBuilder(
    org="my-org",
    project="my-project"
)

# Create a metrics query using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name"])
    .measures(["total_spend", "impressions"])
    .time_range({"iso_duration": "P7D"})
    .sort("total_spend", desc=True)
    .build())

# Generate URL with comparison enabled
url_with_comparison = url_builder.build_url(
    query,
    enable_comparison=True
)
```

## TEST OUTPUT

```python
print(f"URL with comparison: {url_with_comparison}")
```

## EXPLANATORY DETAILS

The `enable_comparison=True` parameter adds prior period comparison to the Rill UI view:

**What it does:**
- Compares current period to previous period of same length
- Shows delta/change metrics automatically
- Highlights trends and anomalies
- Adds comparison columns to the UI

**URL parameter added:**
- `compare_tr=rill-PP` - Enables "Prior Period" comparison
  - For P7D (7 days), compares to previous 7 days
  - For P30D (30 days), compares to previous 30 days
  - Automatically calculates matching period

**Use cases:**
- Week-over-week performance tracking
- Month-over-month growth analysis
- Identifying trends and changes
- Performance reporting with context

**Comparison metrics shown:**
- Absolute change (current - previous)
- Percentage change ((current - previous) / previous * 100)
- Visual indicators (up/down arrows)

**When to use:**
- Monitoring dashboards
- Performance reports
- Trend analysis
- Anomaly detection

Comparison mode works with any time range but is most meaningful with rolling windows (iso_duration) rather than fixed date ranges.
