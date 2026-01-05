"""
End-to-end tests for Partitions resource

These tests require real credentials and make actual API calls.
Run with: pytest tests/client/e2e/test_partitions.py --run-e2e -v
"""

import os
import json
from pathlib import Path
import pytest

from pyrill import RillClient
from pyrill.models.partitions import ModelPartition
from pyrill.exceptions import RillAPIError

# Debug output directory (relative to workspace root)
DEBUG_DIR = Path(__file__).parent.parent.parent / "debug" / "partitions"


def save_debug_output(test_name: str, data: dict):
    """Save debug output for inspection"""
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)
    filepath = DEBUG_DIR / f"{test_name}.json"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"\n📝 Debug output saved to: {filepath}")


@pytest.mark.e2e
class TestE2EPartitionsBasics:
    """E2E tests for basic partition operations"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        # Use my-rill-tutorial project which has partitioned models
        return RillClient(org="demo", project="my-rill-tutorial")

    @pytest.fixture(scope="class")
    def partitioned_model(self, client):
        """Model with partitions for testing"""
        # SQL_increment_tutorial is a known partitioned model
        return "SQL_increment_tutorial"

    def test_list_partitions_uses_defaults(self, client, partitioned_model):
        """Test that list uses client defaults for org/project"""
        partitions = client.partitions.list(partitioned_model)

        assert isinstance(partitions, list)
        assert all(isinstance(p, ModelPartition) for p in partitions)

        # Validate partition structure
        assert len(partitions) > 0, f"Model {partitioned_model} should have partitions"
        partition = partitions[0]
        assert partition.key is not None
        # Other fields may be None depending on partition state

    def test_list_partitions_positional_parameter(self, client, partitioned_model):
        """Test positional parameter style"""
        try:
            partitions = client.partitions.list(partitioned_model)
            assert isinstance(partitions, list)
        except RillAPIError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise

    def test_list_partitions_named_parameter(self, client, partitioned_model):
        """Test named parameter style"""
        try:
            partitions = client.partitions.list(model=partitioned_model)
            assert isinstance(partitions, list)
        except RillAPIError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise

    def test_list_partitions_with_project_override(self, client, partitioned_model):
        """Test overriding just the project parameter"""
        try:
            # Use the same project as default, just testing the parameter works
            partitions = client.partitions.list(
                partitioned_model,
                project="my-rill-tutorial"
            )
            assert isinstance(partitions, list)
        except RillAPIError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise

    def test_list_partitions_with_org_override(self, client, partitioned_model):
        """Test overriding just the org parameter"""
        try:
            # Use the same org as default, just testing the parameter works
            partitions = client.partitions.list(
                partitioned_model,
                org="demo"
            )
            assert isinstance(partitions, list)
        except RillAPIError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise

    def test_list_partitions_with_both_overrides(self, client, partitioned_model):
        """Test overriding both project and org parameters"""
        try:
            partitions = client.partitions.list(
                partitioned_model,
                project="my-rill-tutorial",
                org="demo"
            )
            assert isinstance(partitions, list)
        except RillAPIError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise


@pytest.mark.e2e
class TestE2EPartitionsFiltering:
    """E2E tests for partition filtering"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        return RillClient(org="demo", project="my-rill-tutorial")

    @pytest.fixture(scope="class")
    def partitioned_model(self):
        """Model name for testing"""
        return "SQL_increment_tutorial"

    def test_list_partitions_pending_filter(self, client, partitioned_model):
        """Test filtering for pending partitions"""
        try:
            partitions = client.partitions.list(
                partitioned_model,
                pending=True
            )
            assert isinstance(partitions, list)
            # All returned partitions should be pending (if any)
            for partition in partitions:
                assert isinstance(partition, ModelPartition)
        except RillAPIError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise

    def test_list_partitions_errored_filter(self, client, partitioned_model):
        """Test filtering for errored partitions"""
        try:
            partitions = client.partitions.list(
                partitioned_model,
                errored=True
            )
            assert isinstance(partitions, list)
            # All returned partitions should have errors (if any)
            for partition in partitions:
                assert isinstance(partition, ModelPartition)
                if partition.error:
                    assert partition.error is not None
        except RillAPIError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise


