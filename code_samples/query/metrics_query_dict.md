---
title: Metrics Query with Dict
tags:
  - queries
---

## USER PROMPT

Query metrics using a plain Python dictionary instead of Pydantic models

## CODE SAMPLE

```python
from pyrill import RillClient
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range
end_date = datetime.now()
start_date = end_date - timedelta(days=3)

# Create query as plain dict
query_dict = {
    "metrics_view": "my_metrics_view",
    "dimensions": [
        {"name": "advertiser_name"},
        {"name": "device_type"}
    ],
    "measures": [
        {"name": "total_spend"},
        {"name": "impressions"}
    ],
    "time_range": {
        "start": start_date.isoformat(),
        "end": end_date.isoformat()
    },
    "sort": [{"name": "total_spend", "desc": True}],
    "limit": 20
}

# Execute query with dict
result = client.queries.metrics(query_dict)
```

## TEST OUTPUT

```python
for row in result.data:
    print(row)
```

## EXPLANATORY DETAILS

The SDK supports both Pydantic models and plain Python dictionaries for query construction. Using dictionaries can be more convenient when:
- Building queries dynamically from JSON/YAML configs
- Working in notebooks or scripts without IDE autocomplete
- Migrating from other SDKs or REST API calls

The SDK will validate the dictionary structure and raise clear errors if required fields are missing or types are incorrect. The returned result is still a Pydantic model for type safety.
