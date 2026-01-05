# URL Generation Test Results

This directory contains URLs generated from PyRill queries for inspection and validation.

## Overview

The E2E tests in `tests/client/e2e/test_url_builder_e2e.py` convert all MetricsQuery objects from `test_query_e2e.py` into Rill UI explore URLs using the `UrlBuilder` class.

## Running the Tests

To generate URL files, run the E2E tests with the `--run-e2e` flag:

```bash
cd pyrill-tests
export RILL_USER_TOKEN="your_token_here"
uv run pytest tests/client/e2e/test_url_builder_e2e.py --run-e2e -v -s
```

Note: While these tests don't make API calls, they're marked as E2E to match the pattern of the query tests they're based on.

## Directory Structure

```
urls/
├── metrics/          # URLs for basic metrics queries
│   ├── basic_metrics_query.json
│   ├── metrics_query_time_dimension.json
│   ├── metrics_query_with_filter.json
│   ├── metrics_query_iso_duration_time_range.json
│   ├── metrics_query_expression_time_range.json
│   └── metrics_query_complex_filter.json
├── builder/          # URLs for QueryBuilder-based queries
│   ├── query_builder_time_dimension.json
│   └── query_builder_complex_filter.json
└── variations/       # URLs demonstrating different UrlBuilder options
    ├── url_pivot_mode_standard.json
    ├── url_pivot_mode_pivot.json
    ├── url_leaderboard_multi.json
    ├── url_leaderboard_single.json
    ├── url_comparison_disabled.json
    ├── url_comparison_enabled.json
    └── url_timezone_*.json
```

## JSON File Format

Each JSON file contains:

```json
{
  "test_name": "basic_metrics_query",
  "org": "demo",
  "project": "rill-openrtb-prog-ads",
  "query": {
    // Full MetricsQuery object
  },
  "url": {
    "string": "https://ui.rilldata.com/...",
    "components": {
      "base_url": "https://ui.rilldata.com",
      "org": "demo",
      "project": "rill-openrtb-prog-ads",
      "metrics_view": "bids_metrics",
      "time_range": "2025-11-10 to 2025-11-13",
      "timezone": "UTC",
      "measures": ["overall_spend", "total_bids"],
      "dimensions": ["advertiser_name", "device_type"],
      "sort_dir": "DESC",
      "sort_by": "overall_spend",
      "leaderboard_measures": ["overall_spend", "total_bids"],
      "grain": "day",
      // ... other URL components
    }
  },
  "metadata": {
    "description": "Basic metrics query with advertiser and device dimensions",
    "expected_params": ["tr", "measures", "dims", "sort_dir", "sort_by"]
  }
}
```

## Test Coverage

The URL generation tests cover:

### Basic Metrics Queries
- **basic_metrics_query**: Simple query with dimensions and measures
- **metrics_query_time_dimension**: Time-series with computed time dimension
- **metrics_query_with_filter**: Query with WHERE clause (filter warning expected)
- **metrics_query_iso_duration_time_range**: ISO 8601 duration (P7D)
- **metrics_query_expression_time_range**: Expression-based time range
- **metrics_query_complex_filter**: Complex AND filter (filter warning expected)

### QueryBuilder Integration
- **query_builder_time_dimension**: Time-series via QueryBuilder
- **query_builder_complex_filter**: Complex filter via QueryBuilder

### UrlBuilder Variations
- **Pivot Mode**: Standard vs. pivot table view
- **Leaderboard**: All measures vs. first measure only
- **Comparison**: With and without prior period comparison
- **Timezones**: Multiple timezone variations

## URL Validation

To validate URLs:

1. **Copy URL from JSON file** (from `url.string` field)
2. **Paste into browser** to view in Rill UI
3. **Verify components match** the query parameters
4. **Check metadata** for expected warnings (e.g., filters not encoded)

## Known Limitations (v1.0)

The following query features are **not encoded** in URLs:
- ❌ WHERE clauses (logs warning, URL generated without filter)
- ❌ HAVING clauses (logs warning, URL generated without filter)
- ❌ query.comparison_time_range (use `enable_comparison` parameter instead)
- ❌ Subqueries
- ⚠️ Only first sort is used (multiple sorts ignored)

URLs with these features will include warnings in their metadata.

## Example Usage

### Inspect a Generated URL

```bash
# View the basic metrics query URL
cat urls/metrics/basic_metrics_query.json | jq '.url.string'

# View URL components
cat urls/metrics/basic_metrics_query.json | jq '.url.components'

# View metadata and warnings
cat urls/metrics/metrics_query_with_filter.json | jq '.metadata'
```

### Compare Standard vs. Pivot

```bash
# Standard explore view
cat urls/variations/url_pivot_mode_standard.json | jq '.url.string'

# Pivot table view
cat urls/variations/url_pivot_mode_pivot.json | jq '.url.string'
```

### Check Timezone Encoding

```bash
# See how timezones are URL-encoded
cat urls/variations/url_timezone_America_New_York.json | jq '.url.components.timezone'
cat urls/variations/url_timezone_America_New_York.json | jq '.url.string' | grep -o "tz=[^&]*"
```

## Regenerating URLs

To regenerate all URLs after making changes:

```bash
cd pyrill-tests

# Remove old results
rm -rf tests/fixtures/query_results/object/urls/*.json
rm -rf tests/fixtures/query_results/object/urls/*/

# Run tests to regenerate
export RILL_USER_TOKEN="your_token_here"
uv run pytest tests/client/e2e/test_url_builder_e2e.py --run-e2e -v -s
```

## Troubleshooting

### Tests Not Running
- Ensure `--run-e2e` flag is set
- Tests are marked with `@pytest.mark.e2e`

### URLs Look Wrong
- Check the metadata for warnings about unsupported features
- Compare with real Rill UI URLs to verify format
- Validate JSON structure matches expected format

### No Files Generated
- Verify output directory exists and is writable
- Check test output for error messages
- Ensure UrlBuilder is working correctly (run unit tests first)

## Related Documentation

- **UrlBuilder Implementation**: See `dev_plans/add-url-builder.md`
- **Query E2E Tests**: See `tests/client/e2e/test_query_e2e.py`
- **UrlBuilder Tests**: See `tests/client/unit/test_url_builder.py`
