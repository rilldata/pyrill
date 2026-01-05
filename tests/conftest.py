"""
Pytest configuration and shared fixtures for PyRill SDK client tests

This file contains shared configuration that applies to all client tests.
Client-specific fixtures are in tests/client/conftest.py.
"""

import pytest
import shutil
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def clear_debug_folder():
    """
    Session-scoped fixture that clears the debug folder ONCE before any tests run.

    This ensures a clean slate for each test run across ALL test types (unit, e2e, browser).
    Runs automatically before any tests in the entire session.
    """
    debug_dir = Path(__file__).parent / "debug"

    # Clear debug folder if it exists
    if debug_dir.exists():
        shutil.rmtree(debug_dir)

    # Recreate empty debug folder structure
    debug_dir.mkdir(parents=True, exist_ok=True)
    (debug_dir / "reports").mkdir(exist_ok=True)
    (debug_dir / "screenshots").mkdir(exist_ok=True)

    yield  # Tests run here

    # After all tests complete, nothing to do here
    # (Individual test fixtures handle their own cleanup/saving if needed)


@pytest.fixture
def mock_api_token():
    """Provide a fake API token for testing"""
    return "rill_usr_test_token_123456"


@pytest.fixture
def mock_env_with_token(monkeypatch, mock_api_token):
    """Set up environment with RILL_USER_TOKEN"""
    monkeypatch.setenv("RILL_USER_TOKEN", mock_api_token)
    return mock_api_token


@pytest.fixture
def mock_env_without_token(monkeypatch):
    """Remove RILL_USER_TOKEN from environment"""
    monkeypatch.delenv("RILL_USER_TOKEN", raising=False)


# Pytest configuration hooks

def pytest_configure(config):
    """Configure custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests requiring real credentials")


def pytest_collection_modifyitems(config, items):
    """Automatically skip e2e tests unless explicitly requested"""
    if not config.getoption("--run-e2e", default=False):
        skip_e2e = pytest.mark.skip(reason="E2E tests skipped (use --run-e2e to run)")
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--run-e2e",
        action="store_true",
        default=False,
        help="Run end-to-end tests (requires real credentials)"
    )
    parser.addoption(
        "--capture-screenshots",
        action="store_true",
        default=False,
        help="Capture screenshots of successful page loads"
    )
    parser.addoption(
        "--browser-timeout",
        type=int,
        default=30000,
        help="Browser page load timeout in milliseconds (default: 30000)"
    )


def pytest_sessionfinish(session, exitstatus):
    """Generate summary report after all tests complete (only when --run-e2e is set)"""
    # Only generate report when e2e tests are run
    if not session.config.getoption("--run-e2e", default=False):
        return

    from pathlib import Path
    from tests.fixtures.report_generator import generate_summary_and_readme

    # Path to query results directory
    query_results_dir = Path(__file__).parent / "fixtures" / "query_results"

    # Generate ONE summary report at the top level that includes all subdirectories
    if query_results_dir.exists():
        # Check if there are JSON files recursively
        json_files = list(query_results_dir.rglob("*.json"))
        # Exclude SUMMARY.json from count
        json_files = [f for f in json_files if f.name != "SUMMARY.json"]

        if json_files:
            try:
                generate_summary_and_readme(query_results_dir)
            except Exception as e:
                # Don't fail the test run if report generation fails
                print(f"\nWarning: Failed to generate summary report: {e}")
