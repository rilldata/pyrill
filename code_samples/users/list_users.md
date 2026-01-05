---
title: List Organization Users
tags:
  - users
---

## USER PROMPT

List all users in my organization

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# List all users (uses client default org)
users = client.users.list()
```

## TEST OUTPUT

```python
for user in users:
    print(f"User: {user.user_email}")
    print(f"  Role: {user.role_name}")
    print(f"  Projects: {user.projects_count}")
```

## EXPLANATORY DETAILS

The `list()` method returns a list of `OrganizationMemberUser` models representing all members in the organization. Each user includes:
- `user_email` - User's email address
- `user_name` - Display name
- `role_name` - Organization role
- `projects_count` - Number of projects (if include_counts=True)
- `usergroups_count` - Number of usergroups (if include_counts=True)

The method uses the client's default org unless explicitly overridden with the `org` parameter.
