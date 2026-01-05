# Query Test Results

**Organization:** demo
**Project:** rill-openrtb-prog-ads
**Metrics View:** None

## Overview

This directory contains real API query results from end-to-end tests of the PyRill SDK query functionality. All queries were executed against the live Rill Data API using the demo organization's rill-openrtb-prog-ads project.

**Location:** `tests/fixtures/query_results/`

## Test Results Summary

### ✅ Test Results (34 passed, 0 failed)

| Test Name | Status | Rows | Description |
|-----------|--------|------|-------------|
| basic_metrics_query_dict | ✅ PASSED | 20 | Basic metrics query using plain Python dict |
| complex_metrics_query_dict | ✅ PASSED | 50 | Complex query with time_floor and filters using dict |
| metrics_query_complex_and_filter_dict | ✅ PASSED | 19 | Complex AND filter using dict |
| metrics_sql_query_dict | ✅ PASSED | 20 | Metrics SQL query using plain Python dict - queries pre-aggregated metrics view |
| sql_query_dict | ✅ PASSED | 1 | Raw SQL query using plain Python dict |
| query_builder_complex_filter | ✅ PASSED | 0 | QueryBuilder: Mobile campaigns in US, GB, CA regions |
| query_builder_time_dimension | ✅ PASSED | 100 | QueryBuilder: Time-series query with daily granularity by advertiser |
| basic_metrics_query | ✅ PASSED | 20 | Basic metrics query with advertiser and device dimensions |
| metrics_query_complex_filter | ✅ PASSED | 0 | Mobile campaigns in US, GB, CA regions |
| metrics_query_expression_time_range | ✅ PASSED | 25 | Video performance metrics using expression parameter |
| metrics_query_iso_duration_time_range | ✅ PASSED | 25 | Video performance metrics over last 7 days using iso_duration parameter |
| metrics_query_time_dimension | ✅ PASSED | 100 | Time-series query with daily granularity by advertiser |
| metrics_query_with_filter | ✅ PASSED | 0 | Mobile device campaigns sorted by spend |
| basic_metrics_sql | ✅ PASSED | 20 | Metrics SQL query - queries pre-aggregated metrics view |
| basic_sql_query | ✅ PASSED | 1 | Dataset summary statistics |
| EXAMPLE_basic_metrics_query | ✅ PASSED | 0 | EXAMPLE: Basic metrics query with advertiser and device dimensions |
| query_builder_complex_filter | ✅ PASSED | 0 | QueryBuilder: Mobile campaigns in US, GB, CA regions |
| query_builder_time_dimension | ✅ PASSED | 0 | QueryBuilder: Time-series query with daily granularity by advertiser |
| basic_metrics_query | ✅ PASSED | 0 | Basic metrics query with advertiser and device dimensions |
| metrics_query_complex_filter | ✅ PASSED | 0 | Mobile campaigns in US, GB, CA regions |
| metrics_query_expression_time_range | ✅ PASSED | 0 | Video performance metrics using expression parameter |
| metrics_query_iso_duration_time_range | ✅ PASSED | 0 | Video performance metrics over last 7 days using iso_duration |
| metrics_query_time_dimension | ✅ PASSED | 0 | Time-series query with daily granularity by advertiser |
| metrics_query_with_filter | ✅ PASSED | 0 | Mobile device campaigns sorted by spend |
| url_comparison_disabled | ✅ PASSED | 0 | URL without comparison |
| url_comparison_enabled | ✅ PASSED | 0 | URL with prior period comparison |
| url_leaderboard_multi | ✅ PASSED | 0 | All measures in leaderboard |
| url_leaderboard_single | ✅ PASSED | 0 | Only first measure in leaderboard |
| url_pivot_mode_pivot | ✅ PASSED | 0 | Pivot table view of same query |
| url_pivot_mode_standard | ✅ PASSED | 0 | Standard explore view (for comparison with pivot) |
| url_timezone_America_New_York | ✅ PASSED | 0 | URL with Eastern Time timezone |
| url_timezone_Asia_Tokyo | ✅ PASSED | 0 | URL with Japan Time timezone |
| url_timezone_Europe_London | ✅ PASSED | 0 | URL with British Time timezone |
| url_timezone_UTC | ✅ PASSED | 0 | URL with Coordinated Universal Time timezone |

