---
title: Generate Pivot Table URL
tags:
  - urls
---

## USER PROMPT

Create a URL that opens a pivot table view in the Rill UI

## CODE SAMPLE

```python
from pyrill import UrlBuilder, QueryBuilder

# Initialize URL builder
url_builder = UrlBuilder(
    org="my-org",
    project="my-project"
)

# Create a metrics query suitable for pivot view using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type"])
    .measures(["total_spend", "impressions", "clicks"])
    .time_range({"iso_duration": "P7D"})
    .build())

# Generate pivot table URL
pivot_url = url_builder.build_url(query, pivot=True)
```

## TEST OUTPUT

```python
print(f"Pivot Table URL: {pivot_url}")
```

## EXPLANATORY DETAILS

The `pivot=True` parameter generates a URL that opens the Rill UI in pivot table mode:

**Pivot mode characteristics:**
- Dimensions become row labels
- Measures become column headers
- Creates a cross-tabulated view
- Ideal for comparing multiple metrics across dimensions

**URL parameters for pivot mode:**
- `view=pivot` - Activates pivot table view
- `rows=` - Dimensions to use as row labels
- `cols=` - Measures to use as columns
- `table_mode=nest` - Nesting behavior for multi-dimension pivots

**When to use pivot URLs:**
- Creating executive dashboards
- Comparing multiple metrics side-by-side
- Analyzing data across two categorical dimensions
- Exporting to spreadsheet-style views

**Standard vs Pivot:**
- Standard: Leaderboard/list view with sortable columns
- Pivot: Cross-tab view with measures as columns

The same query can be rendered in both modes - just toggle the `pivot` parameter when building the URL.
