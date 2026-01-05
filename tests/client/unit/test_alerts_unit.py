"""
Unit tests for AlertsResource class
"""

import json
from unittest.mock import Mock
import pytest

from pyrill import RillClient, AlertOptions
from pyrill.exceptions import RillAuthError, RillAPIError
from tests.fixtures.sample_data import (
    SAMPLE_ALERTS_RESOURCES,
    SAMPLE_CREATE_ALERT_RESPONSE,
    SAMPLE_EDIT_ALERT_RESPONSE,
    SAMPLE_DELETE_ALERT_RESPONSE,
    SAMPLE_UNSUBSCRIBE_ALERT_RESPONSE,
    SAMPLE_GET_ALERT_YAML_RESPONSE,
    SAMPLE_GENERATE_ALERT_YAML_RESPONSE,
    SAMPLE_ORGS,
    SAMPLE_PROJECTS,
)


@pytest.fixture
def mock_alerts_httpx_client(monkeypatch):
    """Mock httpx.Client for alert API requests"""
    def _create_response(data, status_code=200):
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.reason_phrase = "OK" if status_code == 200 else "Error"
        mock_response.text = json.dumps(data)
        mock_response.json.return_value = data
        return mock_response

    def _mock_request(method, url, **kwargs):
        """Route requests to appropriate mock responses"""
        endpoint = url.replace("https://api.rilldata.com/v1/", "")

        # Alert endpoints
        if "/runtime/resources" in endpoint and method == "GET":
            return _create_response(SAMPLE_ALERTS_RESOURCES)
        elif endpoint.endswith("/alerts") and method == "POST":
            return _create_response(SAMPLE_CREATE_ALERT_RESPONSE)
        elif "/alerts/" in endpoint and "/yaml" in endpoint and method == "GET":
            return _create_response(SAMPLE_GET_ALERT_YAML_RESPONSE)
        elif "/alerts/-/yaml" in endpoint and method == "POST":
            return _create_response(SAMPLE_GENERATE_ALERT_YAML_RESPONSE)
        elif "/alerts/" in endpoint and "/unsubscribe" in endpoint and method == "POST":
            return _create_response(SAMPLE_UNSUBSCRIBE_ALERT_RESPONSE)
        elif "/alerts/" in endpoint and method == "PUT":
            return _create_response(SAMPLE_EDIT_ALERT_RESPONSE)
        elif "/alerts/" in endpoint and method == "DELETE":
            return _create_response(SAMPLE_DELETE_ALERT_RESPONSE)

        # Auto-detection endpoints
        elif endpoint == "orgs" and method == "GET":
            return _create_response({"organizations": SAMPLE_ORGS})
        elif endpoint.startswith("orgs/") and endpoint.endswith("/projects") and method == "GET":
            return _create_response({"projects": SAMPLE_PROJECTS})

        # Default fallback
        return _create_response({"error": "Not found"}, 404)

    from unittest.mock import MagicMock
    import httpx

    mock_client_instance = MagicMock()
    mock_client_instance.__enter__.return_value = mock_client_instance
    mock_client_instance.__exit__.return_value = None
    mock_client_instance.request.side_effect = _mock_request

    mock_client_class = Mock(return_value=mock_client_instance)
    monkeypatch.setattr(httpx, "Client", mock_client_class)

    return mock_client_instance


