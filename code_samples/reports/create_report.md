---
title: Create a New Report
tags:
  - reports
---

## USER PROMPT

Create a new scheduled report with email delivery

## CODE SAMPLE

```python
from pyrill import RillClient
from pyrill.models.reports import ReportOptions, ExportFormat

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Configure report options
options = ReportOptions(
    display_name="Weekly Sales Report",
    refresh_cron="0 9 * * 1",  # Every Monday at 9 AM
    refresh_time_zone="America/New_York",
    query_name="sales_metrics",
    export_format=ExportFormat.XLSX,
    email_recipients=["team@example.com", "manager@example.com"]
)

# Create the report
response = client.reports.create(options)
```

## TEST OUTPUT

```python
print(f"Created report: {response.name}")
```

## EXPLANATORY DETAILS

The `create()` method creates a new scheduled report with the specified configuration. The `ReportOptions` model allows you to configure:

- **display_name**: Human-readable name shown in the UI
- **refresh_cron**: Cron expression defining the schedule (e.g., "0 9 * * 1" for Mondays at 9 AM)
- **refresh_time_zone**: Timezone for the schedule (e.g., "America/New_York")
- **query_name**: Name of the query or metrics view to export
- **export_format**: Output format (CSV, XLSX, or PARQUET)
- **email_recipients**: List of email addresses to receive the report

The method returns a `CreateReportResponse` containing the generated report name, which is typically derived from the display name but made URL-safe (e.g., "Weekly Sales Report" becomes "weekly-sales-report").

This is useful for:
- Automating report creation across multiple projects
- Programmatically setting up standard reports
- Migrating report configurations between environments
- Creating reports based on templates
