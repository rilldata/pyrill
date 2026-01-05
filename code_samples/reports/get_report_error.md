---
title: Handle Report Not Found Error
tags:
  - reports
  - error-handling
---

## USER PROMPT

Handle errors when getting a non-existent report

## CODE SAMPLE

```python
from pyrill import RillClient
from pyrill.exceptions import RillError

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

try:
    report = client.reports.get("nonexistent-report")
    print(f"Found report: {report.name}")
except RillError as e:
    print(f"Error: {e}")
    # Error message will contain "not found"
```

## EXPLANATORY DETAILS

When accessing a report that doesn't exist, the SDK raises a `RillError` (specifically `RillAPIError`) with a message indicating the report was not found.

This is useful for:
- Validating report names before operations
- Providing user-friendly error messages
- Implementing conditional logic based on report existence
- Building robust error handling in report management tools

Best practices:
- Always catch `RillError` or its subclasses when working with reports
- Check the error message to determine if the error is recoverable
- Consider using `list()` first to discover available reports
- Log errors for debugging and monitoring
