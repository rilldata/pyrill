---
title: List Reports
tags:
  - reports
---

## USER PROMPT

List all scheduled reports for a project

## CODE SAMPLE

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# List all reports
reports = client.reports.list()
```

## TEST OUTPUT

```python
for report in reports:
    print(f"Report: {report.name}")

    # Report spec contains configuration
    if report.spec:
        print(f"  Display Name: {report.spec.display_name}")
        print(f"  Query: {report.spec.query_name}")
        if report.spec.export_format:
            print(f"  Format: {report.spec.export_format.value}")
        if report.spec.refresh_schedule:
            print(f"  Schedule: {report.spec.refresh_schedule.cron}")

    # Report state contains execution information
    if report.state:
        print(f"  Next Run: {report.state.next_run_on}")
        print(f"  Execution Count: {report.state.execution_count}")
```

## EXPLANATORY DETAILS

The `list()` method returns a list of `Report` models representing all scheduled reports in the project. Each report has two main components:

- **spec**: The report configuration (display name, query, schedule, export format, recipients)
- **state**: Runtime information (next run time, execution count)

Reports are scheduled exports of query results that can be delivered via email, Slack, or other notification channels. They support various export formats (CSV, XLSX, Parquet) and flexible cron schedules.

This is useful for:
- Discovering what reports are configured in a project
- Monitoring report schedules and execution status
- Building report management interfaces
- Auditing report configurations
