---
title: Generate Rill UI URL from Query
tags:
  - urls
---

## USER PROMPT

Convert a metrics query into a shareable Rill UI URL

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
    .dimensions(["advertiser_name", "device_type"])
    .measures(["total_spend", "impressions"])
    .time_range({"iso_duration": "P7D"})
    .sort("total_spend", desc=True)
    .build())

# Generate URL
url = url_builder.build_url(query)
```

## TEST OUTPUT

```python
print(f"Rill UI URL: {url}")
print(f"Share this URL to view the data in Rill")
```

## EXPLANATORY DETAILS

The `UrlBuilder` converts metrics queries into URLs that open the Rill UI with the specified query parameters applied:

**Key features:**
- Generates fully-qualified URLs to Rill Cloud
- Encodes query parameters (dimensions, measures, time range, sort)
- Creates shareable links for data exploration
- Useful for embedding in reports or sharing with stakeholders

**URL components:**
- Base URL: `https://ui.rilldata.com`
- Organization and project path
- Query parameters encoded in URL

**Generated URL format:**
```
https://ui.rilldata.com/{org}/{project}/explore/{metrics_view}?
  tr={time_range}&
  measures={measure1},{measure2}&
  dims={dim1},{dim2}&
  sort_by={field}&
  sort_dir={asc|desc}
```

**Limitations:**
- WHERE filters cannot be encoded in URLs (API limitation)
- Complex queries may generate very long URLs
- Some query features may not have URL equivalents

**Use cases:**
- Generate links for email reports
- Create bookmarks for common queries
- Share specific data views with team members
- Embed in documentation or dashboards
