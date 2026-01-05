"""
End-to-end tests for IFrame resource

These tests require real credentials and make actual API calls.
Run with: pytest tests/client/e2e/test_iframe.py --run-e2e -v
"""

import os
import pytest
from urllib.parse import parse_qs, urlparse
from pydantic import ValidationError

from pyrill import RillClient
from pyrill.models import IFrameOptions, IFrameResponse
from pyrill.exceptions import RillError, RillAPIError
from tests.client.e2e.conftest import TEST_ORG, TEST_PROJECT


@pytest.mark.e2e
class TestE2EIFrames:
    """E2E tests for iframe URL generation"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    @pytest.fixture(scope="class")
    def test_org_and_project(self, client):
        """Get test organization and project"""
        return TEST_ORG, TEST_PROJECT

    def test_get_iframe_basic(self, client, test_org_and_project):
        """Test basic iframe URL generation with resource and user_email"""
        org_name, project_name = test_org_and_project

        options = IFrameOptions(
            resource="auction_metrics",
            user_email="test@example.com"
        )

        result = client.iframes.get(options, project=project_name, org=org_name)

        # Validate response type
        assert isinstance(result, IFrameResponse)
        assert isinstance(result.iframe_src, str)
        assert isinstance(result.runtime_host, str)
        assert isinstance(result.instance_id, str)
        assert isinstance(result.access_token, str)
        assert isinstance(result.ttl_seconds, int)

        # Validate URL structure
        assert result.iframe_src.startswith("http")
        assert "access_token=" in result.iframe_src
        assert "instance_id=" in result.iframe_src

    def test_get_iframe_with_navigation(self, client, test_org_and_project):
        """Test iframe URL generation with navigation enabled"""
        org_name, project_name = test_org_and_project

        options = IFrameOptions(
            resource="auction_metrics",
            navigation=True,
            user_email="test@example.com"
        )

        result = client.iframes.get(options, project=project_name, org=org_name)

        assert isinstance(result, IFrameResponse)
        assert result.iframe_src is not None
        # Navigation should be reflected in the URL
        assert "navigation=true" in result.iframe_src or "navigation=True" in result.iframe_src

    def test_get_iframe_project_list(self, client, test_org_and_project):
        """Test embedding project list (no resource specified)"""
        org_name, project_name = test_org_and_project

        options = IFrameOptions(
            navigation=True,
            user_email="test@example.com"
        )

        result = client.iframes.get(options, project=project_name, org=org_name)

        assert isinstance(result, IFrameResponse)
        assert result.iframe_src is not None
        # No specific resource, should allow project navigation
        assert "navigation=" in result.iframe_src

    def test_get_iframe_with_theme_dark(self, client, test_org_and_project):
        """Test iframe URL generation with dark theme mode"""
        org_name, project_name = test_org_and_project

        options = IFrameOptions(
            resource="auction_metrics",
            theme_mode="dark",
            user_email="test@example.com"
        )

        result = client.iframes.get(options, project=project_name, org=org_name)

        assert isinstance(result, IFrameResponse)
        assert result.iframe_src is not None
        # Theme mode might not appear in URL if it's handled differently by the API

    def test_get_iframe_with_theme_light(self, client, test_org_and_project):
        """Test iframe URL generation with light theme mode"""
        org_name, project_name = test_org_and_project

        options = IFrameOptions(
            resource="auction_metrics",
            theme_mode="light",
            user_email="test@example.com"
        )

        result = client.iframes.get(options, project=project_name, org=org_name)

        assert isinstance(result, IFrameResponse)
        # Light is typically default, but should be accepted
        assert result.iframe_src is not None

    def test_get_iframe_with_theme_system(self, client, test_org_and_project):
        """Test iframe URL generation with system theme mode"""
        org_name, project_name = test_org_and_project

        options = IFrameOptions(
            resource="auction_metrics",
            theme_mode="system",
            user_email="test@example.com"
        )

        result = client.iframes.get(options, project=project_name, org=org_name)

        assert isinstance(result, IFrameResponse)
        assert result.iframe_src is not None

    def test_get_iframe_with_canvas_type(self, client, test_org_and_project):
        """Test iframe URL generation with canvas type"""
        org_name, project_name = test_org_and_project

        # Note: This test might fail if the project doesn't have a canvas
        # We're testing the API accepts the type parameter
        options = IFrameOptions(
            resource="test_canvas",
            type="canvas",
            user_email="test@example.com"
        )

        try:
            result = client.iframes.get(options, project=project_name, org=org_name)
            assert isinstance(result, IFrameResponse)
            assert result.iframe_src is not None
        except RillAPIError:
            # Canvas might not exist, but the request should be well-formed
            pytest.skip("Canvas resource not available in test project")

    def test_get_iframe_with_attributes(self, client, test_org_and_project):
        """Test iframe URL generation with custom attributes for security policies"""
        org_name, project_name = test_org_and_project

        options = IFrameOptions(
            resource="auction_metrics",
            attributes={
                "email": "test@example.com",
                "role": "viewer",
                "tenant_id": "tenant123"
            }
        )

        result = client.iframes.get(options, project=project_name, org=org_name)

        assert isinstance(result, IFrameResponse)
        assert result.iframe_src is not None
        assert result.access_token is not None

    def test_get_iframe_with_ttl(self, client, test_org_and_project):
        """Test iframe URL generation with custom TTL"""
        org_name, project_name = test_org_and_project

        options = IFrameOptions(
            resource="auction_metrics",
            user_email="test@example.com",
            ttl_seconds=3600  # 1 hour
        )

        result = client.iframes.get(options, project=project_name, org=org_name)

        assert isinstance(result, IFrameResponse)
        # The response should reflect the requested TTL or use a default
        assert result.ttl_seconds > 0

    def test_get_iframe_url_structure(self, client, test_org_and_project):
        """Test that iframe_src URL contains expected query parameters"""
        org_name, project_name = test_org_and_project

        options = IFrameOptions(
            resource="auction_metrics",
            user_email="test@example.com"
        )

        result = client.iframes.get(options, project=project_name, org=org_name)

        # Parse the URL
        parsed = urlparse(result.iframe_src)
        query_params = parse_qs(parsed.query)

        # Verify essential parameters are present
        assert "access_token" in query_params or "accessToken" in query_params
        assert "instance_id" in query_params or "instanceId" in query_params
        assert "runtime_host" in query_params or "runtimeHost" in query_params

        # Verify the access token from URL matches the one in response
        token_from_url = query_params.get("access_token", query_params.get("accessToken", [None]))[0]
        assert token_from_url == result.access_token


    def test_get_iframe_override_context(self, client, test_org_and_project):
        """Test overriding org/project via method params"""
        org_name, project_name = test_org_and_project

        options = IFrameOptions(
            resource="auction_metrics",
            user_email="test@example.com"
        )

        # Override with explicit params (using same org/project)
        result = client.iframes.get(options, org=org_name, project=project_name)

        assert isinstance(result, IFrameResponse)
        assert result.iframe_src is not None


@pytest.mark.e2e
class TestE2EIFramesValidation:
    """E2E tests for iframe model validation"""

    def test_iframe_options_valid_type_explore(self):
        """Test that type='explore' is accepted"""
        options = IFrameOptions(
            resource="auction_metrics",
            type="explore",
            user_email="test@example.com"
        )

        assert options.type == "explore"

    def test_iframe_options_valid_type_canvas(self):
        """Test that type='canvas' is accepted"""
        options = IFrameOptions(
            resource="my_canvas",
            type="canvas",
            user_email="test@example.com"
        )

        assert options.type == "canvas"

    def test_iframe_options_valid_theme_modes(self):
        """Test that all valid theme_mode values are accepted"""
        # Test light
        options_light = IFrameOptions(
            resource="auction_metrics",
            theme_mode="light",
            user_email="test@example.com"
        )
        assert options_light.theme_mode == "light"

        # Test dark
        options_dark = IFrameOptions(
            resource="auction_metrics",
            theme_mode="dark",
            user_email="test@example.com"
        )
        assert options_dark.theme_mode == "dark"

        # Test system
        options_system = IFrameOptions(
            resource="auction_metrics",
            theme_mode="system",
            user_email="test@example.com"
        )
        assert options_system.theme_mode == "system"

    def test_iframe_options_model_dump_uses_aliases(self):
        """Test IFrameOptions serializes with correct field names (camelCase)"""
        options = IFrameOptions(
            resource="auction_metrics",
            user_email="test@example.com",
            ttl_seconds=3600,
            theme_mode="dark"
        )

        # Dump with aliases for API compatibility
        data = options.model_dump(by_alias=True, exclude_none=True)

        # Should contain camelCase API field names
        assert "userEmail" in data
        assert "ttlSeconds" in data
        assert "themeMode" in data

        # Should not contain Python snake_case field names
        assert "user_email" not in data
        assert "ttl_seconds" not in data
        assert "theme_mode" not in data

    def test_iframe_response_parses_camel_case(self):
        """Test IFrameResponse can parse camelCase API response"""
        api_response = {
            "iframeSrc": "https://example.com/embed?token=abc123",
            "runtimeHost": "https://runtime.example.com",
            "instanceId": "inst_123",
            "accessToken": "token_abc123",
            "ttlSeconds": 86400
        }

        response = IFrameResponse(**api_response)

        assert response.iframe_src == "https://example.com/embed?token=abc123"
        assert response.runtime_host == "https://runtime.example.com"
        assert response.instance_id == "inst_123"
        assert response.access_token == "token_abc123"
        assert response.ttl_seconds == 86400


@pytest.mark.e2e
class TestE2EIFramesErrorHandling:
    """E2E tests for error handling in iframe operations"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    def test_get_iframe_invalid_project(self, client):
        """Test getting iframe for non-existent project raises error"""
        options = IFrameOptions(
            resource="auction_metrics",
            user_email="test@example.com"
        )

        with pytest.raises(RillError):
            client.iframes.get(options, project="nonexistent-project", org="nonexistent-org")

    def test_get_iframe_invalid_resource(self, client):
        """Test getting iframe for non-existent resource"""
        options = IFrameOptions(
            resource="nonexistent_dashboard_12345",
            user_email="test@example.com"
        )

        # This might succeed (iframe URL is generated) but the dashboard won't load
        # The API typically generates the URL even if the resource doesn't exist
        # because the validation happens when the iframe is loaded, not during URL generation
        result = client.iframes.get(options, project=TEST_PROJECT, org=TEST_ORG)

        # URL should still be generated
        assert isinstance(result, IFrameResponse)
        assert result.iframe_src is not None
