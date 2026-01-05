# PyRill SDK - All Code Examples

This file contains all code samples from the PyRill SDK, organized by resource type for easy navigation.

---

## Client

#### Client Connection

##### User Prompt

Initialize a Rill client for my organization and project

##### Code Sample

```python
from pyrill import RillClient

# Initialize client with organization and project
client = RillClient(org="my-org", project="my-project")
```

##### Test Output

```python
# Alternative: Initialize with explicit API token
client = RillClient(
    api_token="rill_usr_...",
    org="my-org",
    project="my-project"
)
```

---

## Auth

#### Get Current User Info

##### User Prompt

Get information about the currently authenticated user

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get current user information
user = client.auth.whoami()
```

##### Test Output

```python
print(f"User ID: {user.id}")
print(f"Email: {user.email}")
print(f"Display Name: {user.display_name}")
```

---

## Projects

#### Get Project Details

##### User Prompt

Get details for a specific project

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get specific project
project = client.projects.get("my-project", "my-org")
```

##### Test Output

```python
print(f"Name: {project.name}")
print(f"Organization: {project.org_name}")
print(f"Public: {project.public}")
```

---

#### Get Project Resources

##### User Prompt

List all runtime resources in a project

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get project resources
resources = client.projects.get_resources("my-org", "my-project")
```

##### Test Output

```python
print(f"Found {len(resources.resources)} resources")

for resource in resources.resources:
    print(f"Resource: {resource.name} (Type: {resource.kind})")
```

---

#### Get Project Status

##### User Prompt

Check the deployment status of a project

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get project status
status = client.projects.status("my-project", "my-org")
```

##### Test Output

```python
print(f"Project: {status.project.name}")
print(f"Organization: {status.project.org}")
print(f"Deployment Status: {status.deployment.status}")
```

---

#### List Projects

##### User Prompt

List all projects I have access to across all organizations

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# List all projects
projects = client.projects.list()
```

##### Test Output

```python
for project in projects:
    print(f"Project: {project.name}")
    print(f"  Organization: {project.org_name}")
    print(f"  Public: {project.public}")
```

---

## Queries

#### Basic Metrics Query

##### User Prompt

Query metrics with dimensions and measures for a specific time range

##### Code Sample

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range (last 3 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=3)

# Create metrics query using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type"])
    .measures(["total_spend", "impressions", "clicks"])
    .time_range({"start": start_date, "end": end_date})
    .sort("total_spend", desc=True)
    .limit(20)
    .build())

# Execute query
result = client.queries.metrics(query)
```

##### Test Output

```python
# Process results
for row in result.data:
    print(row)
```

---

#### Metrics Query with Complex Filter

##### User Prompt

Use AND/OR logic to create complex filters in metrics queries

##### Code Sample

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range
end_date = datetime.now()
start_date = end_date - timedelta(days=4)

# Create query with complex AND filter using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type", "device_region"])
    .measures(["total_spend", "impressions", "clicks"])
    .where({
        "op": "and",
        "conditions": [
            {"op": "eq", "field": "device_type", "value": "mobile"},
            {"op": "in", "field": "device_region", "values": ["US", "GB", "CA"]}
        ]
    })
    .time_range({"start": start_date, "end": end_date})
    .sort("total_spend", desc=True)
    .limit(50)
    .build())

# Execute query
result = client.queries.metrics(query)
```

##### Test Output

```python
print(f"Mobile campaigns in US/GB/CA: {len(result.data)} results")
for row in result.data:
    print(row)
```

---

#### Metrics Query with Dict

##### User Prompt

Query metrics using a plain Python dictionary instead of Pydantic models

##### Code Sample

```python
from pyrill import RillClient
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range
end_date = datetime.now()
start_date = end_date - timedelta(days=3)

# Create query as plain dict
query_dict = {
    "metrics_view": "my_metrics_view",
    "dimensions": [
        {"name": "advertiser_name"},
        {"name": "device_type"}
    ],
    "measures": [
        {"name": "total_spend"},
        {"name": "impressions"}
    ],
    "time_range": {
        "start": start_date.isoformat(),
        "end": end_date.isoformat()
    },
    "sort": [{"name": "total_spend", "desc": True}],
    "limit": 20
}

