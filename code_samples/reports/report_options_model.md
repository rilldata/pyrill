---
title: Working with ReportOptions Model
tags:
  - reports
  - models
---

## USER PROMPT

Create and validate report configuration using the ReportOptions model

## CODE SAMPLE

```python
from pyrill.models.reports import ReportOptions, ExportFormat

# Create report options with all available fields
options = ReportOptions(
    display_name="Comprehensive Sales Report",
    refresh_cron="0 9 * * 1",  # Every Monday at 9 AM
    refresh_time_zone="America/New_York",
    query_name="sales_metrics",
    export_format=ExportFormat.XLSX,
    email_recipients=["team@example.com", "manager@example.com"]
)

# Create minimal options (only required fields)
minimal_options = ReportOptions(
    display_name="Basic Report",
    refresh_cron="0 9 * * 1",
    query_name="simple_query"
)

# Export format options
csv_options = ReportOptions(
    display_name="CSV Report",
    refresh_cron="0 9 * * *",
    query_name="daily_metrics",
    export_format=ExportFormat.CSV  # CSV format
)

parquet_options = ReportOptions(
    display_name="Parquet Report",
    refresh_cron="0 9 * * *",
    query_name="daily_metrics",
    export_format=ExportFormat.PARQUET  # Parquet format (data lake)
)

# Common cron schedules
daily_9am = "0 9 * * *"  # Every day at 9 AM
weekly_monday = "0 9 * * 1"  # Every Monday at 9 AM
monthly_first = "0 9 1 * *"  # First day of month at 9 AM
hourly = "0 * * * *"  # Every hour

# Timezone examples
timezones = [
    "America/New_York",     # Eastern Time
    "America/Chicago",      # Central Time
    "America/Los_Angeles",  # Pacific Time
    "Europe/London",        # GMT/BST
    "UTC"                   # Coordinated Universal Time
]
```

## TEST OUTPUT

```python
# Access fields
print(f"Display Name: {options.display_name}")
print(f"Schedule: {options.refresh_cron}")
print(f"Format: {options.export_format.value}")  # EXPORT_FORMAT_XLSX

# Serialize to dict for API requests (uses camelCase aliases)
api_data = options.model_dump(by_alias=True, exclude_none=True)
print("\nAPI-compatible data:")
print(api_data)
# Output:
# {
#   "displayName": "Comprehensive Sales Report",
#   "refreshCron": "0 9 * * 1",
#   "refreshTimeZone": "America/New_York",
#   "queryName": "sales_metrics",
#   "exportFormat": "EXPORT_FORMAT_XLSX",
#   "emailRecipients": ["team@example.com", "manager@example.com"]
# }
```

## EXPLANATORY DETAILS

The `ReportOptions` model provides a type-safe way to configure reports with validation and IDE autocomplete support.

### Available Fields

**Required fields:**
- **display_name**: Human-readable report name (shown in UI)
- **refresh_cron**: Cron expression for scheduling (e.g., "0 9 * * 1")
- **query_name**: Name of the query or metrics view to export

**Optional fields:**
- **refresh_time_zone**: Timezone for the schedule (defaults to UTC)
- **export_format**: Output format (CSV, XLSX, PARQUET)
- **email_recipients**: List of email addresses to notify

### Export Formats

The `ExportFormat` enum provides type-safe format selection:
- **ExportFormat.CSV**: Comma-separated values (universal compatibility)
- **ExportFormat.XLSX**: Excel format (best for business users)
- **ExportFormat.PARQUET**: Columnar format (efficient for data lakes)
- **ExportFormat.UNSPECIFIED**: Use default format

### Cron Schedule Syntax

Cron expressions follow standard 5-field format: `minute hour day month weekday`

Common patterns:
- `0 9 * * *` - Daily at 9:00 AM
- `0 9 * * 1` - Weekly on Mondays at 9:00 AM
- `0 9 1 * *` - Monthly on 1st day at 9:00 AM
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 1-5` - Weekdays at midnight

### Field Name Aliases

The model automatically converts between Python naming (snake_case) and API naming (camelCase):
- `display_name` → `displayName`
- `refresh_cron` → `refreshCron`
- `refresh_time_zone` → `refreshTimeZone`
- `query_name` → `queryName`
- `export_format` → `exportFormat`
- `email_recipients` → `emailRecipients`

Always use `model_dump(by_alias=True)` when sending data to the API to ensure correct field names.

### Validation

The Pydantic model automatically validates:
- Required fields are present
- Email addresses are properly formatted
- Enum values are valid
- Data types are correct

This catches configuration errors before making API calls, providing immediate feedback during development.
