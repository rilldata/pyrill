"""
End-to-end tests for QueryResource dict-based queries against real Rill API

These tests verify that passing plain Python dicts works identically to
using Pydantic model objects. They require RILL_USER_TOKEN environment variable.

Run with: pytest tests/client/e2e/test_query_dict_e2e.py --run-e2e -v -s
"""

import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from pyrill import RillClient


# Test configuration
TEST_ORG = "demo"
TEST_PROJECT = "rill-openrtb-prog-ads"
TEST_METRICS_VIEW = "bids_metrics"

# Output directory for test results
OUTPUT_DIR = Path(__file__).parent.parent.parent / "fixtures" / "query_results" / "dict"


@pytest.fixture(scope="module")
def real_client():
    """Create a real RillClient using RILL_USER_TOKEN from environment"""
    token = os.environ.get("RILL_USER_TOKEN")
    if not token:
        pytest.skip("RILL_USER_TOKEN not set")

    client = RillClient(
        api_token=token,
        org=TEST_ORG,
        project=TEST_PROJECT
    )
    return client


@pytest.fixture(scope="module")
def output_dir():
    """Create output directory for test results"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR


def save_result(output_dir: Path, test_name: str, query: dict, result: dict, metadata: dict = None, subfolder: str = None):
    """Save query and result to JSON file"""
    output = {
        "test_name": test_name,
        "org": TEST_ORG,
        "project": TEST_PROJECT,
        "query": query,
        "result": result,
        "metadata": metadata or {}
    }

    # Create subfolder path if specified
    if subfolder:
        target_dir = output_dir / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        target_dir = output_dir

    filename = f"{test_name}.json"
    filepath = target_dir / filename

    with open(filepath, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n✓ Saved result to: {filepath}")
    print(f"  - Rows returned: {len(result.get('data', []))}")
    if result.get('data'):
        print(f"  - Sample row: {json.dumps(result['data'][0], default=str)}")
    return filepath


def save_error(output_dir: Path, test_name: str, query: dict, error: Exception, metadata: dict = None, subfolder: str = None):
    """Save query and error details to JSON file"""
    from pyrill.exceptions import RillAPIError

    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    # Extract additional details for RillAPIError
    if isinstance(error, RillAPIError):
        error_data["status_code"] = getattr(error, "status_code", None)
        error_data["response_body"] = getattr(error, "response_body", None)

    output = {
        "test_name": test_name,
        "org": TEST_ORG,
        "project": TEST_PROJECT,
        "query": query,
        "error": error_data,
        "metadata": metadata or {},
        "success": False
    }

    # Create subfolder path if specified
    if subfolder:
        target_dir = output_dir / subfolder
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        target_dir = output_dir

    filename = f"{test_name}_ERROR.json"
    filepath = target_dir / filename

    with open(filepath, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n✗ Saved error to: {filepath}")
    print(f"  - Error type: {error_data['error_type']}")
    print(f"  - Status code: {error_data.get('status_code', 'N/A')}")
    print(f"  - Message: {error_data['error_message']}")
    return filepath


@pytest.mark.e2e
class TestMetricsQueryDictE2E:
    """E2E tests for metrics queries using plain Python dicts"""

    def test_basic_metrics_query_dict(self, real_client, output_dir):
        """Test basic metrics query using a plain Python dict"""
        # Query last 3 days of data
        end_date = (datetime.now(timezone.utc) - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (end_date - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)

        # Plain dict - no Pydantic models!
        query_dict = {
            "metrics_view": TEST_METRICS_VIEW,
            "dimensions": [
                {"name": "advertiser_name"},
                {"name": "device_type"}
            ],
            "measures": [
                {"name": "overall_spend"},
                {"name": "total_bids"},
                {"name": "impressions"},
                {"name": "win_rate"}
            ],
            "time_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "sort": [{"name": "overall_spend", "desc": True}],
            "limit": 20
        }

        # Pass dict directly to metrics()
        result = real_client.queries.metrics(query_dict)

        # Save results
        save_result(
            output_dir,
            "basic_metrics_query_dict",
            query_dict,
            {"data": result.data},
            {
                "description": "Basic metrics query using plain Python dict",
                "time_range": f"{start_date.date()} to {end_date.date()}"
            },
            subfolder="metrics"
        )

        assert result is not None
        assert isinstance(result.data, list)
        print(f"\n✓ Retrieved {len(result.data)} rows using dict query")

    def test_complex_metrics_query_dict(self, real_client, output_dir):
        """Test complex metrics query with time_floor and filters using dict"""
        end_date = (datetime.now(timezone.utc) - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (end_date - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)

        # Complex dict with nested structures
        query_dict = {
            "metrics_view": TEST_METRICS_VIEW,
            "dimensions": [
                {
                    "name": "timestamp_day",
                    "compute": {
                        "time_floor": {
                            "dimension": "__time",
                            "grain": "day"
                        }
                    }
                },
                {"name": "advertiser_name"}
            ],
            "measures": [
                {"name": "overall_spend"},
                {"name": "total_bids"},
                {"name": "win_rate"}
            ],
            "where": {
                "cond": {
                    "op": "eq",
                    "exprs": [
                        {"name": "device_type"},
                        {"val": "Mobile/Tablet"}
                    ]
                }
            },
            "time_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "sort": [
                {"name": "timestamp_day", "desc": False},
                {"name": "overall_spend", "desc": True}
            ],
            "limit": 50
        }

        result = real_client.queries.metrics(query_dict)

        save_result(
            output_dir,
            "complex_metrics_query_dict",
            query_dict,
            {"data": result.data},
            {
                "description": "Complex query with time_floor and filters using dict",
                "time_range": f"{start_date.date()} to {end_date.date()}"
            },
            subfolder="metrics"
        )

        assert result is not None
        print(f"\n✓ Retrieved {len(result.data)} rows using complex dict query")

    def test_metrics_query_complex_and_filter_dict(self, real_client, output_dir):
        """Test metrics query with complex AND filter using dict"""
        end_date = (datetime.now(timezone.utc) - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (end_date - timedelta(days=4)).replace(hour=0, minute=0, second=0, microsecond=0)

        query_dict = {
            "metrics_view": TEST_METRICS_VIEW,
            "dimensions": [
                {"name": "advertiser_name"},
                {"name": "device_type"},
                {"name": "device_region"}
            ],
            "measures": [
                {"name": "overall_spend"},
                {"name": "total_bids"},
                {"name": "impressions"}
            ],
            "where": {
                "cond": {
                    "op": "and",
                    "exprs": [
                        {
                            "cond": {
                                "op": "eq",
                                "exprs": [
                                    {"name": "device_type"},
                                    {"val": "Mobile/Tablet"}
                                ]
                            }
                        },
                        {
                            "cond": {
                                "op": "in",
                                "exprs": [
                                    {"name": "device_region"},
                                    {"val": ["US", "GB", "CA"]}
                                ]
                            }
                        }
                    ]
                }
            },
            "time_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "sort": [{"name": "overall_spend", "desc": True}],
            "limit": 30
        }

        result = real_client.queries.metrics(query_dict)

        save_result(
            output_dir,
            "metrics_query_complex_and_filter_dict",
            query_dict,
            {"data": result.data},
            {
                "description": "Complex AND filter using dict",
                "filter": "device_type = 'Mobile/Tablet' AND device_region IN ('US', 'GB', 'CA')"
            },
            subfolder="metrics"
        )

        assert result is not None
        print(f"\n✓ Retrieved {len(result.data)} rows using complex AND filter dict")


@pytest.mark.e2e
class TestMetricsSqlQueryDictE2E:
    """E2E tests for metrics SQL queries using plain Python dicts"""

    def test_metrics_sql_query_dict(self, real_client, output_dir):
        """Test metrics SQL query using a plain Python dict"""
        from pyrill.exceptions import RillAPIError

        query_dict = {
            "sql": """
            SELECT
                advertiser_name,
                device_type,
                overall_spend,
                total_bids
            FROM bids_metrics
            ORDER BY overall_spend DESC
            LIMIT 20
            """
        }

        try:
            result = real_client.queries.metrics_sql(query_dict)

            save_result(
                output_dir,
                "metrics_sql_query_dict",
                query_dict,
                {"data": result.data},
                {
                    "description": "Metrics SQL query using plain Python dict - queries pre-aggregated metrics view",
                    "note": "Metrics-SQL queries the metrics view directly (no GROUP BY/aggregations needed)"
                },
                subfolder="metrics_sql"
            )

            assert result is not None
            print(f"\n✓ Retrieved {len(result.data)} rows using metrics SQL dict")
        except RillAPIError as e:
            # Save error details for diagnosis
            save_error(
                output_dir,
                "metrics_sql_query_dict",
                query_dict,
                e,
                {
                    "description": "Metrics SQL query using plain Python dict (FAILED)",
                    "note": "This endpoint may not be available for all projects"
                },
                subfolder="metrics_sql"
            )
            # Re-raise to mark test as failed
            raise


@pytest.mark.e2e
class TestSqlQueryDictE2E:
    """E2E tests for raw SQL queries using plain Python dicts"""

    def test_sql_query_dict(self, real_client, output_dir):
        """Test raw SQL query using a plain Python dict"""
        query_dict = {
            "sql": """
            SELECT
                COUNT(*) as total_rows,
                COUNT(DISTINCT advertiser_name) as unique_advertisers,
                COUNT(DISTINCT campaign_name) as unique_campaigns,
                COUNT(DISTINCT device_type) as unique_device_types,
                MIN(__time) as earliest_date,
                MAX(__time) as latest_date
            FROM bids_data_model
            """,
            "connector": "duckdb"
        }

        result = real_client.queries.sql(query_dict)

        save_result(
            output_dir,
            "sql_query_dict",
            query_dict,
            {"data": result.data},
            {
                "description": "Raw SQL query using plain Python dict"
            },
            subfolder="sql"
        )

        assert result is not None
        print(f"\n✓ Retrieved {len(result.data)} rows using raw SQL dict")
        if result.data:
            print(f"  Dataset stats: {json.dumps(result.data[0], indent=2, default=str)}")


@pytest.mark.e2e
class TestDictValidationE2E:
    """E2E tests for dict validation"""

    def test_invalid_metrics_query_dict(self, real_client):
        """Test that invalid dicts raise appropriate validation errors"""
        from pyrill.exceptions import RillAPIError

        # Missing required field (metrics_view)
        invalid_dict = {
            "dimensions": [{"name": "advertiser_name"}],
            "measures": [{"name": "overall_spend"}]
        }

        with pytest.raises(RillAPIError) as exc_info:
            real_client.queries.metrics(invalid_dict)

        assert "Invalid metrics query" in str(exc_info.value)
        print("\n✓ Invalid dict correctly raised validation error")

    def test_invalid_sql_query_dict(self, real_client):
        """Test that invalid SQL dicts raise appropriate validation errors"""
        from pyrill.exceptions import RillAPIError

        # Missing required field (sql)
        invalid_dict = {
            "connector": "duckdb"
        }

        with pytest.raises(RillAPIError) as exc_info:
            real_client.queries.sql(invalid_dict)

        assert "Invalid SQL query" in str(exc_info.value)
        print("\n✓ Invalid SQL dict correctly raised validation error")