# Execute query with dict
result = client.queries.metrics(query_dict)
```

##### Test Output

```python
for row in result.data:
    print(row)
```

---

#### Metrics Query with ISO Duration

##### User Prompt

Use ISO 8601 duration syntax for relative time ranges like "last 7 days"

##### Code Sample

```python
from pyrill import RillClient, QueryBuilder

client = RillClient(org="my-org", project="my-project")

# Query using ISO 8601 duration (last 7 days) with QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type"])
    .measures(["total_spend", "impressions"])
    .time_range({"iso_duration": "P7D"})
    .sort("total_spend", desc=True)
    .limit(25)
    .build())

# Execute query
result = client.queries.metrics(query)
```

##### Test Output

```python
for row in result.data:
    print(row)
```

---

#### Time-Series Metrics Query

##### User Prompt

Query metrics with daily time granularity for time-series analysis

##### Code Sample

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range (last 7 days)
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Create time-series query with daily granularity using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimension("timestamp_day", {
        "time_floor": {
            "dimension": "__time",
            "grain": "day"
        }
    })
    .dimension("advertiser_name")
    .measures(["total_spend", "impressions"])
    .time_range({"start": start_date, "end": end_date})
    .sort("timestamp_day", desc=False)
    .sort("total_spend", desc=True)
    .limit(100)
    .build())

# Execute query
result = client.queries.metrics(query)
```

##### Test Output

```python
for row in result.data:
    print(f"{row['timestamp_day']}: {row['advertiser_name']} - ${row['total_spend']}")
```

---

#### Metrics Query with Filter

##### User Prompt

Filter metrics query results using WHERE conditions

##### Code Sample

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range
end_date = datetime.now()
start_date = end_date - timedelta(days=5)

# Create query with filter using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "campaign_name"])
    .measures(["total_spend", "clicks", "ctr"])
    .where({"op": "eq", "field": "device_type", "value": "mobile"})
    .time_range({"start": start_date, "end": end_date})
    .sort("total_spend", desc=True)
    .limit(30)
    .build())

# Execute query
result = client.queries.metrics(query)
```

##### Test Output

```python
print(f"Found {len(result.data)} mobile campaigns")
for row in result.data:
    print(row)
```

---

#### Metrics SQL Query

##### User Prompt

Query pre-aggregated metrics views using SQL syntax

##### Code Sample

```python
from pyrill import RillClient, MetricsSqlQuery

client = RillClient(org="my-org", project="my-project")

# Create metrics SQL query
query = MetricsSqlQuery(
    sql="""
    SELECT
        advertiser_name,
        device_type,
        total_spend,
        impressions,
        clicks
    FROM my_metrics_view
    ORDER BY total_spend DESC
    LIMIT 20
    """
)

# Execute query
result = client.queries.metrics_sql(query)
```

##### Test Output

```python
for row in result.data:
    print(f"{row['advertiser_name']}: ${row['total_spend']:.2f}")
```

---

#### Query Builder - Fluent API

##### User Prompt

Use QueryBuilder's fluent API to construct metrics queries

##### Code Sample

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

# Build query using fluent API
query = (
    QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type"])
    .measures(["total_spend", "impressions", "clicks"])
    .time_range({
        "start": start_date,
        "end": end_date
    })
    .sort("total_spend", desc=True)
    .limit(50)
    .build()
)

# Execute query
result = client.queries.metrics(query)
```

##### Test Output

```python
for row in result.data:
    print(row)
```

---

#### Query Builder with Filters

##### User Prompt

Use QueryBuilder to create queries with filters using simplified dict syntax

##### Code Sample

