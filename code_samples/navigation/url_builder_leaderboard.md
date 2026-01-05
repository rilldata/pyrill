---
title: Generate URL with Leaderboard Configuration
tags:
  - urls
---

## USER PROMPT

Create a Rill UI URL with specific leaderboard measure display options

## CODE SAMPLE

```python
from pyrill import UrlBuilder, QueryBuilder

# Initialize URL builder
url_builder = UrlBuilder(
    org="my-org",
    project="my-project"
)

# Create a query with multiple measures using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name"])
    .measures(["total_spend", "impressions", "clicks", "ctr"])
    .time_range({"iso_duration": "P7D"})
    .sort("total_spend", desc=True)
    .build())

# Generate URL with all measures in leaderboard
url_multi = url_builder.build_url(
    query,
    multi_leaderboard_measures=True
)

# Generate URL with only first measure in leaderboard
url_single = url_builder.build_url(
    query,
    multi_leaderboard_measures=False
)
```

## TEST OUTPUT

```python
print(f"All measures in leaderboard: {url_multi}")
print(f"Only first measure in leaderboard: {url_single}")
```

## EXPLANATORY DETAILS

The `multi_leaderboard_measures` parameter controls which measures appear in the Rill UI's leaderboard visualization:

**multi_leaderboard_measures=True:**
- All measures from the query appear in the leaderboard
- Users can see multiple metrics at once
- Creates a more comprehensive view
- URL parameter: `leaderboard_measures=measure1,measure2,measure3,...`

**multi_leaderboard_measures=False:**
- Only the first measure appears in the leaderboard
- Cleaner, focused view on primary metric
- Other measures still available but not in leaderboard
- URL parameter: `leaderboard_measures=measure1`

**What is a leaderboard?**
- Visual ranking of dimension values by measure
- Shows top performers (or bottom performers)
- Typically displayed as horizontal bars or sorted list
- Common in explore/analytics views

**Use cases for multi-measure leaderboards:**
- Executive dashboards comparing multiple KPIs
- Performance analysis across different metrics
- Comprehensive reporting views

**Use cases for single-measure leaderboards:**
- Focused analysis on primary metric
- Cleaner presentations
- When screen space is limited
- When comparing different dimensions (not measures)

**Default behavior:**
- If not specified, Rill may use default leaderboard configuration
- First measure in query is typically the default focus

Choose based on whether your audience needs to see multiple metrics simultaneously or focus on a single key metric.
