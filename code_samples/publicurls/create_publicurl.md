---
title: Create Public URL
tags:
  - publicurls
---

## USER PROMPT

Create a new public URL (magic auth token) to share an explore with external users

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Create a basic public URL for an explore
result = client.publicurls.create("my_explore")

# Create a public URL with expiration and field restrictions
result = client.publicurls.create(
    "my_explore",
    display_name="Revenue Report - Q1 2024",
    ttl_minutes=1440,  # Expires in 24 hours
    fields=["date", "revenue", "region"]  # Only these fields visible
)

# Create a public URL with a filter
result = client.publicurls.create(
    "my_explore",
    display_name="High Value Customers",
    filter={
        "field": "revenue",
        "operator": ">",
        "value": 10000
    }
)
```

## TEST OUTPUT

```python
print(f"Created public URL: {result.url}")
print(f"Token: {result.token}")
print()

print(f"Created restricted public URL: {result.url}")
print(f"Display Name: Revenue Report - Q1 2024")
print(f"Token expires in: 24 hours")
print(f"Visible fields: date, revenue, region")
print()

print(f"Created filtered public URL: {result.url}")
print(f"Filter: revenue > 10000")
```

## EXPLANATORY DETAILS

The `create()` method generates a new public URL for sharing an explore. The method returns a `CreatePublicUrlResponse` model with:
- `url` - The shareable public URL
- `token` - The token ID (also embedded in the URL)

**Parameters:**
- `resource_name` (required) - Name of the explore to share
- `display_name` - Human-readable name shown in the token list
- `ttl_minutes` - Time until expiration (e.g., 1440 = 24 hours)
- `fields` - List of field names to restrict visibility to
- `filter` - Dictionary defining a filter to pre-apply to the data
- `org` - Organization name (uses client default if not specified)
- `project` - Project name (uses client default if not specified)

**Use cases:**
- **Basic sharing**: Share full access to an explore without restrictions
- **Time-limited access**: Set `ttl_minutes` for temporary access (demos, trials)
- **Field restriction**: Use `fields` to hide sensitive columns (PII, financial details)
- **Pre-filtered views**: Apply `filter` to show subset of data (specific region, time period)

**Security considerations:**
- Public URLs grant access without authentication
- Use field restrictions to hide sensitive data
- Set expiration times for temporary access
- Monitor token usage via `used_on` field when listing tokens
