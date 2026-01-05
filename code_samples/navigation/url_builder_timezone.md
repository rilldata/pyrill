---
title: Generate URL with Custom Timezone
tags:
  - urls
---

## USER PROMPT

Create a Rill UI URL with a specific timezone for data display

## CODE SAMPLE

```python
from pyrill import UrlBuilder, QueryBuilder

# Initialize URL builder
url_builder = UrlBuilder(
    org="my-org",
    project="my-project"
)

# Create a metrics query with timezone using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name"])
    .measures(["total_spend"])
    .time_range({"iso_duration": "P7D"})
    .time_zone("America/New_York")  # Eastern Time
    .sort("total_spend", desc=True)
    .build())

# Generate URL (timezone from query is used)
url = url_builder.build_url(query)
```

## TEST OUTPUT

```python
print(f"URL with Eastern Time timezone: {url}")

# Or create queries for different timezones
timezones = {
    "America/New_York": "Eastern",
    "America/Los_Angeles": "Pacific",
    "Europe/London": "British",
    "Asia/Tokyo": "Japan"
}

for tz, name in timezones.items():
    query = (QueryBuilder()
        .metrics_view("my_metrics_view")
        .dimensions(["advertiser_name"])
        .measures(["total_spend"])
        .time_range({"iso_duration": "P7D"})
        .time_zone(tz)
        .sort("total_spend", desc=True)
        .build())
    url = url_builder.build_url(query)
    print(f"{name} Time: {url}")
```

## EXPLANATORY DETAILS

Timezones control how time-based data is interpreted and displayed in the Rill UI:

**Supported timezone formats:**
- IANA timezone identifiers (e.g., "America/New_York")
- Common timezones:
  - `"America/New_York"` - Eastern Time (ET)
  - `"America/Los_Angeles"` - Pacific Time (PT)
  - `"America/Chicago"` - Central Time (CT)
  - `"Europe/London"` - British Time
  - `"Europe/Paris"` - Central European Time
  - `"Asia/Tokyo"` - Japan Standard Time
  - `"UTC"` - Coordinated Universal Time

**How timezones affect queries:**
- Time range boundaries are interpreted in the specified timezone
- Time dimensions are displayed in the timezone
- Aggregations respect timezone boundaries (e.g., day boundaries)

**URL parameter:**
- `tz={timezone}` - Sets the display timezone
- URL-encodes special characters (e.g., "/" becomes "%2F")

**Use cases:**
- Multi-region analytics (view data in each region's local time)
- Consistent reporting across distributed teams
- Financial reporting in business hours timezone
- Event analysis in user's local time

**Best practices:**
- Use IANA timezone identifiers for precision
- Consider daylight saving time transitions
- Default is usually UTC if not specified
- Match timezone to your business context (headquarters, primary market, etc.)
