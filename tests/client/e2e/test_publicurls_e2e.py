"""E2E tests for publicurls resource (read-only list operation)"""

import os
import json
import pytest
from pathlib import Path
from pyrill import RillClient
from pyrill.models import MagicAuthToken
from pyrill.exceptions import RillError
from tests.client.e2e.conftest import TEST_ORG, TEST_PROJECT


@pytest.mark.e2e
class TestE2EPublicUrls:
    """E2E tests for publicurls resource"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")
        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    @pytest.fixture(scope="class")
    def debug_dir(self):
        """Create debug directory for saving API responses"""
        # Path is relative to the test file location
        debug_path = Path(__file__).parent.parent.parent / "debug" / "publicurls"
        debug_path.mkdir(parents=True, exist_ok=True)
        print(f"Debug directory created at: {debug_path.absolute()}")
        return debug_path

    def test_list_publicurls_uses_defaults(self, client, debug_dir):
        """Test listing public URLs using client default org and project"""
        tokens = client.publicurls.list()

        assert isinstance(tokens, list)
        assert all(isinstance(t, MagicAuthToken) for t in tokens)

        # Validate structure if tokens exist
        if tokens:
            first_token = tokens[0]
            assert first_token.id is not None
            # Validate resources structure
            if first_token.resources:
                assert first_token.resources[0].type is not None
                assert first_token.resources[0].name is not None

        # Save response for manual review
        token_data = [t.model_dump() for t in tokens]
        (debug_dir / "list_publicurls_defaults.json").write_text(
            json.dumps(token_data, indent=2)
        )

        # Save summary
        summary = {
            "total_tokens": len(tokens),
            "token_ids": [t.id for t in tokens],
            "has_expired_tokens": any(t.expires_on for t in tokens),
            "has_display_names": any(t.display_name for t in tokens),
            "has_field_restrictions": any(t.fields for t in tokens),
            "resource_types": list(set(
                r.type for t in tokens for r in t.resources
            )) if tokens else []
        }
        (debug_dir / "list_publicurls_summary.json").write_text(
            json.dumps(summary, indent=2)
        )

    def test_list_publicurls_with_pagination(self, client, debug_dir):
        """Test listing public URLs with custom page size"""
        # Test with small page size
        tokens_page1 = client.publicurls.list(page_size=5)

        assert isinstance(tokens_page1, list)
        assert all(isinstance(t, MagicAuthToken) for t in tokens_page1)

        # Save response for manual review
        (debug_dir / "list_publicurls_pagination.json").write_text(
            json.dumps({
                "page_size": 5,
                "tokens_returned": len(tokens_page1),
                "tokens": [t.model_dump() for t in tokens_page1]
            }, indent=2)
        )

    @pytest.mark.xfail(reason="May fail with 403 if no permissions to access other project")
    def test_list_publicurls_override_project(self, client, debug_dir):
        """Test listing public URLs with explicit project override"""
        # Get first available project
        projects = client.projects.list()
        if not projects:
            pytest.skip("No projects available")

        test_project = projects[0].name

        try:
            tokens = client.publicurls.list(project=test_project)

            assert isinstance(tokens, list)
            assert all(isinstance(t, MagicAuthToken) for t in tokens)

            # Save response for manual review
            (debug_dir / "list_publicurls_override_project.json").write_text(
                json.dumps({
                    "project": test_project,
                    "token_count": len(tokens),
                    "tokens": [t.model_dump() for t in tokens]
                }, indent=2)
            )
        except RillError as e:
            error_info = {
                "error_type": type(e).__name__,
                "error_message": str(e),
                "test_project": test_project,
                "available_projects": [p.name for p in projects]
            }
            # Save error for manual review
            (debug_dir / "list_publicurls_override_project_error.json").write_text(
                json.dumps(error_info, indent=2)
            )
            raise

    def test_list_publicurls_model_validation(self, client, debug_dir):
        """Test that returned tokens have proper model structure"""
        tokens = client.publicurls.list()

        validation_results = {
            "total_tokens": len(tokens),
            "tokens_validated": []
        }

        for token in tokens:
            token_validation = {
                "id": token.id,
                "has_url": token.url is not None,
                "has_project_id": token.project_id is not None,
                "has_created_on": token.created_on is not None,
                "has_resources": len(token.resources) > 0 if token.resources else False,
                "resource_count": len(token.resources) if token.resources else 0,
                "has_fields": len(token.fields) > 0 if token.fields else False,
                "field_count": len(token.fields) if token.fields else 0,
                "has_display_name": token.display_name is not None,
                "has_expiry": token.expires_on is not None,
                "has_been_used": token.used_on is not None
            }
            validation_results["tokens_validated"].append(token_validation)

        # Save validation results for manual review
        (debug_dir / "list_publicurls_validation.json").write_text(
            json.dumps(validation_results, indent=2)
        )

        # Basic assertions
        if tokens:
            assert all(t.id is not None for t in tokens), "All tokens should have an ID"
            assert all(isinstance(t.resources, list) for t in tokens), "Resources should be a list"
            assert all(isinstance(t.fields, list) for t in tokens), "Fields should be a list"
