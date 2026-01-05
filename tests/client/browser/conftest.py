"""
Browser test fixtures for URL validation using Playwright.

Provides fixtures for:
- Browser context setup
- Screenshot directory management
- Browser configuration options
"""

import pytest
from pathlib import Path
from datetime import datetime


@pytest.fixture(scope="session")
def screenshot_dir():
    """Create and return the screenshot directory path"""
    base_dir = Path(__file__).parent.parent.parent / "debug" / "screenshots"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


@pytest.fixture(scope="session")
def browser_config(pytestconfig):
    """Browser configuration options from command line"""
    return {
        "capture_screenshots": pytestconfig.getoption("--capture-screenshots", default=False),
        "headed": pytestconfig.getoption("--headed", default=False),  # pytest-playwright provides this
        "timeout": pytestconfig.getoption("--browser-timeout", default=30000),  # 30 seconds
    }


# Note: pytest_addoption is defined in tests/conftest.py to ensure proper registration
# Browser-specific options (--capture-screenshots, --browser-timeout) are defined there
