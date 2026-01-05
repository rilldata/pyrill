"""
Unit tests for RillClient class
"""

import os
import time
from unittest.mock import Mock, MagicMock
import pytest

from pyrill import RillClient
from pyrill.exceptions import RillAuthError, RillAPIError


@pytest.mark.unit
class TestRillClientInit:
    """Tests for RillClient initialization"""

    def test_init_with_env_token(self, mock_env_with_token, mock_httpx_client, monkeypatch):
        """Test initialization with token from environment"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient()
        assert client.api_token is not None
        assert client.api_base_url == "https://api.rilldata.com/v1/"

    def test_init_with_explicit_token(self, mock_env_without_token, mock_httpx_client, monkeypatch):
        """Test initialization with explicit token"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient(api_token="rill_usr_explicit")
        assert client.api_token == "rill_usr_explicit"

    def test_init_without_token_raises_error(self, mock_env_without_token):
        """Test that missing token raises RillAuthError"""
        with pytest.raises(RillAuthError) as exc_info:
            RillClient()
        assert "No API token provided" in str(exc_info.value)

    def test_init_with_custom_api_base(self, mock_env_with_token, mock_httpx_client, monkeypatch):
        """Test initialization with custom API base URL"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient(api_base_url="https://custom.api.com/v2")
        assert client.api_base_url == "https://custom.api.com/v2/"

    def test_init_normalizes_api_base_url(self, mock_env_with_token, mock_httpx_client, monkeypatch):
        """Test that API base URL is normalized with trailing slash"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient(api_base_url="https://api.example.com")
        assert client.api_base_url.endswith("/")


@pytest.mark.unit
class TestRillClientAPIRequests:
    """Tests for _make_api_request method"""

    def test_make_api_request_success(self, rill_client_with_mocks):
        """Test successful API request"""
        result = rill_client_with_mocks._make_api_request("GET", "orgs")
        assert result is not None

    def test_make_api_request_constructs_url(self, rill_client_with_mocks, monkeypatch):
        """Test that API request constructs correct URL"""
        urls_called = []

        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                urls_called.append(url)
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {}
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        rill_client_with_mocks._make_api_request("GET", "test/endpoint")

        assert len(urls_called) > 0
        assert "test/endpoint" in urls_called[0]

    def test_make_api_request_sets_auth_header(self, rill_client_with_mocks, monkeypatch):
        """Test that API request sets Authorization header"""
        headers_used = {}

        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, headers=None, **kwargs):
                headers_used.update(headers or {})
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {}
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        rill_client_with_mocks._make_api_request("GET", "test/endpoint")

        assert "Authorization" in headers_used
        assert headers_used["Authorization"].startswith("Bearer ")

    def test_make_api_request_404_error(self, rill_client_with_mocks, monkeypatch):
        """Test handling of 404 error"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(*args, **kwargs):
                mock_response = Mock()
                mock_response.status_code = 404
                mock_response.reason_phrase = "Not Found"
                mock_response.text = "Resource not found"
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        with pytest.raises(RillAPIError) as exc_info:
            rill_client_with_mocks._make_api_request("GET", "test/endpoint")
        assert exc_info.value.status_code == 404

    def test_make_api_request_http_error(self, rill_client_with_mocks, monkeypatch):
        """Test handling of HTTP connection error"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(*args, **kwargs):
                import httpx
                raise httpx.ConnectError("Connection failed")

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        with pytest.raises(RillAPIError):
            rill_client_with_mocks._make_api_request("GET", "test/endpoint")


@pytest.mark.unit
class TestRillClientCache:
    """Tests for client caching functionality"""

    def test_cache_disabled_by_default(self, mock_env_with_token, mock_httpx_client, monkeypatch):
        """Test that caching is disabled by default"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient()
        assert client._cache is None

    def test_cache_enabled_with_flag(self, mock_env_with_token, mock_httpx_client, monkeypatch):
        """Test that caching can be enabled"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient(enable_cache=True)
        assert client._cache is not None

    def test_cache_custom_ttl(self, mock_env_with_token, mock_httpx_client, monkeypatch):
        """Test that cache TTL can be customized"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient(enable_cache=True, cache_ttl=600)
        assert client._cache._ttl == 600

    def test_list_orgs_uses_cache(self, rill_client_with_mocks, monkeypatch):
        """Test that list_orgs uses cache on second call"""
        # Create client with cache enabled
        from pyrill import RillClient
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient(enable_cache=True)

        call_count = [0]
        original_make_request = client._make_api_request

        def counting_make_request(*args, **kwargs):
            call_count[0] += 1
            return original_make_request(*args, **kwargs)

        client._make_api_request = counting_make_request

        # First call should execute request
        orgs1 = client.orgs.list()
        first_call_count = call_count[0]

        # Second call should use cache
        orgs2 = client.orgs.list()

        assert len(orgs1) == len(orgs2)
        assert call_count[0] == first_call_count  # No additional calls

    def test_clear_cache_works(self, mock_env_with_token, mock_httpx_client, monkeypatch):
        """Test that clear_cache clears all cached data"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient(enable_cache=True)

        call_count = [0]
        original_make_request = client._make_api_request

        def counting_make_request(*args, **kwargs):
            call_count[0] += 1
            return original_make_request(*args, **kwargs)

        client._make_api_request = counting_make_request

        # First call
        client.orgs.list()
        first_count = call_count[0]

        # Second call (uses cache)
        client.orgs.list()
        assert call_count[0] == first_count

        # Clear cache
        client.clear_cache()

        # Third call (should fetch again)
        client.orgs.list()
        assert call_count[0] == first_count + 1

    def test_clear_cache_does_nothing_when_disabled(self, mock_env_with_token, mock_httpx_client, monkeypatch):
        """Test that clear_cache is safe to call when caching is disabled"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient(enable_cache=False)
        client.clear_cache()  # Should not raise an error

    def test_cache_expiration(self, mock_env_with_token, mock_httpx_client, monkeypatch):
        """Test that cache entries expire after TTL"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient(enable_cache=True, cache_ttl=1)  # 1 second TTL

        call_count = [0]
        original_make_request = client._make_api_request

        def counting_make_request(*args, **kwargs):
            call_count[0] += 1
            return original_make_request(*args, **kwargs)

        client._make_api_request = counting_make_request

        # First call
        client.orgs.list()
        first_count = call_count[0]

        # Immediate second call (uses cache)
        client.orgs.list()
        assert call_count[0] == first_count

        # Wait for expiration
        time.sleep(1.1)

        # Third call (cache expired, should fetch again)
        client.orgs.list()
        assert call_count[0] == first_count + 1

    def test_project_status_uses_cache(self, rill_client_with_mocks, monkeypatch):
        """Test that project_status uses cache on second call"""
        from pyrill import RillClient
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project")
        client = RillClient(enable_cache=True)

        call_count = [0]
        original_make_request = client._make_api_request

        def counting_make_request(*args, **kwargs):
            call_count[0] += 1
            return original_make_request(*args, **kwargs)

        client._make_api_request = counting_make_request

        # First call should execute request
        status1 = client.projects.status("test-project-1", org="test-org-1")
        first_call_count = call_count[0]

        # Second call should use cache
        status2 = client.projects.status("test-project-1", org="test-org-1")

        assert status1 == status2
        assert call_count[0] == first_call_count  # No additional calls
