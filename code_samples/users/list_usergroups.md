---
title: List Organization Usergroups
tags:
  - users
  - usergroups
---

## USER PROMPT

List all usergroups in my organization

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# List all usergroups (uses client default org)
groups = client.usergroups.list()
```

## TEST OUTPUT

```python
for group in groups:
    print(f"Group: {group.group_name}")
    print(f"  Role: {group.role_name}")
    print(f"  Users: {group.users_count}")
```

## EXPLANATORY DETAILS

The `list()` method returns a list of `MemberUsergroup` models representing all usergroups in the organization. Each group includes:
- `group_name` - Usergroup name
- `group_id` - Unique identifier
- `role_name` - Organization role
- `users_count` - Number of users (if include_counts=True)

The method uses the client's default org unless explicitly overridden with the `org` parameter.
