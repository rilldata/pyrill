"""
Unit tests for PublicUrls resource (with mocked API responses)

These tests mock HTTP responses to test operations without hitting the real API.
"""

import pytest
from unittest.mock import Mock, MagicMock

from pyrill import RillClient
from pyrill.models import MagicAuthToken, CreatePublicUrlResponse
from pyrill.exceptions import RillAPIError


@pytest.mark.unit
class TestPublicUrlsList:
    """Unit tests for list() method"""

    def test_list_publicurls_success(self, rill_client_with_mocks, monkeypatch):
        """Test listing public URLs successfully"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                # Verify request
                assert method == "GET"
                assert "tokens/magic" in url

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "tokens": [
                        {
                            "id": "tok_123",
                            "projectId": "proj_abc",
                            "url": "https://example.rilldata.com/magic/tok_123",
                            "token": "tok_123",
                            "createdOn": "2024-01-20T10:00:00Z",
                            "expiresOn": "2024-01-21T10:00:00Z",
                            "createdByUserId": "user_1",
                            "createdByUserEmail": "user@example.com",
                            "resources": [
                                {
                                    "type": "rill.runtime.v1.Explore",
                                    "name": "test_explore"
                                }
                            ],
                            "fields": ["revenue", "date"],
                            "displayName": "Test Public URL"
                        },
                        {
                            "id": "tok_456",
                            "projectId": "proj_abc",
                            "url": "https://example.rilldata.com/magic/tok_456",
                            "token": "tok_456",
                            "createdOn": "2024-01-19T10:00:00Z",
                            "resources": [
                                {
                                    "type": "rill.runtime.v1.Explore",
                                    "name": "another_explore"
                                }
                            ],
                            "fields": []
                        }
                    ]
                }
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        tokens = rill_client_with_mocks.publicurls.list()

        assert len(tokens) == 2
        assert all(isinstance(t, MagicAuthToken) for t in tokens)
        assert tokens[0].id == "tok_123"
        assert tokens[0].url == "https://example.rilldata.com/magic/tok_123"
        assert tokens[0].display_name == "Test Public URL"
        assert len(tokens[0].resources) == 1
        assert tokens[0].resources[0].type == "rill.runtime.v1.Explore"
        assert tokens[0].resources[0].name == "test_explore"
        assert tokens[1].id == "tok_456"

    def test_list_publicurls_with_pagination(self, rill_client_with_mocks, monkeypatch):
        """Test listing public URLs with pagination params"""
        captured_params = {}

        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                # Capture pagination params
                if "params" in kwargs:
                    captured_params.update(kwargs["params"])

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"tokens": []}
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        rill_client_with_mocks.publicurls.list(page_size=100, page_token="next_page")

        assert captured_params["pageSize"] == 100
        assert captured_params["pageToken"] == "next_page"

    def test_list_publicurls_missing_org_error(self, mock_env_with_token, monkeypatch):
        """Test list raises error when org is missing"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.request.return_value = Mock(
                status_code=200,
                json=lambda: {"organizations": [{"name": "test-org"}]}
            )
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        # Don't set RILL_DEFAULT_ORG or RILL_DEFAULT_PROJECT
        from pyrill import RillClient
        with pytest.raises(Exception):  # Should fail during client init
            client = RillClient()

    def test_list_publicurls_api_error(self, rill_client_with_mocks, monkeypatch):
        """Test list handles API errors"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                mock_response = Mock()
                mock_response.status_code = 404
                mock_response.reason_phrase = "Not Found"
                mock_response.text = "Project not found"
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        with pytest.raises(RillAPIError) as exc_info:
            rill_client_with_mocks.publicurls.list()

        assert exc_info.value.status_code == 404


@pytest.mark.unit
class TestPublicUrlsCreate:
    """Unit tests for create() method"""

    def test_create_publicurl_success(self, rill_client_with_mocks, monkeypatch):
        """Test creating a public URL successfully"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                # Verify request
                assert method == "POST"
                assert "tokens/magic" in url
                assert "json" in kwargs
                request_body = kwargs["json"]
                assert "resources" in request_body
                assert len(request_body["resources"]) == 1
                assert request_body["resources"][0]["type"] == "rill.runtime.v1.Explore"
                assert request_body["resources"][0]["name"] == "my_explore"

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "token": "tok_xyz789",
                    "url": "https://example.rilldata.com/magic/tok_xyz789"
                }
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        result = rill_client_with_mocks.publicurls.create("my_explore")

        assert isinstance(result, CreatePublicUrlResponse)
        assert result.token == "tok_xyz789"
        assert result.url == "https://example.rilldata.com/magic/tok_xyz789"

    def test_create_publicurl_with_ttl(self, rill_client_with_mocks, monkeypatch):
        """Test creating a public URL with TTL"""
        captured_body = {}

        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                if "json" in kwargs:
                    captured_body.update(kwargs["json"])

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "token": "tok_123",
                    "url": "https://example.com/magic/tok_123"
                }
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        rill_client_with_mocks.publicurls.create("my_explore", ttl_minutes=1440)

        assert "ttlMinutes" in captured_body
        assert captured_body["ttlMinutes"] == 1440

    def test_create_publicurl_with_fields(self, rill_client_with_mocks, monkeypatch):
        """Test creating a public URL with field restrictions"""
        captured_body = {}

        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                if "json" in kwargs:
                    captured_body.update(kwargs["json"])

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "token": "tok_123",
                    "url": "https://example.com/magic/tok_123"
                }
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        rill_client_with_mocks.publicurls.create(
            "my_explore",
            fields=["revenue", "date"],
            display_name="Revenue Report"
        )

        assert "fields" in captured_body
        assert captured_body["fields"] == ["revenue", "date"]
        assert "displayName" in captured_body
        assert captured_body["displayName"] == "Revenue Report"

    def test_create_publicurl_with_filter(self, rill_client_with_mocks, monkeypatch):
        """Test creating a public URL with filter"""
        captured_body = {}

        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                if "json" in kwargs:
                    captured_body.update(kwargs["json"])

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "token": "tok_123",
                    "url": "https://example.com/magic/tok_123"
                }
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        test_filter = {"field": "revenue", "operator": ">", "value": 1000}
        rill_client_with_mocks.publicurls.create("my_explore", filter=test_filter)

        assert "filter" in captured_body
        assert captured_body["filter"] == test_filter

    def test_create_publicurl_validation_error(self, rill_client_with_mocks, monkeypatch):
        """Test create handles validation errors"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                # Return invalid response structure
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "invalid": "structure"
                }
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        with pytest.raises(RillAPIError) as exc_info:
            rill_client_with_mocks.publicurls.create("my_explore")

        assert "Failed to validate" in str(exc_info.value)

    def test_create_publicurl_missing_org_error(self, mock_env_with_token, monkeypatch):
        """Test create raises error when org is missing"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None
            mock_instance.request.return_value = Mock(
                status_code=200,
                json=lambda: {"organizations": [{"name": "test-org"}]}
            )
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        from pyrill import RillClient
        with pytest.raises(Exception):  # Should fail during client init
            client = RillClient()


