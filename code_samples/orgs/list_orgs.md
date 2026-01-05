---
title: List Orgs
tags:
  - orgs
---

## USER PROMPT

List all orgs I have access to

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# List all orgs
orgs = client.orgs.list()
```

## TEST OUTPUT
```python
for org in orgs:
    print(f"Org: {org.name}")
    print(f"  Display Name: {org.display_name}")
    print()
```

**output**
```
Org: rilldata
  Display Name: Rill Data

Org: rilldata
  Display Name: Rill Data

```
## EXPLANATORY DETAILS

The `list()` method returns a list of `Org` models representing all orgs the authenticated user has access to. Each org includes metadata such as:
- `name` - The org's unique identifier
- `display_name` - The human-readable name
- Additional org metadata

This is useful for:
- Discovering which orgs you have access to
- Building org selection menus
- Iterating through orgs to perform bulk operations
