---
title: Generate Report YAML Definition
tags:
  - reports
  - yaml
  - infrastructure-as-code
---

## USER PROMPT

Generate a YAML definition for a report to version control in Git

## CODE SAMPLE

```python
from pyrill import RillClient
from pyrill.models.reports import ReportOptions, ExportFormat

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Configure report options
options = ReportOptions(
    display_name="Monthly Revenue Report",
    refresh_cron="0 9 1 * *",  # First day of month at 9 AM
    refresh_time_zone="America/New_York",
    query_name="revenue_metrics",
    export_format=ExportFormat.XLSX,
    email_recipients=["finance@example.com"]
)

# Generate YAML definition
yaml_content = client.reports.generate_yaml(options)

# Save to file for version control
with open("reports/monthly-revenue-report.yaml", "w") as f:
    f.write(yaml_content)
```

## TEST OUTPUT

```python
print("Report YAML generated and saved")
print("\nYAML content:")
print(yaml_content)
```

## EXPLANATORY DETAILS

The `generate_yaml()` method converts a report configuration into a YAML file that can be committed to your project's Git repository. This enables **Infrastructure as Code** for reports.

Benefits of YAML-based reports:
- **Version Control**: Track report changes over time in Git
- **Code Review**: Review report configurations in pull requests
- **Portability**: Easily move reports between environments (dev/staging/prod)
- **Collaboration**: Share and collaborate on report definitions
- **Backup**: Git serves as a backup of report configurations

The generated YAML file can be placed in your Rill project's repository (typically in a `reports/` directory) and will be automatically deployed when the project is synced.

Typical workflow:
1. Create/test reports in the UI
2. Use `generate_yaml()` to export the configuration
3. Commit the YAML file to Git
4. Deploy via Git sync

This approach allows you to:
- Create reports interactively in the UI (visual, fast feedback)
- Export to code for version control and deployment
- Maintain a single source of truth in Git
- Apply standard software development practices to BI artifacts

The YAML format follows Rill's resource specification and includes all report configuration: schedule, query, format, recipients, and notification settings.
