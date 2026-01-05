"""
End-to-end tests for rilltime expressions in metrics queries

These tests validate that various rilltime expressions work with the Rill API.
Based on test cases from: /Users/jon/RillGitHub/rill/runtime/pkg/rilltime/rilltime_test.go

Run with: pytest tests/client/e2e/test_rilltime_e2e.py --run-e2e -v -s
"""

import os
import json
from pathlib import Path
import pytest

from pyrill import (
    RillClient,
    MetricsQuery,
    Dimension,
    Measure,
    TimeRange,
    Sort,
)


# Test configuration
TEST_ORG = "demo"
TEST_PROJECT = "rill-openrtb-prog-ads"
TEST_METRICS_VIEW = "bids_metrics"

# Output directory for test results
OUTPUT_DIR = Path(__file__).parent.parent.parent / "debug" / "rilltime"


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


def save_result(output_dir: Path, test_name: str, query: dict, result: dict, metadata: dict = None):
    """Save query and result to JSON file"""
    output = {
        "test_name": test_name,
        "org": TEST_ORG,
        "project": TEST_PROJECT,
        "query": query,
        "result": result,
        "metadata": metadata or {},
        "success": True
    }

    filename = f"{test_name}.json"
    filepath = output_dir / filename

    with open(filepath, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n✓ Saved result to: {filepath}")
    print(f"  - Rows returned: {len(result.get('data', []))}")
    if result.get('data'):
        print(f"  - Sample row: {json.dumps(result['data'][0], default=str)}")
    return filepath


def save_error(output_dir: Path, test_name: str, query: dict, error: Exception, metadata: dict = None):
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

    filename = f"{test_name}_ERROR.json"
    filepath = output_dir / filename

    with open(filepath, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n✗ Saved error to: {filepath}")
    print(f"  - Error type: {error_data['error_type']}")
    print(f"  - Status code: {error_data.get('status_code', 'N/A')}")
    print(f"  - Message: {error_data['error_message']}")
    return filepath


@pytest.mark.e2e
class TestRilltimeExpressionsE2E:
    """E2E tests for rilltime expressions in metrics queries"""

    def _run_expression_test(self, real_client, output_dir, test_name: str, time_expression: str,
                            description: str, source: str):
        """Helper method to run a single rilltime expression test"""
        from pyrill.exceptions import RillAPIError

        query = MetricsQuery(
            metrics_view=TEST_METRICS_VIEW,
            dimensions=[
                Dimension(name="advertiser_name"),
            ],
            measures=[
                Measure(name="overall_spend"),
            ],
            time_range=TimeRange(expression=time_expression),
            limit=10
        )

        try:
            result = real_client.queries.metrics(query)

            save_result(
                output_dir,
                test_name,
                query.model_dump(),
                {"data": result.data},
                {
                    "description": description,
                    "expression": time_expression,
                    "source": source,
                }
            )

            print(f"\n✓ Retrieved {len(result.data)} rows using expression: {time_expression}")
            return True

        except RillAPIError as e:
            # Save error details for diagnosis
            save_error(
                output_dir,
                test_name,
                query.model_dump(),
                e,
                {
                    "description": f"{description} (FAILED)",
                    "expression": time_expression,
                    "source": source,
                }
            )
            # Don't re-raise - we want to see which expressions work and which don't
            print(f"\n✗ Expression failed: {time_expression}")
            print(f"   Error: {str(e)}")
            return False

    def test_rilltime_2d_to_ref_as_of_latest_d(self, real_client, output_dir):
        """Test: -2D to ref as of latest/D"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_2d_to_ref_as_of_latest_d",
            "-2D to ref as of latest/D",
            "Last 2 complete days relative to latest data boundary",
            "TestEval_WatermarkOnBoundary rilltime_test.go:334"
        )

    # ========================================================================
    # TestEval_PreviousAndCurrentCompleteGrain
    # ========================================================================

    def test_rilltime_previous_complete_day(self, real_client, output_dir):
        """Test: 1D as of watermark/D - Previous complete day"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_previous_complete_day",
            "1D as of watermark/D",
            "Previous complete day",
            "TestEval_PreviousAndCurrentCompleteGrain rilltime_test.go:63"
        )

    def test_rilltime_last_2_days_excluding_current(self, real_client, output_dir):
        """Test: 2D as of watermark/D - Last 2 days, excluding current day"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_last_2_days_excluding_current",
            "2D as of watermark/D",
            "Last 2 days, excluding current day",
            "TestEval_PreviousAndCurrentCompleteGrain rilltime_test.go:69"
        )

    def test_rilltime_last_2_weeks_excluding_current(self, real_client, output_dir):
        """Test: 2W as of watermark/W - Last 2 weeks, excluding current week"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_last_2_weeks_excluding_current",
            "2W as of watermark/W",
            "Last 2 weeks, excluding current week",
            "TestEval_PreviousAndCurrentCompleteGrain rilltime_test.go:83"
        )

    def test_rilltime_previous_complete_month(self, real_client, output_dir):
        """Test: 1M as of watermark/M - Previous complete month"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_previous_complete_month",
            "1M as of watermark/M",
            "Previous complete month",
            "TestEval_PreviousAndCurrentCompleteGrain rilltime_test.go:91"
        )

    def test_rilltime_previous_complete_quarter(self, real_client, output_dir):
        """Test: 1Q as of watermark/Q - Previous complete quarter"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_previous_complete_quarter",
            "1Q as of watermark/Q",
            "Previous complete quarter",
            "TestEval_PreviousAndCurrentCompleteGrain rilltime_test.go:105"
        )

    def test_rilltime_mtd(self, real_client, output_dir):
        """Test: MTD as of watermark/M+1M - Current complete month (MTD)"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_mtd",
            "MTD as of watermark/M+1M",
            "Month-to-date (current complete month)",
            "TestEval_PreviousAndCurrentCompleteGrain rilltime_test.go:102"
        )

    # ========================================================================
    # TestEval_FirstAndLastOfPeriod
    # ========================================================================

    def test_rilltime_last_2_mins_of_last_2_days(self, real_client, output_dir):
        """Test: -2D/D-2m to -2D/D as of watermark/D - Last 2 mins of last 2 days"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_last_2_mins_of_last_2_days",
            "-2D/D-2m to -2D/D as of watermark/D",
            "Last 2 minutes of last 2 days",
            "TestEval_FirstAndLastOfPeriod rilltime_test.go:160"
        )

    def test_rilltime_first_2_hrs_of_last_2_days(self, real_client, output_dir):
        """Test: -2D/D to -2D/D+2h as of watermark/D - First 2 hours of last 2 days"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_first_2_hrs_of_last_2_days",
            "-2D/D to -2D/D+2h as of watermark/D",
            "First 2 hours of last 2 days",
            "TestEval_FirstAndLastOfPeriod rilltime_test.go:168"
        )

    def test_rilltime_day_2_of_last_2_weeks(self, real_client, output_dir):
        """Test: D2 as of -2W/W as of watermark/W - Day 2 of last 2 weeks"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_day_2_of_last_2_weeks",
            "D2 as of -2W/W as of watermark/W",
            "Day 2 of last 2 weeks",
            "TestEval_FirstAndLastOfPeriod rilltime_test.go:185"
        )

    def test_rilltime_week_2_of_last_2_months(self, real_client, output_dir):
        """Test: W2 as of -2M/M as of watermark/M - Week 2 of last 2 months"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_week_2_of_last_2_months",
            "W2 as of -2M/M as of watermark/M",
            "Week 2 of last 2 months",
            "TestEval_FirstAndLastOfPeriod rilltime_test.go:199"
        )

    # ========================================================================
    # TestEval_OrdinalVariations
    # ========================================================================

    def test_rilltime_w1(self, real_client, output_dir):
        """Test: W1 - Week 1 of current period"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_w1",
            "W1",
            "Week 1 of current period",
            "TestEval_OrdinalVariations rilltime_test.go:235"
        )

    def test_rilltime_w1_as_of_2m_ago(self, real_client, output_dir):
        """Test: W1 as of -2M - Week 1 of 2 months ago"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_w1_as_of_2m_ago",
            "W1 as of -2M",
            "Week 1 of 2 months ago",
            "TestEval_OrdinalVariations rilltime_test.go:236"
        )

    # ========================================================================
    # TestEval_WeekCorrections
    # ========================================================================

    def test_rilltime_week_monday_boundary(self, real_client, output_dir):
        """Test: W1 as of 2024-07-01T00:00:00Z - Week on Monday boundary"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_week_monday_boundary",
            "W1 as of 2024-07-01T00:00:00Z",
            "Week 1 when boundary is on Monday",
            "TestEval_WeekCorrections rilltime_test.go:248"
        )

    def test_rilltime_week_thursday_boundary(self, real_client, output_dir):
        """Test: W1 as of 2025-05-01T00:00:00Z - Week on Thursday boundary"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_week_thursday_boundary",
            "W1 as of 2025-05-01T00:00:00Z",
            "Week 1 when boundary is on Thursday",
            "TestEval_WeekCorrections rilltime_test.go:263"
        )

    # ========================================================================
    # TestEval_IsoTimeRanges
    # ========================================================================

    def test_rilltime_iso_time_range(self, real_client, output_dir):
        """Test: 2025-02-20T01:23:45Z to 2025-07-15T02:34:50Z - ISO time range"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_iso_time_range",
            "2025-02-20T01:23:45Z to 2025-07-15T02:34:50Z",
            "Explicit ISO 8601 time range",
            "TestEval_IsoTimeRanges rilltime_test.go:302"
        )

    def test_rilltime_iso_date(self, real_client, output_dir):
        """Test: 2025-02-20 - ISO date (single day)"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_iso_date",
            "2025-02-20",
            "Single ISO date (full day)",
            "TestEval_IsoTimeRanges rilltime_test.go:311"
        )

    def test_rilltime_iso_month(self, real_client, output_dir):
        """Test: 2025-02 - ISO month"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_iso_month",
            "2025-02",
            "Single ISO month",
            "TestEval_IsoTimeRanges rilltime_test.go:313"
        )

    def test_rilltime_iso_year(self, real_client, output_dir):
        """Test: 2025 - ISO year"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_iso_year",
            "2025",
            "Single ISO year",
            "TestEval_IsoTimeRanges rilltime_test.go:315"
        )

    # ========================================================================
    # TestEval_WatermarkOnBoundary
    # ========================================================================

    def test_rilltime_1h_as_of_watermark_h(self, real_client, output_dir):
        """Test: 1h as of watermark/h - Previous complete hour"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_1h_as_of_watermark_h",
            "1h as of watermark/h",
            "Previous complete hour at watermark boundary",
            "TestEval_WatermarkOnBoundary rilltime_test.go:329"
        )

    def test_rilltime_2d_as_of_watermark_d(self, real_client, output_dir):
        """Test: 2D as of watermark/D - Last 2 days at watermark boundary"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_2d_as_of_watermark_d",
            "2D as of watermark/D",
            "Last 2 days at watermark boundary",
            "TestEval_WatermarkOnBoundary rilltime_test.go:342"
        )

    def test_rilltime_w2_as_of_1m_as_of_latest_m(self, real_client, output_dir):
        """Test: W2 as of -1M as of latest/M - Week 2 of previous month"""
        self._run_expression_test(
            real_client, output_dir,
            "rilltime_w2_as_of_1m_as_of_latest_m",
            "W2 as of -1M as of latest/M",
            "Week 2 of previous month at latest boundary",
            "TestEval_WatermarkOnBoundary rilltime_test.go:353"
        )
