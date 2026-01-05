"""
Browser-based URL validation tests using Playwright.

These tests validate that UrlBuilder-generated URLs load correctly in a real browser.
They check for 404 errors and optionally capture screenshots for visual verification.

Run with:
    cd pyrill-tests && uv run pytest tests/client/browser/ -v
    cd pyrill-tests && uv run pytest tests/client/browser/ --capture-screenshots -v
    cd pyrill-tests && uv run pytest tests/client/browser/ --headed -v

The tests automatically discover all URL fixture JSON files and validate each URL.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Page


# Directory containing URL fixture files
URL_FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures" / "query_results" / "object" / "urls"


def discover_url_fixtures():
    """
    Discover all URL fixture JSON files.

    Returns list of tuples: (test_id, fixture_path, url_string)
    """
    fixtures = []

    if not URL_FIXTURES_DIR.exists():
        return fixtures

    for json_file in URL_FIXTURES_DIR.rglob("*.json"):
        # Skip error files
        if "_ERROR" in json_file.name:
            continue

        try:
            with open(json_file, "r") as f:
                data = json.load(f)

            # Extract URL string
            url = data.get("url", {}).get("string")
            if url:
                # Create a readable test ID from the file path
                relative_path = json_file.relative_to(URL_FIXTURES_DIR)
                test_id = str(relative_path).replace("/", "_").replace(".json", "")
                fixtures.append((test_id, json_file, url))
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Could not parse {json_file}: {e}")
            continue

    return fixtures


def check_for_404_error(page: Page) -> bool:
    """
    Check if the page shows a 404 error.

    Returns True if 404 error is detected, False otherwise.
    """
    # Check for the specific 404 indicator mentioned by the user
    # <h1 class="status-code svelte-h1ftig">404</h1>
    try:
        error_heading = page.locator('h1.status-code.svelte-h1ftig')
        if error_heading.count() > 0 and "404" in error_heading.inner_text():
            return True
    except:
        pass

    # Additional checks for 404 errors
    try:
        # Check page title for common 404 indicators
        title = page.title().lower()
        if "404" in title or "not found" in title:
            return True
    except:
        pass

    return False


def save_screenshot(page: Page, screenshot_dir: Path, test_id: str, status: str = "success") -> Path:
    """
    Save a screenshot of the current page.

    Args:
        page: Playwright page object
        screenshot_dir: Directory to save screenshots
        test_id: Test identifier for filename
        status: "success" or "failure"

    Returns:
        Path to saved screenshot
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{test_id}_{status}_{timestamp}.png"
    filepath = screenshot_dir / filename

    # Create parent directory if needed
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # Take screenshot
    page.screenshot(path=str(filepath), full_page=True)

    return filepath


@pytest.mark.browser
class TestUrlValidation:
    """Browser-based validation of UrlBuilder-generated URLs"""

    @pytest.mark.parametrize("test_id,fixture_path,url", discover_url_fixtures())
    def test_url_loads_without_404(self, test_id, fixture_path, url, page: Page, screenshot_dir, browser_config):
        """
        Validate that a URL loads successfully without 404 errors.

        This test:
        1. Loads the URL in an incognito browser context
        2. Waits for the page to stabilize
        3. Checks for 404 error indicators
        4. Optionally captures a screenshot
        """
        print(f"\n{'='*80}")
        print(f"Testing URL: {test_id}")
        print(f"Fixture: {fixture_path.name}")
        print(f"URL: {url}")
        print(f"{'='*80}")

        try:
            # Navigate to the URL with timeout
            timeout = browser_config["timeout"]
            print(f"Loading page (timeout: {timeout}ms)...")

            response = page.goto(url, timeout=timeout, wait_until="networkidle")

            # Check HTTP status code
            if response and response.status >= 400:
                print(f"WARNING: HTTP status code: {response.status}")

            # Wait a bit for any dynamic content to load
            page.wait_for_timeout(2000)  # 2 seconds

            # Check for 404 error
            has_404_error = check_for_404_error(page)

            if has_404_error:
                # Always capture screenshot on failure
                screenshot_path = save_screenshot(page, screenshot_dir, test_id, status="failure")
                print(f"\n✗ 404 ERROR DETECTED!")
                print(f"  Screenshot saved: {screenshot_path}")
                pytest.fail(f"URL returned 404 error: {url}")
            else:
                print(f"\n✓ Page loaded successfully (no 404 error)")

                # Capture screenshot if requested
                if browser_config["capture_screenshots"]:
                    screenshot_path = save_screenshot(page, screenshot_dir, test_id, status="success")
                    print(f"  Screenshot saved: {screenshot_path}")

        except Exception as e:
            # Capture screenshot on any exception
            try:
                screenshot_path = save_screenshot(page, screenshot_dir, test_id, status="error")
                print(f"\n✗ EXCEPTION: {type(e).__name__}: {e}")
                print(f"  Screenshot saved: {screenshot_path}")
            except:
                pass
            raise


@pytest.mark.browser
class TestSpecificUrlValidation:
    """Manual validation tests for specific URLs"""

    def test_good_url_example(self, page: Page, screenshot_dir, browser_config):
        """Test the known good URL provided by the user"""
        url = "https://ui.rilldata.com/demo/rill-openrtb-prog-ads/explore/bids_explore?tr=2025-11-12+to+2025-11-16&measures=overall_spend,total_bids,impressions,clicks,ctr&dims=advertiser_name,device_type,device_region&sort_dir=DESC&sort_by=overall_spend&leaderboard_measures=overall_spend,total_bids,impressions,clicks,ctr&grain=day"

        print(f"\n{'='*80}")
        print(f"Testing KNOWN GOOD URL")
        print(f"URL: {url}")
        print(f"{'='*80}")

        page.goto(url, timeout=browser_config["timeout"], wait_until="networkidle")
        page.wait_for_timeout(2000)

        has_404_error = check_for_404_error(page)
        assert not has_404_error, f"Good URL should not return 404: {url}"

        print(f"✓ Known good URL validated successfully")

        if browser_config["capture_screenshots"]:
            screenshot_path = save_screenshot(page, screenshot_dir, "known_good_url", status="success")
            print(f"  Screenshot saved: {screenshot_path}")

    def test_bad_url_example(self, page: Page, screenshot_dir, browser_config):
        """Test the known bad URL provided by the user (should fail with 404)"""
        url = "https://ui.rilldata.com/demo/rill-openrtb-prog-ads/explore/bids_whatsit?tr=2025-11-12+to+2025-11-16&grain=day&measures=overall_spend%2Ctotal_bids%2Cimpressions%2Cclicks%2Cctr&dims=advertiser_name%2Cdevice_type%2Cdevice_region&leaderboard_measures=overall_spend%2Ctotal_bids%2Cimpressions%2Cclicks%2Cctr"

        print(f"\n{'='*80}")
        print(f"Testing KNOWN BAD URL (expect 404)")
        print(f"URL: {url}")
        print(f"{'='*80}")

        page.goto(url, timeout=browser_config["timeout"], wait_until="networkidle")
        page.wait_for_timeout(2000)

        has_404_error = check_for_404_error(page)

        # Capture screenshot to verify 404 detection
        screenshot_path = save_screenshot(page, screenshot_dir, "known_bad_url", status="404_detected" if has_404_error else "404_missed")
        print(f"Screenshot saved: {screenshot_path}")

        # This test verifies that our 404 detection works
        assert has_404_error, f"Bad URL should return 404 (used to verify 404 detection logic): {url}"

        print(f"✓ 404 error correctly detected for bad URL")
