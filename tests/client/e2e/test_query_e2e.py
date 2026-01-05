"""
End-to-end tests for QueryResource against real Rill API

These tests require RILL_USER_TOKEN environment variable and make real API calls.
Run with: pytest tests/client/e2e/test_query_e2e.py --run-e2e -v -s
"""

import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from pyrill import (
    RillClient,
    QueryBuilder,
    MetricsQuery,
    MetricsSqlQuery,
    SqlQuery,
    Dimension,
    Measure,
    TimeRange,
    Sort,
    Expression,
    Condition,
    Operator,
    TimeGrain,
    DimensionCompute,
    DimensionComputeTimeFloor,
)


# Test configuration
TEST_ORG = "demo"
TEST_PROJECT = "rill-openrtb-prog-ads"
TEST_METRICS_VIEW = "bids_metrics"

# Output directory for test results
OUTPUT_DIR = Path(__file__).parent.parent.parent / "fixtures" / "query_results" / "object"


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
class TestMetricsQueryE2E:
    """E2E tests for metrics queries"""

    def test_basic_metrics_query(self, real_client, output_dir):
        """Test basic metrics query with dimensions and measures"""
        # Query last 3 days of data
        end_date = (datetime.now(timezone.utc) - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (end_date - timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)

        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            dimensions=[
                Dimension(name="advertiser_name"),
                Dimension(name="device_type")
            ],
            measures=[
                Measure(name="overall_spend"),
                Measure(name="total_bids"),
                Measure(name="impressions"),
                Measure(name="win_rate")
            ],
            time_range=TimeRange(
                start=start_date.isoformat(),
                end=end_date.isoformat()
            ),
            sort=[Sort(name="overall_spend", desc=True)],
            limit=20
        )

        result = real_client.queries.metrics(query)

        # Save results
        save_result(
            output_dir,
            "basic_metrics_query",
            query.model_dump(),
            {"data": result.data},
            {
                "description": "Basic metrics query with advertiser and device dimensions",
                "time_range": f"{start_date.date()} to {end_date.date()}"
            },
            subfolder="metrics"
        )

        assert result is not None
        assert isinstance(result.data, list)
        print(f"\n✓ Retrieved {len(result.data)} rows")

    def test_metrics_query_with_time_dimension(self, real_client, output_dir):
        """Test metrics query with time-based dimension"""
        # Query last 7 days with daily granularity
        end_date = (datetime.now(timezone.utc) - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (end_date - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)

        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            dimensions=[
                Dimension(
                    name="timestamp_day",
                    compute=DimensionCompute(
                        time_floor=DimensionComputeTimeFloor(
                            dimension="__time",
                            grain=TimeGrain.DAY
                        )
                    )
                ),
                Dimension(name="advertiser_name")
            ],
            measures=[
                Measure(name="overall_spend"),
                Measure(name="total_bids"),
                Measure(name="win_rate")
            ],
            time_range=TimeRange(
                start=start_date.isoformat(),
                end=end_date.isoformat()
            ),
            sort=[
                Sort(name="timestamp_day", desc=False),
                Sort(name="overall_spend", desc=True)
            ],
            limit=100
        )

        result = real_client.queries.metrics(query)

        save_result(
            output_dir,
            "metrics_query_time_dimension",
            query.model_dump(),
            {"data": result.data},
            {
                "description": "Time-series query with daily granularity by advertiser",
                "time_range": f"{start_date.date()} to {end_date.date()}"
            },
            subfolder="metrics"
        )

        assert result is not None
        print(f"\n✓ Retrieved {len(result.data)} time-series rows")

    def test_metrics_query_with_filter(self, real_client, output_dir):
        """Test metrics query with WHERE filter"""
        end_date = (datetime.now(timezone.utc) - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (end_date - timedelta(days=5)).replace(hour=0, minute=0, second=0, microsecond=0)

        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            dimensions=[
                Dimension(name="advertiser_name"),
                Dimension(name="campaign_name")
            ],
            measures=[
                Measure(name="overall_spend"),
                Measure(name="total_bids"),
                Measure(name="clicks"),
                Measure(name="ctr")
            ],
            where=Expression(
                cond=Condition(
                    op=Operator.EQ,
                    exprs=[
                        Expression(name="device_type"),
                        Expression(val="mobile")
                    ]
                )
            ),
            time_range=TimeRange(
                start=start_date.isoformat(),
                end=end_date.isoformat()
            ),
            sort=[Sort(name="overall_spend", desc=True)],
            limit=30
        )

        result = real_client.queries.metrics(query)

        save_result(
            output_dir,
            "metrics_query_with_filter",
            query.model_dump(),
            {"data": result.data},
            {
                "description": "Mobile device campaigns sorted by spend",
                "filter": "device_type = 'mobile'",
                "time_range": f"{start_date.date()} to {end_date.date()}"
            },
            subfolder="metrics"
        )

        assert result is not None
        print(f"\n✓ Retrieved {len(result.data)} filtered rows (mobile only)")

    def test_metrics_query_with_iso_duration_time_range(self, real_client, output_dir):
        """Test metrics query with ISO 8601 duration using iso_duration parameter"""
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            dimensions=[
                Dimension(name="advertiser_name"),
                Dimension(name="device_type"),
                Dimension(name="creative_type")
            ],
            measures=[
                Measure(name="overall_spend"),
                Measure(name="impressions"),
                Measure(name="video_completes"),
                Measure(name="video_completion_rate")
            ],
            time_range=TimeRange(iso_duration="P7D"),
            sort=[Sort(name="video_completes", desc=True)],
            limit=25
        )

        result = real_client.queries.metrics(query)

        save_result(
            output_dir,
            "metrics_query_iso_duration_time_range",
            query.model_dump(),
            {"data": result.data},
            {
                "description": "Video performance metrics over last 7 days using iso_duration parameter",
                "time_range": "iso_duration='P7D'"
            },
            subfolder="metrics"
        )

        assert result is not None
        print(f"\n✓ Retrieved {len(result.data)} rows (iso_duration='P7D')")

    def test_metrics_query_with_expression_time_range(self, real_client, output_dir):
        """Test metrics query with time range using expression parameter"""
        from pyrill.exceptions import RillAPIError

        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            dimensions=[
                Dimension(name="advertiser_name"),
                Dimension(name="device_type"),
                Dimension(name="creative_type")
            ],
            measures=[
                Measure(name="overall_spend"),
                Measure(name="impressions"),
                Measure(name="video_completes"),
                Measure(name="video_completion_rate")
            ],
            time_range=TimeRange(expression="P7D"),
            sort=[Sort(name="video_completes", desc=True)],
            limit=25
        )

        try:
            result = real_client.queries.metrics(query)

            save_result(
                output_dir,
                "metrics_query_expression_time_range",
                query.model_dump(),
                {"data": result.data},
                {
                    "description": "Video performance metrics using expression parameter",
                    "time_range": "expression='P7D'"
                },
                subfolder="metrics"
            )

            assert result is not None
            print(f"\n✓ Retrieved {len(result.data)} rows (expression='P7D')")
        except RillAPIError as e:
            # Save error details for diagnosis
            save_error(
                output_dir,
                "metrics_query_expression_time_range",
                query.model_dump(),
                e,
                {
                    "description": "Video performance metrics using expression parameter (FAILED)",
                    "time_range": "expression='P7D'",
                    "note": "Testing if expression parameter works differently than iso_duration"
                },
                subfolder="metrics"
            )
            # Re-raise to mark test as failed
            raise

    def test_metrics_query_complex_filter(self, real_client, output_dir):
        """Test metrics query with complex AND filter"""
        end_date = (datetime.now(timezone.utc) - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (end_date - timedelta(days=4)).replace(hour=0, minute=0, second=0, microsecond=0)

        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            dimensions=[
                Dimension(name="advertiser_name"),
                Dimension(name="device_type"),
                Dimension(name="device_region")
            ],
            measures=[
                Measure(name="overall_spend"),
                Measure(name="total_bids"),
                Measure(name="impressions"),
                Measure(name="clicks"),
                Measure(name="ctr")
            ],
            where=Expression(
                cond=Condition(
                    op=Operator.AND,
                    exprs=[
                        Expression(
                            cond=Condition(
                                op=Operator.EQ,
                                exprs=[
                                    Expression(name="device_type"),
                                    Expression(val="mobile")
                                ]
                            )
                        ),
                        Expression(
                            cond=Condition(
                                op=Operator.IN,
                                exprs=[
                                    Expression(name="device_region"),
                                    Expression(val=["US", "GB", "CA"])
                                ]
                            )
                        )
                    ]
                )
            ),
            time_range=TimeRange(
                start=start_date.isoformat(),
                end=end_date.isoformat()
            ),
            sort=[Sort(name="overall_spend", desc=True)],
            limit=50
        )

        result = real_client.queries.metrics(query)

        save_result(
            output_dir,
            "metrics_query_complex_filter",
            query.model_dump(),
            {"data": result.data},
            {
                "description": "Mobile campaigns in US, GB, CA regions",
                "filter": "device_type = 'mobile' AND device_region IN ('US', 'GB', 'CA')",
                "time_range": f"{start_date.date()} to {end_date.date()}"
            },
            subfolder="metrics"
        )

        assert result is not None
        print(f"\n✓ Retrieved {len(result.data)} rows (complex filter)")

    def test_query_builder_with_time_dimension(self, real_client, output_dir):
        """Test QueryBuilder with time-based dimension"""
        # Query last 7 days with daily granularity
        end_date = (datetime.now(timezone.utc) - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (end_date - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)

        query = (
            QueryBuilder()
            .metrics_view(TEST_METRICS_VIEW)
            .dimension(
                "timestamp_day",
                {"time_floor": {"dimension": "__time", "grain": "day"}}
            )
            .dimension("advertiser_name")
            .measures(["overall_spend", "total_bids", "win_rate"])
            .time_range({
                "start": start_date,
                "end": end_date
            })
            .sorts([
                {"name": "timestamp_day", "desc": False},
                {"name": "overall_spend", "desc": True}
            ])
            .limit(100)
            .build()
        )

        result = real_client.queries.metrics(query)

        save_result(
            output_dir,
            "query_builder_time_dimension",
            query.model_dump(),
            {"data": result.data},
            {
                "description": "QueryBuilder: Time-series query with daily granularity by advertiser",
                "time_range": f"{start_date.date()} to {end_date.date()}",
                "note": "Built using QueryBuilder fluent API"
            },
            subfolder="builder"
        )

        assert result is not None
        print(f"\n✓ Retrieved {len(result.data)} time-series rows (via QueryBuilder)")

    def test_query_builder_with_complex_filter(self, real_client, output_dir):
        """Test QueryBuilder with complex AND filter"""
        end_date = (datetime.now(timezone.utc) - timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = (end_date - timedelta(days=4)).replace(hour=0, minute=0, second=0, microsecond=0)

        query = (
            QueryBuilder()
            .metrics_view(TEST_METRICS_VIEW)
            .dimensions(["advertiser_name", "device_type", "device_region"])
            .measures(["overall_spend", "total_bids", "impressions", "clicks", "ctr"])
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
            .sort("overall_spend", desc=True)
            .limit(50)
            .build()
        )

        result = real_client.queries.metrics(query)

        save_result(
            output_dir,
            "query_builder_complex_filter",
            query.model_dump(),
            {"data": result.data},
            {
                "description": "QueryBuilder: Mobile campaigns in US, GB, CA regions",
                "filter": "device_type = 'mobile' AND device_region IN ('US', 'GB', 'CA')",
                "time_range": f"{start_date.date()} to {end_date.date()}",
                "note": "Built using QueryBuilder fluent API with dict-based filters"
            },
            subfolder="builder"
        )

        assert result is not None
        print(f"\n✓ Retrieved {len(result.data)} rows (complex filter via QueryBuilder)")


@pytest.mark.e2e
class TestMetricsSqlQueryE2E:
    """E2E tests for metrics SQL queries"""

    def test_basic_metrics_sql(self, real_client, output_dir):
        """Test basic metrics SQL query"""
        from pyrill.exceptions import RillAPIError

        query = MetricsSqlQuery(
            sql="""
            SELECT
                advertiser_name,
                device_type,
                overall_spend,
                total_bids
            FROM bids_metrics
            ORDER BY overall_spend DESC
            LIMIT 20
            """
        )

        try:
            result = real_client.queries.metrics_sql(query)

            save_result(
                output_dir,
                "basic_metrics_sql",
                {"sql": query.sql},
                {"data": result.data},
                {
                    "description": "Metrics SQL query - queries pre-aggregated metrics view",
                    "note": "Metrics-SQL queries the metrics view directly (no GROUP BY/aggregations needed)"
                },
                subfolder="metrics_sql"
            )

            assert result is not None
            print(f"\n✓ Retrieved {len(result.data)} rows from SQL query")
        except RillAPIError as e:
            # Save error details for diagnosis
            save_error(
                output_dir,
                "basic_metrics_sql",
                {"sql": query.sql},
                e,
                {
                    "description": "Aggregated spend by advertiser and device type (FAILED)",
                    "note": "This endpoint may not be available for all projects"
                },
                subfolder="metrics_sql"
            )
            # Re-raise to mark test as failed
            raise


@pytest.mark.e2e
class TestSqlQueryE2E:
    """E2E tests for raw SQL queries"""

    def test_basic_sql_query(self, real_client, output_dir):
        """Test basic raw SQL query"""
        query = SqlQuery(
            sql="""
            SELECT
                COUNT(*) as total_rows,
                COUNT(DISTINCT advertiser_name) as unique_advertisers,
                COUNT(DISTINCT campaign_name) as unique_campaigns,
                MIN(__time) as earliest_date,
                MAX(__time) as latest_date
            FROM bids_data_model
            """,
            connector="duckdb"
        )

        result = real_client.queries.sql(query)

        save_result(
            output_dir,
            "basic_sql_query",
            {"sql": query.sql, "connector": query.connector},
            {"data": result.data},
            {
                "description": "Dataset summary statistics"
            },
            subfolder="sql"
        )

        assert result is not None
        print(f"\n✓ Retrieved {len(result.data)} rows from raw SQL")
        if result.data:
            print(f"  Dataset stats: {json.dumps(result.data[0], indent=2, default=str)}")
