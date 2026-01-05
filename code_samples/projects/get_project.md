---
title: Get Project Details
tags:
  - projects
---

## USER PROMPT

Get details for a specific project

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get specific project
project = client.projects.get("my-project", "my-org")
```

## TEST OUTPUT

```python
print(f"Name: {project.name}")
print(f"Organization: {project.org_name}")
print(f"Public: {project.public}")
```

## EXPLANATORY DETAILS

The `get()` method retrieves detailed information about a specific project within an organization. Both the project name and organization name are required.

This is useful when you need to:
- Verify a project exists
- Get current project metadata
- Check project properties before performing queries

The method raises a `RillError` if the project doesn't exist or you don't have access to it.
