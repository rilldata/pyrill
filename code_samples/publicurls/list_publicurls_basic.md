---
title: List Public URLs (Basic)
tags:
  - publicurls
---

## USER PROMPT

List all public URLs (magic auth tokens) for a project

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# List all public URLs for the project
tokens = client.publicurls.list()
```

## TEST OUTPUT

```python
for token in tokens:
    print(f"Token ID: {token.id}")
    print(f"  URL: {token.url}")
    print(f"  Display Name: {token.display_name}")
    print(f"  Created: {token.created_on}")
    if token.expires_on:
        print(f"  Expires: {token.expires_on}")
    print(f"  Resources: {len(token.resources)}")
    if token.resources:
        for resource in token.resources:
            print(f"    - {resource.type}: {resource.name}")
    if token.fields:
        print(f"  Field Restrictions: {', '.join(token.fields)}")
    print()
```

## EXPLANATORY DETAILS

The `list()` method returns all public URLs (magic auth tokens) for the project. Each `MagicAuthToken` model includes:
- `id` - The token's unique identifier
- `url` - The shareable public URL
- `display_name` - Optional human-readable name
- `created_on` - When the token was created
- `expires_on` - Optional expiration timestamp
- `resources` - List of resources (explores, dashboards) the token grants access to
- `fields` - Optional list of restricted fields/columns
- `used_on` - Timestamp of last use (if ever used)

Public URLs are useful for:
- Sharing dashboards with external users without requiring Rill accounts
- Creating time-limited access links
- Embedding dashboards in external applications
- Controlling which data fields are visible to recipients
