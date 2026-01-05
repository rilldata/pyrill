---
title: Edit an Existing Report
tags:
  - reports
---

## USER PROMPT

Update a report's schedule and recipients

## CODE SAMPLE

```python
from pyrill import RillClient
from pyrill.models.reports import ReportOptions

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Update report configuration
options = ReportOptions(
    display_name="Daily Sales Report",  # Updated name
    refresh_cron="0 10 * * *",  # Changed from 9 AM to 10 AM daily
    refresh_time_zone="America/Los_Angeles",  # Changed timezone
    email_recipients=["new-team@example.com"]  # Updated recipients
)

# Edit the existing report
response = client.reports.edit("weekly-sales-report", options)
```

## TEST OUTPUT

```python
print(f"Updated report configuration")
```

## EXPLANATORY DETAILS

The `edit()` method updates an existing report's configuration. You can modify any aspect of the report including:
- Schedule timing (cron expression and timezone)
- Display name
- Email recipients
- Query or export format

Important notes:
- You must provide the report's current name (not the display name)
- All fields in `ReportOptions` will update the report - use `exclude_none=True` in model dumps to preserve unspecified fields
- The report's execution history is preserved

This is useful for:
- Adjusting report schedules based on business needs
- Updating recipient lists as teams change
- Modifying report names or formats
- Fine-tuning report configurations after initial creation

Common use cases:
- Changing daily reports to weekly
- Updating timezones for distributed teams
- Adding or removing recipients
- Switching between CSV and XLSX formats