@pytest.mark.unit
class TestAlertsResourceInit:
    """Tests for AlertsResource initialization and configuration"""

    def test_client_requires_org_and_project(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test that client requires both org and project (or auto-detection fails)"""
        with pytest.raises(RillAuthError) as exc_info:
            RillClient()
        # Auto-detection will fail because mock returns multiple orgs
        error_msg = str(exc_info.value)
        assert ("Cannot auto-detect" in error_msg or "org" in error_msg)

    def test_client_with_explicit_config(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test that client accepts explicit org/project"""
        client = RillClient(org="test-org-1", project="test-project-1")
        assert client.config.default_org == "test-org-1"
        assert client.config.default_project == "test-project-1"

    def test_client_with_env_config(self, mock_env_with_token, monkeypatch, mock_alerts_httpx_client):
        """Test that client loads org/project from environment"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org-1")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project-1")
        client = RillClient()
        assert client.config.default_org == "test-org-1"
        assert client.config.default_project == "test-project-1"


@pytest.mark.unit
class TestAlertsListMethod:
    """Tests for alerts.list() method"""

    def test_list_alerts_with_defaults(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test listing alerts using client defaults"""
        client = RillClient(org="test-org-1", project="test-project-1")
        alerts = client.alerts.list()

        assert alerts is not None
        assert len(alerts) == 2
        assert alerts[0].name == "revenue-drop-alert"
        assert alerts[0].spec.display_name == "Revenue Drop Alert"
        assert alerts[0].state.execution_count == 15
        assert alerts[1].name == "high-spend-alert"

    def test_list_alerts_with_explicit_params(self, mock_env_with_token, mock_alerts_httpx_client, monkeypatch):
        """Test listing alerts with explicit org and project override"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "default-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "default-project")
        client = RillClient()

        alerts = client.alerts.list(org="test-org-1", project="test-project-1")

        assert alerts is not None
        assert len(alerts) == 2

    def test_list_alerts_without_defaults_raises_error(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test that list without org/project configured raises error during client init"""
        with pytest.raises(RillAuthError) as exc_info:
            client = RillClient()
        error_msg = str(exc_info.value)
        assert ("Cannot auto-detect" in error_msg or ("org" in error_msg and "project" in error_msg))

    def test_list_alerts_filters_by_kind(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test that list only returns Alert resources"""
        client = RillClient(org="test-org-1", project="test-project-1")
        alerts = client.alerts.list()

        # Verify all returned items are alerts
        for alert in alerts:
            assert alert.name is not None
            assert alert.spec is not None

    def test_list_alerts_constructs_correct_endpoint(self, mock_env_with_token, monkeypatch):
        """Test that list constructs correct API endpoint"""
        urls_called = []

        def _mock_request(method, url, **kwargs):
            urls_called.append(url)
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = SAMPLE_ALERTS_RESOURCES
            return mock_response

        from unittest.mock import MagicMock
        import httpx

        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_instance.request.side_effect = _mock_request

        mock_client_class = Mock(return_value=mock_client_instance)
        monkeypatch.setattr(httpx, "Client", mock_client_class)

        client = RillClient(org="test-org-1", project="test-project-1")
        client.alerts.list()

        assert len(urls_called) > 0
        assert "organizations/test-org-1/projects/test-project-1/runtime/resources" in urls_called[0]


@pytest.mark.unit
class TestAlertsGetMethod:
    """Tests for alerts.get() method"""

    def test_get_alert_by_name(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test getting a specific alert by name"""
        client = RillClient(org="test-org-1", project="test-project-1")
        alert = client.alerts.get("revenue-drop-alert")

        assert alert is not None
        assert alert.name == "revenue-drop-alert"
        assert alert.spec.display_name == "Revenue Drop Alert"
        assert alert.spec.resolver == "metrics_threshold"

    def test_get_alert_with_explicit_params(self, mock_env_with_token, mock_alerts_httpx_client, monkeypatch):
        """Test getting alert with explicit org/project override"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "default-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "default-project")
        client = RillClient()

        alert = client.alerts.get("revenue-drop-alert", org="test-org-1", project="test-project-1")

        assert alert is not None
        assert alert.name == "revenue-drop-alert"

    def test_get_nonexistent_alert_raises_error(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test that getting nonexistent alert raises RillAPIError"""
        client = RillClient(org="test-org-1", project="test-project-1")

        with pytest.raises(RillAPIError) as exc_info:
            client.alerts.get("nonexistent-alert")
        assert "not found" in str(exc_info.value).lower()


@pytest.mark.unit
class TestAlertsCreateMethod:
    """Tests for alerts.create() method"""

    def test_create_alert(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test creating a new alert"""
        client = RillClient(org="test-org-1", project="test-project-1")

        options = AlertOptions(
            display_name="New Alert",
            refresh_cron="0 * * * *",
            resolver="metrics_threshold",
            metrics_view_name="test_metrics"
        )

        response = client.alerts.create(options)

        assert response is not None
        assert response.name == "new-alert"

    def test_create_alert_with_explicit_params(self, mock_env_with_token, mock_alerts_httpx_client, monkeypatch):
        """Test creating alert with explicit org/project override"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "default-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "default-project")
        client = RillClient()

        options = AlertOptions(
            display_name="New Alert",
            refresh_cron="0 * * * *"
        )

        response = client.alerts.create(options, org="test-org-1", project="test-project-1")

        assert response is not None
        assert response.name == "new-alert"

    def test_create_alert_with_notifiers(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test creating alert with notification configuration"""
        client = RillClient(org="test-org-1", project="test-project-1")

        options = AlertOptions(
            display_name="Alert with Notifications",
            refresh_cron="0 0 * * *",
            resolver="metrics_threshold",
            email_recipients=["team@example.com"],
            slack_channels=["#alerts"]
        )

        response = client.alerts.create(options)

        assert response is not None


@pytest.mark.unit
class TestAlertsEditMethod:
    """Tests for alerts.edit() method"""

    def test_edit_alert(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test editing an existing alert"""
        client = RillClient(org="test-org-1", project="test-project-1")

        options = AlertOptions(
            display_name="Updated Alert Name",
            refresh_cron="0 */2 * * *"
        )

        response = client.alerts.edit("revenue-drop-alert", options)

        assert response is not None

    def test_edit_alert_with_explicit_params(self, mock_env_with_token, mock_alerts_httpx_client, monkeypatch):
        """Test editing alert with explicit org/project override"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "default-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "default-project")
        client = RillClient()

        options = AlertOptions(display_name="Updated")

        response = client.alerts.edit(
            "revenue-drop-alert",
            options,
            org="test-org-1",
            project="test-project-1"
        )

        assert response is not None


@pytest.mark.unit
class TestAlertsDeleteMethod:
    """Tests for alerts.delete() method"""

    def test_delete_alert(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test deleting an alert"""
        client = RillClient(org="test-org-1", project="test-project-1")

        response = client.alerts.delete("revenue-drop-alert")

        assert response is not None

    def test_delete_alert_with_explicit_params(self, mock_env_with_token, mock_alerts_httpx_client, monkeypatch):
        """Test deleting alert with explicit org/project override"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "default-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "default-project")
        client = RillClient()

        response = client.alerts.delete(
            "revenue-drop-alert",
            org="test-org-1",
            project="test-project-1"
        )

        assert response is not None


@pytest.mark.unit
class TestAlertsUnsubscribeMethod:
    """Tests for alerts.unsubscribe() method"""

    def test_unsubscribe_from_alert(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test unsubscribing from an alert"""
        client = RillClient(org="test-org-1", project="test-project-1")

        response = client.alerts.unsubscribe("revenue-drop-alert")

        assert response is not None

    def test_unsubscribe_with_explicit_params(self, mock_env_with_token, mock_alerts_httpx_client, monkeypatch):
        """Test unsubscribing with explicit org/project override"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "default-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "default-project")
        client = RillClient()

        response = client.alerts.unsubscribe(
            "revenue-drop-alert",
            org="test-org-1",
            project="test-project-1"
        )

        assert response is not None


@pytest.mark.unit
class TestAlertsYAMLMethods:
    """Tests for alerts YAML methods (get_yaml and generate_yaml)"""

    def test_get_yaml(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test getting YAML for existing alert"""
        client = RillClient(org="test-org-1", project="test-project-1")

        yaml_str = client.alerts.get_yaml("revenue-drop-alert")

        assert yaml_str is not None
        assert isinstance(yaml_str, str)
        assert "type: alert" in yaml_str
        assert "Revenue Drop Alert" in yaml_str

    def test_get_yaml_with_explicit_params(self, mock_env_with_token, mock_alerts_httpx_client, monkeypatch):
        """Test getting YAML with explicit org/project override"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "default-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "default-project")
        client = RillClient()

        yaml_str = client.alerts.get_yaml(
            "revenue-drop-alert",
            org="test-org-1",
            project="test-project-1"
        )

        assert yaml_str is not None
        assert "type: alert" in yaml_str

    def test_generate_yaml(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test generating YAML from alert options"""
        client = RillClient(org="test-org-1", project="test-project-1")

        options = AlertOptions(
            display_name="New Alert",
            refresh_cron="0 * * * *",
            resolver="metrics_threshold",
            metrics_view_name="test_metrics"
        )

        yaml_str = client.alerts.generate_yaml(options)

        assert yaml_str is not None
        assert isinstance(yaml_str, str)
        assert "type: alert" in yaml_str

    def test_generate_yaml_with_explicit_params(self, mock_env_with_token, mock_alerts_httpx_client, monkeypatch):
        """Test generating YAML with explicit org/project override"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "default-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "default-project")
        client = RillClient()

        options = AlertOptions(
            display_name="New Alert",
            refresh_cron="0 * * * *"
        )

        yaml_str = client.alerts.generate_yaml(
            options,
            org="test-org-1",
            project="test-project-1"
        )

        assert yaml_str is not None


@pytest.mark.unit
class TestAlertsErrorHandling:
    """Tests for alert error handling"""

    def test_list_alerts_api_error(self, mock_env_with_token, monkeypatch):
        """Test handling of API errors in list"""
        def _mock_error_request(method, url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.reason_phrase = "Internal Server Error"
            mock_response.text = "Server error"
            mock_response.json.return_value = {"error": "Internal error"}
            return mock_response

        from unittest.mock import MagicMock
        import httpx

        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_instance.request.side_effect = _mock_error_request

        mock_client_class = Mock(return_value=mock_client_instance)
        monkeypatch.setattr(httpx, "Client", mock_client_class)

        client = RillClient(org="test-org-1", project="test-project-1")

        with pytest.raises(RillAPIError) as exc_info:
            client.alerts.list()
        assert exc_info.value.status_code == 500

    def test_create_alert_api_error(self, mock_env_with_token, monkeypatch):
        """Test handling of API errors in create"""
        def _mock_error_request(method, url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.reason_phrase = "Bad Request"
            mock_response.text = "Invalid alert configuration"
            mock_response.json.return_value = {"error": "Invalid options"}
            return mock_response

        from unittest.mock import MagicMock
        import httpx

        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_instance.request.side_effect = _mock_error_request

        mock_client_class = Mock(return_value=mock_client_instance)
        monkeypatch.setattr(httpx, "Client", mock_client_class)

        client = RillClient(org="test-org-1", project="test-project-1")

        options = AlertOptions(display_name="Invalid Alert")

        with pytest.raises(RillAPIError) as exc_info:
            client.alerts.create(options)
        assert exc_info.value.status_code == 400

    def test_alerts_without_org_raises_error(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test that operations without org configured raise error"""
        client = RillClient(org="test-org-1", project="test-project-1")
        # Override config to remove org
        client.config.default_org = None

        with pytest.raises(RillAPIError) as exc_info:
            client.alerts.list()
        assert "org" in str(exc_info.value).lower()

    def test_alerts_without_project_raises_error(self, mock_env_with_token, mock_alerts_httpx_client):
        """Test that operations without project configured raise error"""
        client = RillClient(org="test-org-1", project="test-project-1")
        # Override config to remove project
        client.config.default_project = None

        with pytest.raises(RillAPIError) as exc_info:
            client.alerts.list()
        assert "project" in str(exc_info.value).lower()
