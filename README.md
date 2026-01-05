# PyRill SDK

![Coverage](./coverage.svg)

**34 end-to-end query tests** passed. [View Report](tests/fixtures/query_results/README.md)

**34 end-to-end query tests** passed. [View Report](tests/fixtures/query_results/README.md)

**34 end-to-end query tests** passed. [View Report](tests/fixtures/query_results/README.md)

A lightweight Python SDK for interacting with the [Rill Data](https://rilldata.com) API.

## Features

- **Simple & Lightweight**: Minimal dependencies (httpx, pydantic, pyyaml)
- **Type-Safe**: Pydantic models for all API responses
- **Comprehensive**: Full coverage of Rill Data API
- **Well-Tested**: Extensive test suite with 100% API coverage

## Installation

### From TestPyPI (Testing)

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pyrill
```

### From Source

```bash
git clone https://github.com/rilldata/pyrill.git
cd pyrill
uv sync
```

### Prerequisites

- Python 3.9 or higher
- Rill API token from [Rill Console](https://ui.rilldata.com/)

## Quick Start

Set your API token:
```bash
export RILL_USER_TOKEN="rill_usr_..."
```

Basic usage:
```python
from pyrill import RillClient

# Initialize client (uses RILL_USER_TOKEN from environment)
client = RillClient()

# List organizations
orgs = client.organizations.list()
for org in orgs:
    print(f"{org.name} - {org.description}")

# Get a specific organization
org = client.organizations.get("my-org")

# List projects in an organization
projects = client.projects.list(org_name="my-org")
for project in projects:
    print(f"{project.name} - Public: {project.public}")

# Get project status
status = client.projects.status("my-project", "my-org")
print(f"Deployment: {status.deployment.status}")
```

## Core Resources

### Organizations

```python
# List all organizations
orgs = client.organizations.list()

# Get specific organization
org = client.organizations.get("my-org")
```

### Projects

```python
# List projects in an organization
projects = client.projects.list("my-org")

# Get specific project
project = client.projects.get("my-project", "my-org")

# Get project resources
resources = client.projects.get_resources("my-org", "my-project")

# Check deployment status
status = client.projects.status("my-project", "my-org")
```

### Queries

Execute metrics and SQL queries:

```python
# Metrics query
result = client.query.metrics(
    org_name="my-org",
    project_name="my-project",
    metrics_view_name="my_metrics",
    measures=["total_sales"],
    dimensions=["region"],
    time_dimension="timestamp"
)

# SQL query
result = client.query.sql(
    org_name="my-org",
    project_name="my-project",
    sql="SELECT * FROM my_table LIMIT 10"
)
```

### Query Builder

Fluent API for building complex queries:

```python
from pyrill import QueryBuilder

query = (
    QueryBuilder("my_metrics")
    .select_measures(["total_sales", "avg_price"])
    .select_dimensions(["region", "category"])
    .where("region", "=", "US")
    .where("total_sales", ">", 1000)
    .order_by("total_sales", "desc")
    .limit(100)
)

result = client.query.execute(query, org_name="my-org", project_name="my-project")
```

### URL Builder

Generate shareable Rill dashboard URLs:

```python
from pyrill import URLBuilder

url = (
    URLBuilder("my-org", "my-project")
    .explore("my_metrics")
    .with_measures(["total_sales"])
    .with_dimensions(["region"])
    .with_filter("region", ["US", "EU"])
    .with_time_range("2024-01-01", "2024-12-31")
    .build()
)

print(url)  # https://ui.rilldata.com/my-org/my-project/-/explore/my_metrics?...
```

## Advanced Features

### Public URLs

Create shareable public URLs for dashboards:

```python
# Create public URL
public_url = client.publicurls.create(
    org_name="my-org",
    project_name="my-project",
    resource_kind="rill.runtime.v1.Explore",
    resource_name="my_metrics"
)

# List public URLs
urls = client.publicurls.list("my-org", "my-project")

# Revoke public URL
client.publicurls.delete("my-org", "my-project", public_url.id)
```

### Reports

Generate and manage reports:

```python
# Create report
report = client.reports.create(
    org_name="my-org",
    project_name="my-project",
    query_name="my_metrics",
    export_format="csv",
    email_recipients=["user@example.com"]
)

# List reports
reports = client.reports.list("my-org", "my-project")

# Delete report
client.reports.delete("my-org", "my-project", report.id)
```

### Alerts & Annotations

```python
# List alerts
alerts = client.alerts.list("my-org", "my-project")

# List annotations
annotations = client.annotations.list("my-org", "my-project")
```

### User & Group Management

```python
# List users
users = client.users.list("my-org")

# List user groups
groups = client.usergroups.list("my-org")
```

## Configuration

### Environment Variables

- `RILL_USER_TOKEN` - Your Rill API token (required)
- `RILL_API_URL` - Custom API URL (optional, defaults to https://api.rilldata.com)

### Config File

Create `~/.pyrill/config.yaml`:

```yaml
token: rill_usr_your_token_here
api_url: https://api.rilldata.com  # optional
```

### In Code

```python
from pyrill import RillClient

# Explicit token
client = RillClient(token="rill_usr_...")

# Custom API URL
client = RillClient(api_url="https://custom.api.url")
```

## Error Handling

```python
from pyrill import RillClient
from pyrill.exceptions import RillAuthenticationError, RillAPIError

client = RillClient()

try:
    orgs = client.organizations.list()
except RillAuthenticationError:
    print("Invalid API token")
except RillAPIError as e:
    print(f"API error: {e.message}")
```

## Examples

See the [examples](examples/) and [code_samples](code_samples/) directories for more usage examples.

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## Testing

The SDK includes comprehensive tests:

```bash
# Unit tests (fast, mocked)
uv run pytest tests/client/unit/ -v

# Integration tests
uv run pytest tests/client/integration/ -v

# E2E tests (requires RILL_USER_TOKEN)
export RILL_USER_TOKEN="rill_usr_..."
uv run pytest tests/client/e2e/ --run-e2e -v
```

See [tests/README.md](tests/README.md) for complete testing documentation.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [Rill Data Website](https://rilldata.com)
- [Rill Console](https://ui.rilldata.com)
- [Rill Documentation](https://docs.rilldata.com)
- [Issue Tracker](https://github.com/rilldata/pyrill/issues)
