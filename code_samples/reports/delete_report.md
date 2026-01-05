---
title: Delete a Report
tags:
  - reports
---

## USER PROMPT

Delete a scheduled report

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Delete the report
response = client.reports.delete("old-report")
```

## TEST OUTPUT

```python
print("Report deleted successfully")
```

## EXPLANATORY DETAILS

The `delete()` method permanently removes a scheduled report from the project. This action:
- Stops all future scheduled executions
- Removes the report from the project
- Cannot be undone

The method returns a `DeleteReportResponse` to confirm the deletion.

This is useful for:
- Cleaning up obsolete or deprecated reports
- Removing test reports after validation
- Implementing report lifecycle management
- Programmatically managing report configurations

Best practices:
- Verify the report name before deletion
- Consider archiving report configurations before deleting
- Notify stakeholders before removing reports they may depend on
- Use `get()` to confirm the report exists before attempting deletion
- Document why reports are being removed for audit purposes

Note: Deleting a report does not delete the underlying query or data - only the scheduled export configuration is removed.