## File Descriptions

Each test produces a JSON file containing:
- Query parameters used
- Result data returned from API
- Metadata about the test (description, timestamp, etc.)

Files ending in `_ERROR.json` indicate tests that failed, and include error details.

## Running Tests

To regenerate these results, run the E2E tests:

```bash
cd /path/to/pyrill-tests
export RILL_USER_TOKEN='rill_usr_...'
uv run pytest tests/client/e2e/ --run-e2e -v
```

## Files

- `dict/metrics/basic_metrics_query_dict.json` - Basic metrics query using plain Python dict
- `dict/metrics/complex_metrics_query_dict.json` - Complex query with time_floor and filters using dict
- `dict/metrics/metrics_query_complex_and_filter_dict.json` - Complex AND filter using dict
- `dict/metrics_sql/metrics_sql_query_dict.json` - Metrics SQL query using plain Python dict - queries pre-aggregated metrics view
- `dict/sql/sql_query_dict.json` - Raw SQL query using plain Python dict
- `object/builder/query_builder_complex_filter.json` - QueryBuilder: Mobile campaigns in US, GB, CA regions
- `object/builder/query_builder_time_dimension.json` - QueryBuilder: Time-series query with daily granularity by advertiser
- `object/metrics/basic_metrics_query.json` - Basic metrics query with advertiser and device dimensions
- `object/metrics/metrics_query_complex_filter.json` - Mobile campaigns in US, GB, CA regions
- `object/metrics/metrics_query_expression_time_range.json` - Video performance metrics using expression parameter
- `object/metrics/metrics_query_iso_duration_time_range.json` - Video performance metrics over last 7 days using iso_duration parameter
- `object/metrics/metrics_query_time_dimension.json` - Time-series query with daily granularity by advertiser
- `object/metrics/metrics_query_with_filter.json` - Mobile device campaigns sorted by spend
- `object/metrics_sql/basic_metrics_sql.json` - Metrics SQL query - queries pre-aggregated metrics view
- `object/sql/basic_sql_query.json` - Dataset summary statistics
- `object/urls/EXAMPLE.json` - EXAMPLE: Basic metrics query with advertiser and device dimensions
- `object/urls/builder/query_builder_complex_filter.json` - QueryBuilder: Mobile campaigns in US, GB, CA regions
- `object/urls/builder/query_builder_time_dimension.json` - QueryBuilder: Time-series query with daily granularity by advertiser
- `object/urls/metrics/basic_metrics_query.json` - Basic metrics query with advertiser and device dimensions
- `object/urls/metrics/metrics_query_complex_filter.json` - Mobile campaigns in US, GB, CA regions
- `object/urls/metrics/metrics_query_expression_time_range.json` - Video performance metrics using expression parameter
- `object/urls/metrics/metrics_query_iso_duration_time_range.json` - Video performance metrics over last 7 days using iso_duration
- `object/urls/metrics/metrics_query_time_dimension.json` - Time-series query with daily granularity by advertiser
- `object/urls/metrics/metrics_query_with_filter.json` - Mobile device campaigns sorted by spend
- `object/urls/variations/url_comparison_disabled.json` - URL without comparison
- `object/urls/variations/url_comparison_enabled.json` - URL with prior period comparison
- `object/urls/variations/url_leaderboard_multi.json` - All measures in leaderboard
- `object/urls/variations/url_leaderboard_single.json` - Only first measure in leaderboard
- `object/urls/variations/url_pivot_mode_pivot.json` - Pivot table view of same query
- `object/urls/variations/url_pivot_mode_standard.json` - Standard explore view (for comparison with pivot)
- `object/urls/variations/url_timezone_America_New_York.json` - URL with Eastern Time timezone
- `object/urls/variations/url_timezone_Asia_Tokyo.json` - URL with Japan Time timezone
- `object/urls/variations/url_timezone_Europe_London.json` - URL with British Time timezone
- `object/urls/variations/url_timezone_UTC.json` - URL with Coordinated Universal Time timezone
- `SUMMARY.json` - Machine-readable summary of all test results
- `README.md` - This file
