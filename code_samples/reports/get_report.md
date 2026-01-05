---
title: Get Report Details
tags:
  - reports
---

## USER PROMPT

Get details for a specific report by name

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Get specific report
report = client.reports.get("weekly-summary")
```

## TEST OUTPUT

```python
print(f"Name: {report.name}")

if report.spec:
    print(f"Display Name: {report.spec.display_name}")
    print(f"Query: {report.spec.query_name}")
    print(f"Export Format: {report.spec.export_format.value}")

    if report.spec.refresh_schedule:
        print(f"Cron Schedule: {report.spec.refresh_schedule.cron}")
        print(f"Timezone: {report.spec.refresh_schedule.time_zone}")

if report.state:
    print(f"Next Run: {report.state.next_run_on}")
    print(f"Total Executions: {report.state.execution_count}")
```

## EXPLANATORY DETAILS

The `get()` method retrieves detailed information about a specific report by its name. This is useful when you need to:
- Verify a report's configuration
- Check when a report will run next
- Monitor a report's execution history
- Get report details before editing

The method raises a `RillAPIError` if the report doesn't exist.

Note that the report name is different from the display name:
- **name**: The unique identifier used in API calls (e.g., "weekly-summary")
- **display_name**: The human-readable name shown in the UI (e.g., "Weekly Summary Report")
