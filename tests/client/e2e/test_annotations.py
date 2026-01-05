"""
End-to-end tests for Annotations resource

These tests require real credentials and make actual API calls.
Run with: pytest tests/client/e2e/test_annotations.py --run-e2e -v
"""

import os
import json
import pytest
from pathlib import Path

from pyrill import RillClient
from pyrill.models.annotations import (
    Annotation,
    AnnotationsQuery,
    AnnotationsResponse,
)
from pyrill.models.query import TimeRange, TimeGrain
from pyrill.exceptions import RillError
from tests.client.e2e.conftest import TEST_ORG, TEST_PROJECT

# Debug output directory
DEBUG_DIR = Path(__file__).parent.parent.parent / "debug" / "annotations"


def save_debug_output(test_name: str, data: dict):
    """Save debug output for inspection"""
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DEBUG_DIR / f"{test_name}.json"
    filepath.write_text(json.dumps(data, indent=2, default=str))
    print(f"\n📝 Debug output saved to: {filepath}")


@pytest.mark.e2e
class TestE2EAnnotations:
    """E2E tests for annotations query operations"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    @pytest.fixture(scope="class")
    def debug_dir(self):
        """Create debug directory for saving API responses"""
        # Ensure debug directory exists
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Debug directory created at: {DEBUG_DIR.absolute()}")
        return DEBUG_DIR

    def test_query_annotations_basic(self, client, debug_dir):
        """Test querying annotations for a metrics view"""
        print("\n" + "="*80)
        print("TEST: Query Annotations (Basic)")
        print("="*80)

        # Create a basic query without time_range (will return all annotations)
        query = AnnotationsQuery(
            measures=["requests"],
            limit=100
        )

        print(f"Querying annotations for metrics view: auction_metrics")
        print(f"Measures: {query.measures}")
        print(f"Time Range: None (all annotations)")
        print(f"Limit: {query.limit}")

        result = client.annotations.query("auction_metrics", query)

        assert isinstance(result, AnnotationsResponse), f"Expected AnnotationsResponse, got {type(result)}"
        assert hasattr(result, "rows"), "Response should have 'rows' attribute"

        print(f"✅ Got {len(result.rows) if result.rows else 0} annotations")

        # Save debug output
        annotations_data = []
        if result.rows:
            assert isinstance(result.rows, list), f"Expected rows to be list, got {type(result.rows)}"
            assert all(isinstance(ann, Annotation) for ann in result.rows), "Not all rows are Annotation instances"

            for ann in result.rows:
                ann_dict = {
                    "time": ann.time,
                    "time_end": ann.time_end,
                    "description": ann.description,
                    "duration": ann.duration,
                    "for_measures": ann.for_measures,
                    "additional_fields": ann.additional_fields
                }
                annotations_data.append(ann_dict)
                print(f"  • {ann.time}: {ann.description}")
                if ann.for_measures:
                    print(f"    For measures: {', '.join(ann.for_measures)}")

        # Build API call info for debugging
        org_name = client.config.default_org
        project_name = client.config.default_project
        endpoint = f"organizations/{org_name}/projects/{project_name}/runtime/queries/metrics-views/auction_metrics/annotations"

        save_debug_output("test_query_annotations_basic", {
            "test": "query_annotations_basic",
            "api_call": {
                "method": "POST",
                "endpoint": endpoint,
                "base_url": "https://api.rilldata.com/v1/",
                "full_url": f"https://api.rilldata.com/v1/{endpoint}",
                "org": org_name,
                "project": project_name
            },
            "request": {
                "metrics_view": "auction_metrics",
                "query_params": {
                    "measures": query.measures,
                    "time_range": query.time_range.expression if query.time_range else None,
                    "time_grain": query.time_grain.value if query.time_grain else None,
                    "limit": query.limit
                }
            },
            "response": {
                "count": len(result.rows) if result.rows else 0,
                "annotations": annotations_data
            }
        })

        # Verify response structure (may have 0 or more annotations)
        assert result.rows is not None, "Expected rows to not be None"
        print(f"Note: Found {len(result.rows)} annotations (may be 0 if none configured)")

        # Verify first annotation structure
        if result.rows:
            ann = result.rows[0]
            assert hasattr(ann, "time"), "Annotation should have 'time' attribute"
            assert hasattr(ann, "description"), "Annotation should have 'description' attribute"

    def test_query_annotations_with_time_grain(self, client, debug_dir):
        """Test querying annotations with time grain"""
        print("\n" + "="*80)
        print("TEST: Query Annotations (With Time Grain)")
        print("="*80)

        query = AnnotationsQuery(
            measures=["requests"],
            time_grain=TimeGrain.DAY,
            limit=50
        )

        print(f"Querying annotations with time grain: {query.time_grain}")
        print(f"Time Range: None (all annotations)")

        result = client.annotations.query("auction_metrics", query)

        assert isinstance(result, AnnotationsResponse)
        print(f"✅ Got {len(result.rows) if result.rows else 0} annotations")

        # Save debug output
        annotations_data = []
        if result.rows:
            for ann in result.rows:
                annotations_data.append({
                    "time": ann.time,
                    "description": ann.description,
                    "duration": ann.duration,
                })
                print(f"  • {ann.time}: {ann.description}")

        # Build API call info for debugging
        org_name = client.config.default_org
        project_name = client.config.default_project
        endpoint = f"organizations/{org_name}/projects/{project_name}/runtime/queries/metrics-views/auction_metrics/annotations"

        save_debug_output("test_query_annotations_with_time_grain", {
            "test": "query_annotations_with_time_grain",
            "api_call": {
                "method": "POST",
                "endpoint": endpoint,
                "base_url": "https://api.rilldata.com/v1/",
                "full_url": f"https://api.rilldata.com/v1/{endpoint}",
                "org": org_name,
                "project": project_name
            },
            "request": {
                "metrics_view": "auction_metrics",
                "query_params": {
                    "measures": query.measures,
                    "time_range": query.time_range.expression if query.time_range else None,
                    "time_grain": query.time_grain.value if query.time_grain else None,
                    "limit": query.limit
                }
            },
            "response": {
                "count": len(result.rows) if result.rows else 0,
                "annotations": annotations_data
            }
        })

    def test_query_annotations_nonexistent_metrics_view(self, client, debug_dir):
        """Test querying annotations for non-existent metrics view raises error"""
        print("\n" + "="*80)
        print("TEST: Query Annotations (Nonexistent Metrics View)")
        print("="*80)

        query = AnnotationsQuery(
            measures=["some_measure"],
            limit=10
        )

        nonexistent_view = "nonexistent-metrics-view-12345"
        print(f"Attempting to query nonexistent metrics view: {nonexistent_view}")

        with pytest.raises(RillError) as exc_info:
            client.annotations.query(nonexistent_view, query)

        error_msg = str(exc_info.value)
        print(f"✅ Got expected error: {error_msg}")

        # Build API call info for debugging
        org_name = client.config.default_org
        project_name = client.config.default_project
        endpoint = f"organizations/{org_name}/projects/{project_name}/runtime/queries/metrics-views/{nonexistent_view}/annotations"

        save_debug_output("test_query_annotations_nonexistent", {
            "test": "query_annotations_nonexistent",
            "api_call": {
                "method": "POST",
                "endpoint": endpoint,
                "base_url": "https://api.rilldata.com/v1/",
                "full_url": f"https://api.rilldata.com/v1/{endpoint}",
                "org": org_name,
                "project": project_name
            },
            "request": {
                "metrics_view": nonexistent_view,
                "query_params": {
                    "measures": query.measures,
                    "time_range": query.time_range.expression if query.time_range else None,
                    "limit": query.limit
                }
            },
            "response": {
                "error": error_msg
            }
        })

    def test_query_annotations_with_dict(self, client, debug_dir):
        """Test that query method accepts dict input"""
        print("\n" + "="*80)
        print("TEST: Query Annotations (Dict Input)")
        print("="*80)

        # Test the convenience feature of accepting dicts
        query_dict = {
            "measures": ["requests"],
            "limit": 10
        }

        print(f"Querying with dict input: {query_dict}")

        result = client.annotations.query("auction_metrics", query_dict)

        assert isinstance(result, AnnotationsResponse)
        print(f"✅ Query with dict succeeded, got {len(result.rows) if result.rows else 0} annotations")

        # Build API call info for debugging
        org_name = client.config.default_org
        project_name = client.config.default_project
        endpoint = f"organizations/{org_name}/projects/{project_name}/runtime/queries/metrics-views/auction_metrics/annotations"

        save_debug_output("test_query_annotations_with_dict", {
            "test": "query_annotations_with_dict",
            "api_call": {
                "method": "POST",
                "endpoint": endpoint,
                "base_url": "https://api.rilldata.com/v1/",
                "full_url": f"https://api.rilldata.com/v1/{endpoint}",
                "org": org_name,
                "project": project_name
            },
            "request": {
                "metrics_view": "auction_metrics",
                "query_params": query_dict
            },
            "response": {
                "count": len(result.rows) if result.rows else 0
            }
        })
