---
title: List Public URLs with Pagination
tags:
  - publicurls
---

## USER PROMPT

List public URLs with custom page size for better control over large result sets

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# List public URLs with custom page size
tokens = client.publicurls.list(page_size=5)
```

## TEST OUTPUT

```python
print(f"Retrieved {len(tokens)} public URLs")
print()

for token in tokens:
    print(f"Token: {token.id}")
    print(f"  URL: {token.url}")
    if token.display_name:
        print(f"  Name: {token.display_name}")

    # Show resource details
    if token.resources:
        resource = token.resources[0]
        print(f"  Resource: {resource.name} ({resource.type})")

    # Show security settings
    if token.fields:
        print(f"  Restricted Fields: {len(token.fields)} field(s)")
    if token.expires_on:
        print(f"  Expires: {token.expires_on}")
    print()
```

## EXPLANATORY DETAILS

The `list()` method supports pagination parameters for managing large result sets:
- `page_size` - Number of tokens to return per page (useful for limiting results)
- `page_token` - Token for fetching the next page (returned from previous response)

Pagination is useful when:
- Working with projects that have many public URLs
- Building UIs that display results incrementally
- Reducing initial load time by fetching smaller batches
- Implementing infinite scroll or "load more" patterns

The API returns tokens in reverse chronological order (newest first), making `page_size` useful for getting just the most recent tokens.
