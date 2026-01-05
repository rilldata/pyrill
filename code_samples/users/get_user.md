---
title: Get User Details
tags:
  - users
---

## USER PROMPT

Get details for a specific user by email address

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get specific user by email (uses client default org)
user = client.users.get("user@example.com")
```

## TEST OUTPUT

```python
print(f"User: {user.user_name}")
print(f"Email: {user.user_email}")
print(f"Role: {user.role_name}")
```

## EXPLANATORY DETAILS

The `get()` method returns a single `OrganizationMemberUser` for the specified email address. The method:
- Accepts email as required parameter (positional or named)
- Uses client's default org unless explicitly overridden
- Raises `RillAPIError` if user is not found
- Also available as `show()` for compatibility
