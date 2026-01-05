"""
Report generation utilities for query test results

This module generates summary reports and README documentation from test result JSON files.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def generate_summary_and_readme(output_dir: Path, org: str | None = None, project: str | None = None, metrics_view: str | None = None):
    """
    Generate SUMMARY.json and README.md from test result JSON files.

    Args:
        output_dir: Directory containing test result JSON files (searches recursively)
        org: Organization name (extracted from JSON if not provided)
        project: Project name (extracted from JSON if not provided)
        metrics_view: Metrics view name (extracted from JSON if not provided)

    Returns:
        dict: Summary data structure
    """
    # Find all result files recursively
    result_files = list(output_dir.rglob("*.json"))
    # Exclude SUMMARY.json itself
    result_files = [f for f in result_files if f.name != "SUMMARY.json"]

    # Extract metadata from first result file if not provided
    if result_files and (not org or not project):
        with open(result_files[0]) as f:
            first_result = json.load(f)
            org = org or first_result.get("org")
            project = project or first_result.get("project")
            metrics_view = metrics_view or first_result.get("metrics_view")

    # Build summary structure
    summary = {
        "total_tests": len(result_files),
        "org": org,
        "project": project,
        "metrics_view": metrics_view,
        "results": []
    }

    for filepath in sorted(result_files):
        with open(filepath) as f:
            data = json.load(f)

            # Determine if this is an error file
            is_error = "_ERROR" in filepath.name or data.get("success") == False

            # Get relative path from output_dir for better file organization
            relative_path = filepath.relative_to(output_dir)

            summary["results"].append({
                "test_name": data.get("test_name"),
                "rows_returned": len(data.get("result", {}).get("data", [])) if not is_error else None,
                "file": str(relative_path),
                "description": data.get("metadata", {}).get("description"),
                "is_error": is_error,
                "error_message": data.get("error", {}).get("error_message") if is_error else None
            })

    # Write SUMMARY.json
    summary_path = output_dir / "SUMMARY.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Generate README.md from SUMMARY.json
    _generate_readme_from_summary(summary_path)

    # Print summary to console
    print(f"\n{'='*70}")
    print(f"QUERY TEST SUMMARY")
    print(f"{'='*70}")
    print(f"Results saved to: {output_dir}")
    print(f"Total tests run: {len(result_files)}")
    print(f"\nTest results:")
    for result in summary["results"]:
        status = "✗" if result["is_error"] else "✓"
        rows = result["rows_returned"] if result["rows_returned"] is not None else "ERROR"
        print(f"  {status} {result['test_name']}: {rows} rows")
        if result.get('description'):
            print(f"    {result['description']}")
    print(f"\nSummary report: {summary_path}")
    print(f"README: {output_dir / 'README.md'}")
    print(f"{'='*70}\n")

    return summary


def _generate_readme_from_summary(summary_path: Path):
    """
    Generate README.md from SUMMARY.json file.

    Args:
        summary_path: Path to SUMMARY.json file
    """
    with open(summary_path) as f:
        summary = json.load(f)

    # Count passed/failed
    passed_count = sum(1 for r in summary["results"] if not r["is_error"])
    failed_count = sum(1 for r in summary["results"] if r["is_error"])

    # Build README content
    readme_lines = [
        "# Query Test Results",
        "",
        f"**Organization:** {summary['org']}",
        f"**Project:** {summary['project']}",
        f"**Metrics View:** {summary['metrics_view']}",
        "",
        "## Overview",
        "",
        "This directory contains real API query results from end-to-end tests of the PyRill SDK query functionality. "
        f"All queries were executed against the live Rill Data API using the {summary['org']} organization's "
        f"{summary['project']} project.",
        "",
        f"**Location:** `tests/fixtures/query_results/`",
        "",
        "## Test Results Summary",
        "",
        f"### ✅ Test Results ({passed_count} passed, {failed_count} failed)",
        "",
        "| Test Name | Status | Rows | Description |",
        "|-----------|--------|------|-------------|",
    ]

    # Add table rows
    for result in summary["results"]:
        status = "❌ FAILED" if result["is_error"] else "✅ PASSED"
        rows = str(result["rows_returned"]) if result["rows_returned"] is not None else "-"
        description = result.get("description", "")
        test_name = result["test_name"]

        # If failed, append error message to description
        if result["is_error"] and result.get("error_message"):
            error_msg = result["error_message"]
            # Truncate long error messages
            if len(error_msg) > 80:
                error_msg = error_msg[:77] + "..."
            description = f"{description} ({error_msg})" if description else error_msg

        readme_lines.append(f"| {test_name} | {status} | {rows} | {description} |")

    readme_lines.extend([
        "",
        "## File Descriptions",
        "",
        "Each test produces a JSON file containing:",
        "- Query parameters used",
        "- Result data returned from API",
        "- Metadata about the test (description, timestamp, etc.)",
        "",
        "Files ending in `_ERROR.json` indicate tests that failed, and include error details.",
        "",
        "## Running Tests",
        "",
        "To regenerate these results, run the E2E tests:",
        "",
        "```bash",
        "cd /path/to/pyrill-tests",
        "export RILL_USER_TOKEN='rill_usr_...'",
        "uv run pytest tests/client/e2e/ --run-e2e -v",
        "```",
        "",
        "## Files",
        "",
    ])

    # List all files
    for result in summary["results"]:
        readme_lines.append(f"- `{result['file']}` - {result.get('description', result['test_name'])}")

    readme_lines.extend([
        "- `SUMMARY.json` - Machine-readable summary of all test results",
        "- `README.md` - This file",
        "",
    ])

    # Write README
    readme_path = summary_path.parent / "README.md"
    with open(readme_path, "w") as f:
        f.write("\n".join(readme_lines))
