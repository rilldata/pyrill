"""
Pytest fixtures for E2E tests that save results to disk for review

Note: Debug folder clearing is handled by the root conftest.py clear_debug_folder fixture
"""

import json
from pathlib import Path
import pytest


# E2E Test Configuration Constants
TEST_ORG = "demo"
TEST_PROJECT = "rill-openrtb-prog-ads"
TEST_METRICS_VIEW = "bids_metrics"
TEST_PARTITION_PROJECT = "my-rill-tutorial"
TEST_EXPECTED_METRICS_VIEW_ANNOTATIONS = "auction_metrics"


# Storage for test results during the session
_reports_test_results = []


@pytest.fixture(scope="session", autouse=True)
def save_e2e_reports():
    """
    Session-scoped fixture that saves e2e report test results after all tests complete.

    Note: Debug folder initialization/clearing is handled by root conftest.py
    """
    yield  # Tests run here

    # After all tests complete, save results
    if _reports_test_results:
        debug_dir = Path(__file__).parent.parent.parent / "debug"
        output_dir = debug_dir / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save detailed results for each test
        for result in _reports_test_results:
            if result.get("data"):
                filename = f"{result['test_name']}.json"
                filepath = output_dir / filename
                with open(filepath, 'w') as f:
                    json.dump(result["data"], f, indent=2, default=str)


@pytest.fixture
def record_reports_test():
    """
    Fixture to record test results for reports tests.

    Usage in test:
        def test_something(record_reports_test):
            result = record_reports_test(
                test_name="test_list_reports",
                data=reports_list
            )
    """
    def _record(test_name, data=None):
        global _reports_test_results
        _reports_test_results.append({
            "test_name": test_name,
            "data": data,
        })
        return data

    return _record
