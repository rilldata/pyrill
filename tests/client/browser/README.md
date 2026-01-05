# Browser-Based URL Validation Tests

This directory contains Playwright-based browser tests that validate UrlBuilder-generated URLs by loading them in a real browser environment.

## Overview

The browser tests serve to:
- Validate that generated URLs load successfully without 404 errors
- Detect malformed explore names or invalid parameters
- Optionally capture screenshots for visual verification
- Test URLs in an environment that closely matches end-user experience

## Prerequisites

### 1. Install Dependencies

```bash
cd pyrill-tests && uv sync
```

### 2. Install Playwright Browsers

First time setup requires installing browser binaries:

```bash
cd pyrill-tests && uv run playwright install chromium
```

This downloads the Chromium browser binary used by Playwright.

## Running Tests

### Basic Validation (Default)

Run all browser tests in headless mode without screenshots:

```bash
cd pyrill-tests && uv run pytest tests/client/browser/ -v
```

### With Screenshots

Capture screenshots of successful page loads:

```bash
cd pyrill-tests && uv run pytest tests/client/browser/ --capture-screenshots -v
```

### Headed Mode (Visible Browser)

Run with a visible browser window for debugging:

```bash
cd pyrill-tests && uv run pytest tests/client/browser/ --headed -v
```

### Test Specific URLs

Run tests for URLs matching a specific pattern:

```bash
# Test only URLs with "complex_filter" in the name
cd pyrill-tests && uv run pytest tests/client/browser/ -k "complex_filter" -v

# Test only the known good/bad URL examples
cd pyrill-tests && uv run pytest tests/client/browser/test_url_validation.py::TestSpecificUrlValidation -v
```

### Custom Browser Timeout

Adjust the page load timeout (default: 30 seconds):

```bash
cd pyrill-tests && uv run pytest tests/client/browser/ --browser-timeout=60000 -v
```

### Run Only Browser Tests

Using the pytest marker:

```bash
cd pyrill-tests && uv run pytest -m browser -v
```

## Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--capture-screenshots` | Save screenshots of successful page loads | False |
| `--headed` | Run browser in headed mode (visible) | False (headless) |
| `--browser-timeout` | Page load timeout in milliseconds | 30000 (30 sec) |

## How It Works

### 1. URL Discovery

The tests automatically discover all URL fixture JSON files in:
```
tests/fixtures/query_results/object/urls/
```

Each fixture file contains:
- The generated URL string
- URL components
- Query metadata

### 2. Validation Process

For each URL, the test:
1. Loads the URL in an incognito browser context
2. Waits for the page to reach "networkidle" state
3. Checks for the 404 error indicator: `<h1 class="status-code svelte-h1ftig">404</h1>`
4. Optionally captures a screenshot
5. Reports success or failure

### 3. 404 Detection

The test checks for 404 errors by:
- Looking for the specific HTML element: `<h1 class="status-code svelte-h1ftig">404</h1>`
- Checking the page title for "404" or "not found"

If a 404 is detected, the test automatically captures a screenshot and fails.

## Screenshot Location

Screenshots are saved to:
```
tests/debug/screenshots/
```

This directory is **gitignored** to avoid version control bloat.

### Screenshot Naming Convention

```
{test_id}_{status}_{timestamp}.png
```

Examples:
- `metrics_basic_metrics_query_success_20251118_143052.png`
- `builder_query_builder_complex_filter_failure_20251118_143110.png`
- `known_bad_url_404_detected_20251118_143125.png`

## Test Structure

### `test_url_validation.py`

Contains two test classes:

#### `TestUrlValidation`
- Automatically discovers and tests all URL fixtures
- Parametrized tests (one test per URL)
- Validates no 404 errors

#### `TestSpecificUrlValidation`
- Manual tests for specific known URLs
- `test_good_url_example`: Tests a known valid URL
- `test_bad_url_example`: Tests a known invalid URL (verifies 404 detection works)