```python
from pyrill import RillClient, QueryBuilder
from datetime import datetime, timedelta

client = RillClient(org="my-org", project="my-project")

# Define time range
end_date = datetime.now()
start_date = end_date - timedelta(days=4)

# Build query with complex filter using dict syntax
query = (
    QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type", "device_region"])
    .measures(["total_spend", "impressions", "clicks"])
    .where({
        "op": "and",
        "conditions": [
            {"op": "eq", "field": "device_type", "value": "mobile"},
            {"op": "in", "field": "device_region", "values": ["US", "GB", "CA"]}
        ]
    })
    .time_range({
        "start": start_date,
        "end": end_date
    })
    .sort("total_spend", desc=True)
    .limit(50)
    .build()
)

# Execute query
result = client.queries.metrics(query)
```

##### Test Output

```python
for row in result.data:
    print(row)
```

---

#### Raw SQL Query

##### User Prompt

Execute a raw SQL query against a project's data sources

##### Code Sample

```python
from pyrill import RillClient, SqlQuery

client = RillClient(org="my-org", project="my-project")

# Create raw SQL query
query = SqlQuery(
    sql="""
    SELECT
        COUNT(*) as total_rows,
        COUNT(DISTINCT advertiser_name) as unique_advertisers,
        MIN(__time) as earliest_date,
        MAX(__time) as latest_date
    FROM my_data_model
    """,
    connector="duckdb"
)

# Execute query
result = client.queries.sql(query)
```

##### Test Output

```python
# Print summary statistics
if result.data:
    stats = result.data[0]
    print(f"Total rows: {stats['total_rows']}")
    print(f"Unique advertisers: {stats['unique_advertisers']}")
    print(f"Date range: {stats['earliest_date']} to {stats['latest_date']}")
```

---

## Urls

#### Generate Rill UI URL from Query

##### User Prompt

Convert a metrics query into a shareable Rill UI URL

##### Code Sample

```python
from pyrill import UrlBuilder, QueryBuilder

# Initialize URL builder
url_builder = UrlBuilder(
    org="my-org",
    project="my-project"
)

# Create a metrics query using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type"])
    .measures(["total_spend", "impressions"])
    .time_range({"iso_duration": "P7D"})
    .sort("total_spend", desc=True)
    .build())

# Generate URL
url = url_builder.build_url(query)
```

##### Test Output

```python
print(f"Rill UI URL: {url}")
print(f"Share this URL to view the data in Rill")
```

---

#### Generate URL with Time Comparison

##### User Prompt

Create a Rill UI URL with prior period comparison enabled

##### Code Sample

```python
from pyrill import UrlBuilder, QueryBuilder

# Initialize URL builder
url_builder = UrlBuilder(
    org="my-org",
    project="my-project"
)

# Create a metrics query using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name"])
    .measures(["total_spend", "impressions"])
    .time_range({"iso_duration": "P7D"})
    .sort("total_spend", desc=True)
    .build())

# Generate URL with comparison enabled
url_with_comparison = url_builder.build_url(
    query,
    enable_comparison=True
)
```

##### Test Output

```python
print(f"URL with comparison: {url_with_comparison}")
```

---

#### Generate URL with Leaderboard Configuration

##### User Prompt

Create a Rill UI URL with specific leaderboard measure display options

##### Code Sample

```python
from pyrill import UrlBuilder, QueryBuilder

# Initialize URL builder
url_builder = UrlBuilder(
    org="my-org",
    project="my-project"
)

# Create a query with multiple measures using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name"])
    .measures(["total_spend", "impressions", "clicks", "ctr"])
    .time_range({"iso_duration": "P7D"})
    .sort("total_spend", desc=True)
    .build())

# Generate URL with all measures in leaderboard
url_multi = url_builder.build_url(
    query,
    multi_leaderboard_measures=True
)

# Generate URL with only first measure in leaderboard
url_single = url_builder.build_url(
    query,
    multi_leaderboard_measures=False
)
```

##### Test Output

```python
print(f"All measures in leaderboard: {url_multi}")
print(f"Only first measure in leaderboard: {url_single}")
```

---

#### Generate Pivot Table URL

##### User Prompt

Create a URL that opens a pivot table view in the Rill UI

##### Code Sample

