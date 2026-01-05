---
title: Get Usergroup Details
tags:
  - users
  - usergroups
---

## USER PROMPT

Get details for a specific usergroup by name

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get specific usergroup by name (uses client default org)
group = client.usergroups.get("engineering")
```

## TEST OUTPUT

```python
print(f"Group: {group.group_name}")
print(f"Role: {group.role_name}")
print(f"Managed: {group.group_managed}")
```

## EXPLANATORY DETAILS

The `get()` method returns a single `Usergroup` with full details for the specified group name. The method:
- Accepts usergroup name as required parameter (positional or named)
- Uses client's default org unless explicitly overridden
- Raises `RillAPIError` if usergroup is not found
- Returns more detailed information than the list endpoint
- Also available as `show()` for compatibility
