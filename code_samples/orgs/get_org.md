---
title: Get Org Details
tags:
  - orgs
---

## USER PROMPT

Get details for a specific org by name

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get specific org
org = client.orgs.get("my-org")
```

## TEST OUTPUT

```python
print(f"Name: {org.name}")
print(f"Display Name: {org.display_name}")
```

**Output:** 
```
Name: rilldata
Display Name: Rill Data
```

## EXPLANATORY DETAILS

The `get()` method retrieves detailed information about a specific org by its name. This is useful when you need to:
- Verify an org exists
- Get current metadata for an org
- Check org properties before performing operations

The method raises a `RillError` if the org doesn't exist or you don't have access to it.
