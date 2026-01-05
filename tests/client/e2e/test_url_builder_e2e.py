"""
End-to-end tests for UrlBuilder - converts queries from test_query_e2e.py to URLs

These tests take all MetricsQuery objects from test_query_e2e.py and generate URLs.
URLs are saved to fixtures/query_results/object/urls/ for inspection and validation.

Run with: pytest tests/client/e2e/test_url_builder_e2e.py --run-e2e -v -s
"""

import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import pytest

from pyrill import (
    UrlBuilder,
    QueryBuilder,
    MetricsQuery,
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


# Test configuration (matching test_query_e2e.py)
TEST_ORG = "demo"
TEST_PROJECT = "rill-openrtb-prog-ads"
TEST_METRICS_VIEW = "bids_metrics"

# Output directory for URLs
URL_OUTPUT_DIR = Path(__file__).parent.parent.parent / "fixtures" / "query_results" / "object" / "urls"


@pytest.fixture(scope="module")
def url_builder():
    """Create a UrlBuilder for generating URLs"""
    return UrlBuilder(
        org=TEST_ORG,
        project=TEST_PROJECT
    )


@pytest.fixture(scope="module")
def url_output_dir():
    """Create output directory for URL results"""
    URL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return URL_OUTPUT_DIR


def save_url_result(output_dir: Path, test_name: str, query: MetricsQuery, url_obj, metadata: dict = None, subfolder: str = None):
    """Save query and generated URL to JSON file"""
    output = {
        "test_name": test_name,
        "org": TEST_ORG,
        "project": TEST_PROJECT,
        "query": query.model_dump(),
        "url": {
            "string": str(url_obj),
            "components": {
                "base_url": url_obj.base_url,
                "org": url_obj.org,
                "project": url_obj.project,
                "page_type": url_obj.page_type,
                "page_name": url_obj.page_name,
                "time_range": url_obj.time_range,
                "timezone": url_obj.timezone,
                "measures": url_obj.measures,
                "dimensions": url_obj.dimensions,
                "sort_dir": url_obj.sort_dir,
                "sort_by": url_obj.sort_by,
                "leaderboard_measures": url_obj.leaderboard_measures,
                "view": url_obj.view,
                "rows": url_obj.rows,
                "cols": url_obj.cols,
                "table_mode": url_obj.table_mode,
                "grain": url_obj.grain,
                "compare_time_range": url_obj.compare_time_range,
            }
        },
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

    print(f"\n✓ Saved URL to: {filepath}")
    print(f"  - URL: {str(url_obj)}")
    print(f"  - Length: {len(str(url_obj))} characters")
    return filepath


def save_url_error(output_dir: Path, test_name: str, query: MetricsQuery, error: Exception, metadata: dict = None, subfolder: str = None):
    """Save query and URL generation error to JSON file"""
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
    }

    output = {
        "test_name": test_name,
        "org": TEST_ORG,
        "project": TEST_PROJECT,
        "query": query.model_dump() if isinstance(query, MetricsQuery) else query,
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

    print(f"\n✗ Saved URL generation error to: {filepath}")
    print(f"  - Error type: {error_data['error_type']}")
    print(f"  - Message: {error_data['error_message']}")
    return filepath


@pytest.mark.e2e
class TestMetricsQueryUrlGeneration:
    """Generate URLs for all MetricsQuery tests from test_query_e2e.py"""

    def test_basic_metrics_query_url(self, url_builder, url_output_dir):
        """Generate URL for basic metrics query with dimensions and measures"""
        # Query last 3 days of data (matching test_query_e2e.py)
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

        url = url_builder.build_url(query)

        # Save URL result
        save_url_result(
            url_output_dir,
            "basic_metrics_query",
            query,
            url,
            {
                "description": "Basic metrics query with advertiser and device dimensions",
                "time_range": f"{start_date.date()} to {end_date.date()}",
                "expected_params": ["tr", "measures", "dims", "sort_dir", "sort_by"]
            },
            subfolder="metrics"
        )

        assert str(url) is not None
        assert "bids_explore" in str(url)  # page_name in URL, not metrics_view
        assert "advertiser_name" in str(url)

    def test_metrics_query_with_time_dimension_url(self, url_builder, url_output_dir):
        """Generate URL for metrics query with time-based dimension"""
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

        url = url_builder.build_url(query)

        save_url_result(
            url_output_dir,
            "metrics_query_time_dimension",
            query,
            url,
            {
                "description": "Time-series query with daily granularity by advertiser",
                "time_range": f"{start_date.date()} to {end_date.date()}",
                "note": "Computed dimension with time_floor - dimension name used in URL"
            },
            subfolder="metrics"
        )

        assert str(url) is not None
        print(f"\n✓ Generated URL for time-series query")

    def test_metrics_query_with_filter_url(self, url_builder, url_output_dir):
        """Generate URL for metrics query with WHERE filter"""
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

        url = url_builder.build_url(query)

        save_url_result(
            url_output_dir,
            "metrics_query_with_filter",
            query,
            url,
            {
                "description": "Mobile device campaigns sorted by spend",
                "filter": "device_type = 'mobile'",
                "time_range": f"{start_date.date()} to {end_date.date()}",
                "warning": "WHERE clause cannot be encoded in URL - URL generated without filter"
            },
            subfolder="metrics"
        )

        assert str(url) is not None
        # Note: filter won't be in URL (unsupported feature)
        print(f"\n✓ Generated URL for query with filter (filter not in URL - expected)")

    def test_metrics_query_with_iso_duration_time_range_url(self, url_builder, url_output_dir):
        """Generate URL for metrics query with ISO 8601 duration"""
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

        url = url_builder.build_url(query)

        save_url_result(
            url_output_dir,
            "metrics_query_iso_duration_time_range",
            query,
            url,
            {
                "description": "Video performance metrics over last 7 days using iso_duration",
                "time_range": "iso_duration='P7D'",
                "expected_tr_param": "P7D"
            },
            subfolder="metrics"
        )

        assert str(url) is not None
        assert "tr=P7D" in str(url)
        print(f"\n✓ Generated URL with iso_duration time range")

    def test_metrics_query_with_expression_time_range_url(self, url_builder, url_output_dir):
        """Generate URL for metrics query with expression time range"""
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

        url = url_builder.build_url(query)

        save_url_result(
            url_output_dir,
            "metrics_query_expression_time_range",
            query,
            url,
            {
                "description": "Video performance metrics using expression parameter",
                "time_range": "expression='P7D'",
                "note": "Expression passed through as-is to tr parameter"
            },
            subfolder="metrics"
        )

        assert str(url) is not None
        assert "tr=P7D" in str(url)
        print(f"\n✓ Generated URL with expression time range")

    def test_metrics_query_complex_filter_url(self, url_builder, url_output_dir):
        """Generate URL for metrics query with complex AND filter"""
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

        url = url_builder.build_url(query)

        save_url_result(
            url_output_dir,
            "metrics_query_complex_filter",
            query,
            url,
            {
                "description": "Mobile campaigns in US, GB, CA regions",
                "filter": "device_type = 'mobile' AND device_region IN ('US', 'GB', 'CA')",
                "time_range": f"{start_date.date()} to {end_date.date()}",
                "warning": "Complex WHERE clause cannot be encoded in URL"
            },
            subfolder="metrics"
        )

        assert str(url) is not None
        print(f"\n✓ Generated URL for complex filter query (filter not in URL)")

    def test_query_builder_with_time_dimension_url(self, url_builder, url_output_dir):
        """Generate URL for QueryBuilder with time-based dimension"""
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

        url = url_builder.build_url(query)

        save_url_result(
            url_output_dir,
            "query_builder_time_dimension",
            query,
            url,
            {
                "description": "QueryBuilder: Time-series query with daily granularity by advertiser",
                "time_range": f"{start_date.date()} to {end_date.date()}",
                "note": "Built using QueryBuilder fluent API"
            },
            subfolder="builder"
        )

        assert str(url) is not None
        print(f"\n✓ Generated URL for QueryBuilder time-series query")

    def test_query_builder_with_complex_filter_url(self, url_builder, url_output_dir):
        """Generate URL for QueryBuilder with complex AND filter"""
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

        url = url_builder.build_url(query)

        save_url_result(
            url_output_dir,
            "query_builder_complex_filter",
            query,
            url,
            {
                "description": "QueryBuilder: Mobile campaigns in US, GB, CA regions",
                "filter": "device_type = 'mobile' AND device_region IN ('US', 'GB', 'CA')",
                "time_range": f"{start_date.date()} to {end_date.date()}",
                "note": "Built using QueryBuilder fluent API with dict-based filters",
                "warning": "WHERE clause not encoded in URL"
            },
            subfolder="builder"
        )

        assert str(url) is not None
        print(f"\n✓ Generated URL for QueryBuilder complex filter query")


@pytest.mark.e2e
class TestUrlBuilderVariations:
    """Test UrlBuilder with different parameter variations"""

    def test_url_with_pivot_mode(self, url_builder, url_output_dir):
        """Generate pivot mode URL"""
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
                Measure(name="impressions")
            ],
            time_range=TimeRange(
                start=start_date.isoformat(),
                end=end_date.isoformat()
            ),
            sort=[Sort(name="timestamp_day", desc=False)]
        )

        # Generate standard URL
        standard_url = url_builder.build_url(query)

        # Generate pivot URL
        pivot_url = url_builder.build_url(query, pivot=True)

        # Save both for comparison
        save_url_result(
            url_output_dir,
            "url_pivot_mode_standard",
            query,
            standard_url,
            {
                "description": "Standard explore view (for comparison with pivot)",
                "time_range": f"{start_date.date()} to {end_date.date()}"
            },
            subfolder="variations"
        )

        save_url_result(
            url_output_dir,
            "url_pivot_mode_pivot",
            query,
            pivot_url,
            {
                "description": "Pivot table view of same query",
                "time_range": f"{start_date.date()} to {end_date.date()}",
                "note": "Uses view=pivot, rows=dimensions, cols=measures, table_mode=nest"
            },
            subfolder="variations"
        )

        assert "view=pivot" in str(pivot_url)
        assert "view=pivot" not in str(standard_url)
        print(f"\n✓ Generated both standard and pivot URLs")

    def test_url_with_leaderboard_variations(self, url_builder, url_output_dir):
        """Generate URLs with different leaderboard measure configurations"""
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            dimensions=[
                Dimension(name="advertiser_name"),
                Dimension(name="campaign_name")
            ],
            measures=[
                Measure(name="overall_spend"),
                Measure(name="total_bids"),
                Measure(name="impressions"),
                Measure(name="clicks"),
                Measure(name="ctr")
            ],
            time_range=TimeRange(iso_duration="P7D"),
            sort=[Sort(name="overall_spend", desc=True)]
        )

        # Generate with all measures in leaderboard
        url_multi = url_builder.build_url(query, multi_leaderboard_measures=True)

        # Generate with only first measure in leaderboard
        url_single = url_builder.build_url(query, multi_leaderboard_measures=False)

        save_url_result(
            url_output_dir,
            "url_leaderboard_multi",
            query,
            url_multi,
            {
                "description": "All measures in leaderboard",
                "leaderboard_config": "multi_leaderboard_measures=True",
                "expected_leaderboard": "overall_spend,total_bids,impressions,clicks,ctr"
            },
            subfolder="variations"
        )

        save_url_result(
            url_output_dir,
            "url_leaderboard_single",
            query,
            url_single,
            {
                "description": "Only first measure in leaderboard",
                "leaderboard_config": "multi_leaderboard_measures=False",
                "expected_leaderboard": "overall_spend"
            },
            subfolder="variations"
        )

        assert "leaderboard_measures=" in str(url_multi)
        assert "leaderboard_measures=" in str(url_single)
        print(f"\n✓ Generated URLs with different leaderboard configurations")

    def test_url_with_comparison(self, url_builder, url_output_dir):
        """Generate URL with comparison enabled"""
        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            dimensions=[
                Dimension(name="advertiser_name")
            ],
            measures=[
                Measure(name="overall_spend"),
                Measure(name="total_bids")
            ],
            time_range=TimeRange(iso_duration="P7D"),
            sort=[Sort(name="overall_spend", desc=True)]
        )

        # Without comparison
        url_no_compare = url_builder.build_url(query, enable_comparison=False)

        # With comparison
        url_with_compare = url_builder.build_url(query, enable_comparison=True)

        save_url_result(
            url_output_dir,
            "url_comparison_disabled",
            query,
            url_no_compare,
            {
                "description": "URL without comparison",
                "comparison_config": "enable_comparison=False"
            },
            subfolder="variations"
        )

        save_url_result(
            url_output_dir,
            "url_comparison_enabled",
            query,
            url_with_compare,
            {
                "description": "URL with prior period comparison",
                "comparison_config": "enable_comparison=True",
                "expected_param": "compare_tr=rill-PP"
            },
            subfolder="variations"
        )

        assert "compare_tr=rill-PP" in str(url_with_compare)
        assert "compare_tr" not in str(url_no_compare)
        print(f"\n✓ Generated URLs with and without comparison")

    def test_url_with_timezone_variations(self, url_builder, url_output_dir):
        """Generate URLs with different timezones"""
        timezones = [
            ("America/New_York", "Eastern Time"),
            ("Europe/London", "British Time"),
            ("Asia/Tokyo", "Japan Time"),
            ("UTC", "Coordinated Universal Time")
        ]

        for tz, description in timezones:
            query = MetricsQuery(
                metrics_view=TEST_METRICS_VIEW,
                dimensions=[Dimension(name="advertiser_name")],
                measures=[Measure(name="overall_spend")],
                time_range=TimeRange(iso_duration="P7D"),
                time_zone=tz,
                sort=[Sort(name="overall_spend", desc=True)]
            )

            url = url_builder.build_url(query)

            save_url_result(
                url_output_dir,
                f"url_timezone_{tz.replace('/', '_')}",
                query,
                url,
                {
                    "description": f"URL with {description} timezone",
                    "timezone": tz,
                    "expected_encoding": f"tz={tz.replace('/', '%2F')}"
                },
                subfolder="variations"
            )

        print(f"\n✓ Generated URLs for {len(timezones)} different timezones")