```python
from pyrill import UrlBuilder, QueryBuilder

# Initialize URL builder
url_builder = UrlBuilder(
    org="my-org",
    project="my-project"
)

# Create a metrics query suitable for pivot view using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name", "device_type"])
    .measures(["total_spend", "impressions", "clicks"])
    .time_range({"iso_duration": "P7D"})
    .build())

# Generate pivot table URL
pivot_url = url_builder.build_url(query, pivot=True)
```

##### Test Output

```python
print(f"Pivot Table URL: {pivot_url}")
```

---

#### Generate URL with Custom Timezone

##### User Prompt

Create a Rill UI URL with a specific timezone for data display

##### Code Sample

```python
from pyrill import UrlBuilder, QueryBuilder

# Initialize URL builder
url_builder = UrlBuilder(
    org="my-org",
    project="my-project"
)

# Create a metrics query with timezone using QueryBuilder
query = (QueryBuilder()
    .metrics_view("my_metrics_view")
    .dimensions(["advertiser_name"])
    .measures(["total_spend"])
    .time_range({"iso_duration": "P7D"})
    .time_zone("America/New_York")  # Eastern Time
    .sort("total_spend", desc=True)
    .build())

# Generate URL (timezone from query is used)
url = url_builder.build_url(query)
```

##### Test Output

```python
print(f"URL with Eastern Time timezone: {url}")

# Or create queries for different timezones
timezones = {
    "America/New_York": "Eastern",
    "America/Los_Angeles": "Pacific",
    "Europe/London": "British",
    "Asia/Tokyo": "Japan"
}

for tz, name in timezones.items():
    query = (QueryBuilder()
        .metrics_view("my_metrics_view")
        .dimensions(["advertiser_name"])
        .measures(["total_spend"])
        .time_range({"iso_duration": "P7D"})
        .time_zone(tz)
        .sort("total_spend", desc=True)
        .build())
    url = url_builder.build_url(query)
    print(f"{name} Time: {url}")
```

---

## Publicurls

#### Create Public URL

##### User Prompt

Create a new public URL (magic auth token) to share an explore with external users

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Create a basic public URL for an explore
result = client.publicurls.create("my_explore")

# Create a public URL with expiration and field restrictions
result = client.publicurls.create(
    "my_explore",
    display_name="Revenue Report - Q1 2024",
    ttl_minutes=1440,  # Expires in 24 hours
    fields=["date", "revenue", "region"]  # Only these fields visible
)

# Create a public URL with a filter
result = client.publicurls.create(
    "my_explore",
    display_name="High Value Customers",
    filter={
        "field": "revenue",
        "operator": ">",
        "value": 10000
    }
)
```

##### Test Output

```python
print(f"Created public URL: {result.url}")
print(f"Token: {result.token}")
print()

print(f"Created restricted public URL: {result.url}")
print(f"Display Name: Revenue Report - Q1 2024")
print(f"Token expires in: 24 hours")
print(f"Visible fields: date, revenue, region")
print()

print(f"Created filtered public URL: {result.url}")
print(f"Filter: revenue > 10000")
```

---

#### List Public URLs (Basic)

##### User Prompt

List all public URLs (magic auth tokens) for a project

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# List all public URLs for the project
tokens = client.publicurls.list()
```

##### Test Output

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

---

#### List Public URLs with Pagination

##### User Prompt

List public URLs with custom page size for better control over large result sets

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# List public URLs with custom page size
tokens = client.publicurls.list(page_size=5)
```

##### Test Output

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

---

## Partitions

#### List Model Partitions - Basic

##### User Prompt

List partitions for a partitioned model to inspect execution state and watermarks

##### Code Sample

```python
from pyrill import RillClient

# Initialize client with defaults
client = RillClient(org="my-org", project="my-project")

# List partitions for a model (uses client defaults)
partitions = client.partitions.list("sales_model")
```

##### Test Output

```python
# Display partition information
for partition in partitions:
    status = "✓" if partition.error is None else "✗"
    print(f"{status} {partition.key}")
    if partition.watermark:
        print(f"  Watermark: {partition.watermark}")
    if partition.executed_on:
        print(f"  Executed: {partition.executed_on}")
    if partition.error:
        print(f"  Error: {partition.error}")
    if partition.elapsed_ms:
        print(f"  Duration: {partition.elapsed_ms}ms")
