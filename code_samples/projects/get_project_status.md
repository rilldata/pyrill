---
title: Get Project Status
tags:
  - projects
---

## USER PROMPT

Check the deployment status of a project

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get project status
status = client.projects.status("my-project", "my-org")
```

## TEST OUTPUT

```python
print(f"Project: {status.project.name}")
print(f"Organization: {status.project.org}")
print(f"Deployment Status: {status.deployment.status}")
```

## EXPLANATORY DETAILS

The `status()` method returns a `ProjectStatus` object containing information about the project and its current deployment state. This includes:

**Project information:**
- `name` - Project identifier
- `org` - Organization identifier
- Additional project metadata

**Deployment information:**
- `status` - Current deployment state
- Deployment configuration
- Runtime information

This is useful for:
- Verifying a project is deployed and running
- Checking deployment health before querying
- Monitoring project state
- Troubleshooting deployment issues
