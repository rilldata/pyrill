---
title: Client Connection
tags:
  - client
---

## USER PROMPT

Initialize a Rill client for my organization and project

## CODE SAMPLE

```python
from pyrill import RillClient

# Initialize client with organization and project
client = RillClient(org="my-org", project="my-project")
```

## TEST OUTPUT

```python
# Alternative: Initialize with explicit API token
client = RillClient(
    api_token="rill_usr_...",
    org="my-org",
    project="my-project"
)
```

## EXPLANATORY DETAILS

The `RillClient` is the main entry point for interacting with the Rill API. It can be initialized in two ways:

1. **Using environment variable** (recommended): Set `RILL_USER_TOKEN` environment variable and initialize with just `org` and `project`
2. **Explicit token**: Pass the `api_token` parameter directly

The client provides access to all Rill resources through its properties:
- `client.auth` - Authentication operations (whoami, list tokens)
- `client.organizations` - Organization operations (list, get)
- `client.projects` - Project operations (list, get, get resources, status)
- `client.queries` - Query operations (metrics, SQL, metrics SQL)
