---
title: Get Project Resources
tags:
  - projects
---

## USER PROMPT

List all runtime resources in a project

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get project resources
resources = client.projects.get_resources("my-org", "my-project")
```

## TEST OUTPUT

```python
print(f"Found {len(resources.resources)} resources")

for resource in resources.resources:
    print(f"Resource: {resource.name} (Type: {resource.kind})")
```

## EXPLANATORY DETAILS

The `get_resources()` method returns a `ProjectResources` object containing all runtime resources defined in a project. Resources can include:
- Sources (data connections)
- Models (data transformations)
- Metrics views (aggregated datasets)
- Dashboards
- Reports

Each resource has:
- `name` - The resource identifier
- `kind` - The resource type (Source, Model, MetricsView, etc.)
- Additional resource-specific metadata

This is useful for:
- Discovering available data sources and metrics
- Building dynamic interfaces based on project resources
- Validating resource existence before querying