```

---

#### List Model Partitions - Filtering

##### User Prompt

Filter partitions to find pending or errored partitions for troubleshooting

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get only errored partitions for debugging
errored_partitions = client.partitions.list(
    "sales_model",
    errored=True
)

# Get pending partitions waiting to execute
pending_partitions = client.partitions.list(
    "sales_model",
    pending=True
)

# Override project to check a different environment
staging_errors = client.partitions.list(
    "sales_model",
    project="staging",
    errored=True
)
```

##### Test Output

```python
print(f"Found {len(errored_partitions)} errored partitions:")
for partition in errored_partitions:
    print(f"\n❌ Partition: {partition.key}")
    print(f"   Error: {partition.error}")
    if partition.executed_on:
        print(f"   Failed at: {partition.executed_on}")

print(f"\n⏳ {len(pending_partitions)} partitions pending execution")

print(f"\n🔧 Staging has {len(staging_errors)} errored partitions")
```

---

#### List Model Partitions - Pagination

##### User Prompt

Retrieve large numbers of partitions using automatic pagination

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get up to 400 partitions with automatic pagination
# The SDK handles pagination transparently via nextPageToken
all_partitions = client.partitions.list(
    "large_model",
    limit=400
)

# Without limit, returns first page only (default 50)
first_page = client.partitions.list("large_model")

# Custom page size for API efficiency
# SDK makes multiple requests of 25 each until limit reached
partitions = client.partitions.list(
    "large_model",
    limit=100,
    page_size=25  # 4 API calls
)
```

##### Test Output

```python
print(f"Retrieved {len(all_partitions)} partitions")

# Analyze partition health
total = len(all_partitions)
errored = sum(1 for p in all_partitions if p.error)
success = total - errored

print(f"\nPartition Health:")
print(f"  ✓ Successful: {success} ({success/total*100:.1f}%)")
print(f"  ✗ Errored: {errored} ({errored/total*100:.1f}%)")

print(f"\nFirst page: {len(first_page)} partitions")

# Calculate average execution time
executed = [p for p in partitions if p.elapsed_ms]
if executed:
    avg_time = sum(p.elapsed_ms for p in executed) / len(executed)
    print(f"\nAverage execution time: {avg_time:.0f}ms")
```

---

## Reports

#### Create a New Report

##### User Prompt

Create a new scheduled report with email delivery

##### Code Sample

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

##### Test Output

```python
print(f"Created report: {response.name}")
```

---

#### Delete a Report

##### User Prompt

Delete a scheduled report

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Delete the report
response = client.reports.delete("old-report")
```

##### Test Output

```python
print("Report deleted successfully")
```

---

#### Edit an Existing Report

##### User Prompt

Update a report's schedule and recipients

##### Code Sample

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

##### Test Output

```python
print(f"Updated report configuration")
```

---

#### Generate Report YAML Definition

##### User Prompt

Generate a YAML definition for a report to version control in Git

##### Code Sample

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

##### Test Output

```python
print("Report YAML generated and saved")
print("\nYAML content:")
print(yaml_content)
```

---

#### Get Report Details

##### User Prompt

Get details for a specific report by name

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Get specific report
report = client.reports.get("weekly-summary")
```

##### Test Output

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

---

#### Handle Report Not Found Error

##### User Prompt

Handle errors when getting a non-existent report

##### Code Sample

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

---

#### List Reports

##### User Prompt

List all scheduled reports for a project

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# List all reports
reports = client.reports.list()
```

##### Test Output

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

---

#### Working with ReportOptions Model

##### User Prompt

Create and validate report configuration using the ReportOptions model

##### Code Sample

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

##### Test Output

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

---

#### Trigger Report Execution

##### User Prompt

