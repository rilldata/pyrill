---
title: Get Current User Info
tags:
  - auth
---

## USER PROMPT

Get information about the currently authenticated user

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get current user information
user = client.auth.whoami()
```

## TEST OUTPUT

```python
print(f"User ID: {user.id}")
print(f"Email: {user.email}")
print(f"Display Name: {user.display_name}")
```

## EXPLANATORY DETAILS

The `whoami()` method returns a `User` model with information about the currently authenticated user. This is useful for:
- Verifying authentication is working correctly
- Getting the current user's ID for API calls
- Displaying user information in your application

The returned `User` model includes fields such as `id`, `email`, `name`, and `display_name`.