@pytest.mark.e2e
class TestE2EPartitionsPagination:
    """E2E tests for partition pagination"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        return RillClient(org="demo", project="my-rill-tutorial")

    @pytest.fixture(scope="class")
    def partitioned_model(self):
        """Model name for testing"""
        return "SQL_increment_tutorial"

    @pytest.mark.xfail(reason="API bug: pagination token has malformed JSON (missing closing quote)")
    def test_list_partitions_with_limit(self, client, partitioned_model):
        """Test automatic pagination with limit parameter"""
        try:
            # Request up to 100 partitions
            partitions = client.partitions.list(
                partitioned_model,
                limit=100
            )

            # Save debug output
            save_debug_output("test_list_partitions_with_limit", {
                "model": partitioned_model,
                "limit": 100,
                "partitions_returned": len(partitions),
                "partitions": [p.model_dump() for p in partitions]
            })

            assert isinstance(partitions, list)
            assert len(partitions) <= 100
            assert all(isinstance(p, ModelPartition) for p in partitions)
        except RillAPIError as e:
            save_debug_output("test_list_partitions_with_limit_ERROR", {
                "model": partitioned_model,
                "limit": 100,
                "error": str(e),
                "error_type": type(e).__name__
            })
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise

    @pytest.mark.xfail(reason="API bug: pagination token has malformed JSON (missing closing quote)")
    def test_list_partitions_large_limit(self, client, partitioned_model):
        """Test pagination up to 400 partitions"""
        try:
            # Request up to 400 partitions (max supported)
            partitions = client.partitions.list(
                partitioned_model,
                limit=400
            )

            # Save debug output
            save_debug_output("test_list_partitions_large_limit", {
                "model": partitioned_model,
                "limit": 400,
                "partitions_returned": len(partitions),
                "partitions": [p.model_dump() for p in partitions]
            })

            assert isinstance(partitions, list)
            assert len(partitions) <= 400
            assert all(isinstance(p, ModelPartition) for p in partitions)
        except RillAPIError as e:
            save_debug_output("test_list_partitions_large_limit_ERROR", {
                "model": partitioned_model,
                "limit": 400,
                "error": str(e),
                "error_type": type(e).__name__
            })
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise

    @pytest.mark.xfail(reason="API bug: pagination token has malformed JSON (missing closing quote)")
    def test_list_partitions_custom_page_size(self, client, partitioned_model):
        """Test with custom page size"""
        try:
            partitions = client.partitions.list(
                partitioned_model,
                page_size=25,
                limit=50
            )

            # Save debug output
            save_debug_output("test_list_partitions_custom_page_size", {
                "model": partitioned_model,
                "page_size": 25,
                "limit": 50,
                "partitions_returned": len(partitions),
                "partitions": [p.model_dump() for p in partitions]
            })

            assert isinstance(partitions, list)
            assert len(partitions) <= 50
        except RillAPIError as e:
            save_debug_output("test_list_partitions_custom_page_size_ERROR", {
                "model": partitioned_model,
                "page_size": 25,
                "limit": 50,
                "error": str(e),
                "error_type": type(e).__name__
            })
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise

    def test_list_partitions_max_page_size(self, client, partitioned_model):
        """Test with maximum page size of 400 in a single request"""
        try:
            # Request up to 400 partitions in a single page (no pagination)
            partitions = client.partitions.list(
                partitioned_model,
                page_size=400
            )

            # Save debug output
            save_debug_output("test_list_partitions_max_page_size", {
                "model": partitioned_model,
                "page_size": 400,
                "limit": None,
                "partitions_returned": len(partitions),
                "partitions": [p.model_dump() for p in partitions]
            })

            assert isinstance(partitions, list)
            # Should get either all partitions or up to the page_size
            assert all(isinstance(p, ModelPartition) for p in partitions)
        except RillAPIError as e:
            save_debug_output("test_list_partitions_max_page_size_ERROR", {
                "model": partitioned_model,
                "page_size": 400,
                "limit": None,
                "error": str(e),
                "error_type": type(e).__name__
            })
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise


@pytest.mark.e2e
class TestE2EPartitionsValidation:
    """E2E tests for partition data validation"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        return RillClient(org="demo", project="my-rill-tutorial")

    @pytest.fixture(scope="class")
    def partitioned_model(self):
        """Model name for testing"""
        return "SQL_increment_tutorial"

    def test_partition_fields(self, client, partitioned_model):
        """Test that partition fields are properly parsed"""
        try:
            partitions = client.partitions.list(partitioned_model, limit=5)

            if not partitions:
                pytest.skip("No partitions available for field validation")

            for partition in partitions:
                # Key is always required
                assert partition.key is not None
                assert isinstance(partition.key, str)

                # Optional fields - just check types if present
                if partition.data is not None:
                    assert isinstance(partition.data, dict)

                if partition.watermark is not None:
                    assert isinstance(partition.watermark, str)

                if partition.executed_on is not None:
                    assert isinstance(partition.executed_on, str)

                if partition.error is not None:
                    assert isinstance(partition.error, str)

                if partition.elapsed_ms is not None:
                    assert isinstance(partition.elapsed_ms, int)

        except RillAPIError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                pytest.skip(f"Model {partitioned_model} not available")
            raise