Manually trigger a report to run immediately

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Trigger an ad-hoc execution
response = client.reports.trigger("weekly-summary")
```

##### Test Output

```python
print("Report triggered successfully")
print("The report will execute outside its normal schedule")
```

---

#### Unsubscribe from Report

##### User Prompt

Remove the current user from a report's recipient list

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="demo", project="rill-openrtb-prog-ads")

# Unsubscribe from the report
response = client.reports.unsubscribe("daily-metrics")
```

##### Test Output

```python
print("Successfully unsubscribed from report")
print("You will no longer receive this report")
```

---

## Orgs

#### Get Org Details

##### User Prompt

Get details for a specific org by name

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get specific org
org = client.orgs.get("my-org")
```

##### Test Output

```python
print(f"Name: {org.name}")
print(f"Display Name: {org.display_name}")
```

---

#### List Orgs

##### User Prompt

List all orgs I have access to

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# List all orgs
orgs = client.orgs.list()
```

---

## Users

#### Get User Details

##### User Prompt

Get details for a specific user by email address

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get specific user by email (uses client default org)
user = client.users.get("user@example.com")
```

##### Test Output

```python
print(f"User: {user.user_name}")
print(f"Email: {user.user_email}")
print(f"Role: {user.role_name}")
```

---

#### Get Usergroup Details

##### User Prompt

Get details for a specific usergroup by name

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# Get specific usergroup by name (uses client default org)
group = client.usergroups.get("engineering")
```

##### Test Output

```python
print(f"Group: {group.group_name}")
print(f"Role: {group.role_name}")
print(f"Managed: {group.group_managed}")
```

---

#### List Organization Usergroups

##### User Prompt

List all usergroups in my organization

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# List all usergroups (uses client default org)
groups = client.usergroups.list()
```

##### Test Output

```python
for group in groups:
    print(f"Group: {group.group_name}")
    print(f"  Role: {group.role_name}")
    print(f"  Users: {group.users_count}")
```

---

#### List Organization Users

##### User Prompt

List all users in my organization

##### Code Sample

```python
from pyrill import RillClient

client = RillClient(org="my-org", project="my-project")

# List all users (uses client default org)
users = client.users.list()
```

##### Test Output

```python
for user in users:
    print(f"User: {user.user_email}")
    print(f"  Role: {user.role_name}")
    print(f"  Projects: {user.projects_count}")
```

---

## Rill Time

Rill Time expressions provide powerful time-based filtering for queries. Below are examples of supported time expressions:

**Previous complete hour at watermark boundary:**
`1h as of watermark/h`

**Last 2 days at watermark boundary:**
`2D as of watermark/D`

**Last 2 Complete Days Relative to Latest Data Boundary:**
`-2D to ref as of latest/D`

**Day 2 of last 2 weeks:**
`D2 as of -2W/W as of watermark/W`

**First 2 hours of last 2 days:**
`-2D/D to -2D/D+2h as of watermark/D`

**Single ISO date (full day):**
`2025-02-20`

**Single ISO month:**
`2025-02`

**Explicit ISO 8601 time range:**
`2025-02-20T01:23:45Z to 2025-07-15T02:34:50Z`

**Single ISO year:**
`2025`

**Last 2 days, excluding current day:**
`2D as of watermark/D`

**Last 2 minutes of last 2 days:**
`-2D/D-2m to -2D/D as of watermark/D`

**Last 2 weeks, excluding current week:**
`2W as of watermark/W`

**Month-to-date (current complete month):**
`MTD as of watermark/M+1M`

**Previous complete day:**
`1D as of watermark/D`

**Previous complete month:**
`1M as of watermark/M`

**Previous complete quarter:**
`1Q as of watermark/Q`

**Week 1 of current period:**
`W1`

**Week 1 of 2 months ago:**
`W1 as of -2M`

**Week 2 of previous month at latest boundary:**
`W2 as of -1M as of latest/M`

**Week 2 of last 2 months:**
`W2 as of -2M/M as of watermark/M`

**Week 1 when boundary is on Monday:**
`W1 as of 2024-07-01T00:00:00Z`

**Week 1 when boundary is on Thursday:**
`W1 as of 2025-05-01T00:00:00Z`