### `conftest.py`

Provides fixtures:
- `screenshot_dir`: Screenshot directory path
- `browser_config`: Configuration from command-line options
- Custom pytest options for browser testing

## Troubleshooting

### "Browser not installed" Error

Run:
```bash
cd pyrill-tests && uv run playwright install chromium
```

### Tests Timing Out

Increase the timeout:
```bash
cd pyrill-tests && uv run pytest tests/client/browser/ --browser-timeout=60000 -v
```

### Want to See What's Happening?

Use headed mode:
```bash
cd pyrill-tests && uv run pytest tests/client/browser/ --headed -v
```

### Need to Debug a Specific URL?

1. Run with headed mode and the specific test:
```bash
cd pyrill-tests && uv run pytest tests/client/browser/ -k "your_test_name" --headed -v
```

2. Check the screenshot:
```bash
ls -lh tests/debug/screenshots/
```

## Integration with Existing Tests

The browser tests complement the existing URL generation tests:

1. **URL Generation** (`tests/client/e2e/test_url_builder_e2e.py`)
   - Generates URLs from queries
   - Saves to fixture files

2. **Browser Validation** (`tests/client/browser/test_url_validation.py`)
   - Reads URL fixture files
   - Validates URLs in browser
   - Captures screenshots

## CI/CD Considerations

For continuous integration:

```bash
# Install browsers in CI
cd pyrill-tests && uv run playwright install --with-deps chromium

# Run tests in headless mode
cd pyrill-tests && uv run pytest tests/client/browser/ -v
```

The `--with-deps` flag installs system dependencies needed by the browser.

## Example Output

```
tests/client/browser/test_url_validation.py::TestUrlValidation::test_url_loads_without_404[metrics_basic_metrics_query]
================================================================================
Testing URL: metrics_basic_metrics_query
Fixture: basic_metrics_query.json
URL: https://ui.rilldata.com/demo/rill-openrtb-prog-ads/explore/bids_explore?tr=2025-11-15+to+2025-11-18&measures=overall_spend,total_bids,impressions,win_rate&dims=advertiser_name,device_type&sort_dir=DESC&sort_by=overall_spend&leaderboard_measures=overall_spend&grain=day
================================================================================
Loading page (timeout: 30000ms)...

✓ Page loaded successfully (no 404 error)
PASSED

tests/client/browser/test_url_validation.py::TestSpecificUrlValidation::test_bad_url_example
================================================================================
Testing KNOWN BAD URL (expect 404)
URL: https://ui.rilldata.com/demo/rill-openrtb-prog-ads/explore/bids_whatsit?tr=2025-11-12+to+2025-11-16&grain=day&measures=overall_spend%2Ctotal_bids%2Cimpressions%2Cclicks%2Cctr&dims=advertiser_name%2Cdevice_type%2Cdevice_region&leaderboard_measures=overall_spend%2Ctotal_bids%2Cimpressions%2Cclicks%2Cctr
================================================================================
Screenshot saved: /Users/jon/RillGitHub/pyrill-workspace/pyrill-tests/tests/debug/screenshots/known_bad_url_404_detected_20251118_143125.png
✓ 404 error correctly detected for bad URL
PASSED
```

## Best Practices

1. **Run browser tests separately from unit tests** - They're slower and require browser binaries
2. **Use `--capture-screenshots` selectively** - Screenshots can consume disk space
3. **Clean up old screenshots periodically** - They're not version controlled
4. **Use headed mode for debugging** - Visual feedback helps troubleshoot issues
5. **Test after URL generation changes** - Ensure URL structure changes don't break pages

## Related Files

- `tests/client/e2e/test_url_builder_e2e.py` - URL generation tests
- `tests/fixtures/query_results/object/urls/` - URL fixture files
- `pyrill/src/pyrill/url_builder.py` - UrlBuilder implementation