@pytest.mark.unit
class TestPublicUrlsDelete:
    """Unit tests for delete() method"""

    def test_delete_publicurl_success(self, rill_client_with_mocks, monkeypatch):
        """Test deleting a public URL successfully"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                assert method == "DELETE"
                assert "magic-tokens" in url
                assert "tok_123" in url

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {}
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        # Should not raise an error
        result = rill_client_with_mocks.publicurls.delete("tok_123")
        assert result is None  # DELETE returns None

    def test_delete_publicurl_api_error(self, rill_client_with_mocks, monkeypatch):
        """Test delete handles API errors"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                mock_response = Mock()
                mock_response.status_code = 404
                mock_response.reason_phrase = "Not Found"
                mock_response.text = "Token not found"
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        with pytest.raises(RillAPIError) as exc_info:
            rill_client_with_mocks.publicurls.delete("tok_nonexistent")

        assert exc_info.value.status_code == 404


@pytest.mark.unit
class TestPublicUrlsModels:
    """Unit tests for PublicUrl model validation"""

    def test_magic_auth_token_model(self):
        """Test MagicAuthToken model accepts all expected fields"""
        token = MagicAuthToken(
            id="tok_123",
            project_id="proj_abc",
            url="https://example.com/magic/tok_123",
            token="tok_123",
            created_on="2024-01-20T10:00:00Z",
            expires_on="2024-01-21T10:00:00Z",
            used_on="2024-01-20T15:00:00Z",
            created_by_user_id="user_1",
            created_by_user_email="user@example.com",
            resources=[
                {"type": "rill.runtime.v1.Explore", "name": "test_explore"}
            ],
            filter={"field": "revenue", "operator": ">", "value": 1000},
            fields=["revenue", "date"],
            state="active",
            display_name="Test Token"
        )

        assert token.id == "tok_123"
        assert token.url == "https://example.com/magic/tok_123"
        assert token.display_name == "Test Token"
        assert len(token.resources) == 1
        assert token.resources[0].type == "rill.runtime.v1.Explore"
        assert len(token.fields) == 2

    def test_magic_auth_token_with_camelcase_fields(self):
        """Test MagicAuthToken model handles camelCase API fields"""
        token = MagicAuthToken(
            id="tok_123",
            projectId="proj_abc",
            createdByUserId="user_1",
            createdByUserEmail="user@example.com",
            displayName="Test Token",
            resources=[]
        )

        assert token.id == "tok_123"
        assert token.project_id == "proj_abc"
        assert token.created_by_user_id == "user_1"
        assert token.created_by_user_email == "user@example.com"
        assert token.display_name == "Test Token"

    def test_create_public_url_response_model(self):
        """Test CreatePublicUrlResponse model"""
        response = CreatePublicUrlResponse(
            token="tok_xyz789",
            url="https://example.com/magic/tok_xyz789"
        )

        assert response.token == "tok_xyz789"
        assert response.url == "https://example.com/magic/tok_xyz789"


@pytest.mark.unit
class TestPublicUrlsClientIntegration:
    """Test that publicurls resource is properly integrated into RillClient"""

    def test_publicurls_resource_exists(self, rill_client_with_mocks):
        """Test that client.publicurls exists"""
        assert hasattr(rill_client_with_mocks, "publicurls")

    def test_publicurls_resource_has_methods(self, rill_client_with_mocks):
        """Test that publicurls resource has all expected methods"""
        assert hasattr(rill_client_with_mocks.publicurls, "list")
        assert hasattr(rill_client_with_mocks.publicurls, "create")
        assert hasattr(rill_client_with_mocks.publicurls, "delete")
        assert callable(rill_client_with_mocks.publicurls.list)
        assert callable(rill_client_with_mocks.publicurls.create)
        assert callable(rill_client_with_mocks.publicurls.delete)
