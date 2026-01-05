---
title: List Projects
tags:
  - projects
---

## USER PROMPT

List all projects I have access to across all organizations

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# List all projects
projects = client.projects.list()
```

## TEST OUTPUT

```python
for project in projects:
    print(f"Project: {project.name}")
    print(f"  Organization: {project.org_name}")
    print(f"  Public: {project.public}")
```

## EXPLANATORY DETAILS

The `list()` method returns a list of all `Project` models the authenticated user has access to, across all organizations. Each project includes:
- `name` - The project's unique identifier
- `org_name` - The organization the project belongs to
- `public` - Whether the project is publicly accessible
- Additional project metadata

This is useful for:
- Discovering available projects
- Building project selection interfaces
- Performing operations across multiple projects
