"""
Unit tests for AnnotationsResource class
"""

import json
from unittest.mock import Mock
import pytest

from pyrill import RillClient
from pyrill.models import AnnotationsQuery, TimeRange, TimeGrain
from pyrill.exceptions import RillAuthError, RillAPIError
from tests.fixtures.sample_data import (
    SAMPLE_ANNOTATIONS_RESULT,
    SAMPLE_ORGS,
    SAMPLE_PROJECTS,
)


@pytest.fixture
def mock_annotations_httpx_client(monkeypatch):
    """Mock httpx.Client for annotations API requests"""
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

        # Annotations endpoints
        if "/runtime/queries/metrics-views/" in endpoint and "/annotations" in endpoint and method == "POST":
            return _create_response(SAMPLE_ANNOTATIONS_RESULT)

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
class TestAnnotationsResourceInit:
    """Tests for AnnotationsResource initialization and configuration"""

    def test_client_requires_org_and_project(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that client requires both org and project (or auto-detection fails)"""
        with pytest.raises(RillAuthError) as exc_info:
            RillClient()
        # Auto-detection will fail because mock returns multiple orgs
        error_msg = str(exc_info.value)
        assert ("Cannot auto-detect" in error_msg or "org" in error_msg)

    def test_client_with_explicit_config(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that client accepts explicit org/project"""
        client = RillClient(org="test-org-1", project="test-project-1")
        assert client.config.default_org == "test-org-1"
        assert client.config.default_project == "test-project-1"

    def test_client_with_env_config(self, mock_env_with_token, monkeypatch, mock_annotations_httpx_client):
        """Test that client loads org/project from environment"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "test-org-1")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "test-project-1")
        client = RillClient()
        assert client.config.default_org == "test-org-1"
        assert client.config.default_project == "test-project-1"


@pytest.mark.unit
class TestAnnotationsQuery:
    """Tests for annotations.query() method"""

    def test_annotations_query_with_defaults(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test annotations query using client defaults"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["revenue"],
            time_range=TimeRange(expression="LAST_30_DAYS"),
            limit=100
        )

        result = client.annotations.query("revenue_metrics", query)

        assert result is not None
        assert result.rows is not None
        assert len(result.rows) == 3
        assert result.rows[0].time == "2025-01-15T09:00:00Z"
        assert result.rows[0].description == "Product launch - New model released"
        assert result.rows[0].for_measures == ["revenue", "orders"]

    def test_annotations_query_with_explicit_params(self, mock_env_with_token, mock_annotations_httpx_client, monkeypatch):
        """Test annotations query with explicit org and project"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "default-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "default-project")
        client = RillClient()

        query = AnnotationsQuery(
            measures=["revenue", "orders"],
            time_range=TimeRange(expression="LAST_7_DAYS"),
            limit=50
        )

        result = client.annotations.query(
            "revenue_metrics",
            query,
            project="test-project-1",
            org="test-org-1"
        )

        assert result is not None
        assert len(result.rows) == 3

    def test_annotations_query_without_defaults_raises_error(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that query without org/project configured raises error during client init"""
        query = AnnotationsQuery(
            measures=["revenue"],
            limit=10
        )

        # Client creation should fail without org/project (auto-detection fails with multiple options)
        with pytest.raises(RillAuthError) as exc_info:
            client = RillClient()
        error_msg = str(exc_info.value)
        assert ("Cannot auto-detect" in error_msg or ("org" in error_msg and "project" in error_msg))

    def test_annotations_query_with_time_grain(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test annotations query with time grain"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["revenue"],
            time_range=TimeRange(expression="LAST_30_DAYS"),
            time_grain=TimeGrain.DAY,
            limit=100
        )

        result = client.annotations.query("revenue_metrics", query)
        assert result is not None

    def test_annotations_query_with_time_zone(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test annotations query with time zone"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["revenue"],
            time_range=TimeRange(expression="LAST_7_DAYS"),
            time_zone="America/New_York",
            limit=50
        )

        result = client.annotations.query("revenue_metrics", query)
        assert result is not None

    def test_annotations_query_with_priority(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test annotations query with priority filter"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["revenue"],
            priority=1,
            limit=20
        )

        result = client.annotations.query("revenue_metrics", query)
        assert result is not None

    def test_annotations_query_with_offset(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test annotations query with offset for pagination"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["revenue"],
            limit=10,
            offset=5
        )

        result = client.annotations.query("revenue_metrics", query)
        assert result is not None

    def test_annotations_query_with_dict(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test annotations query using dict instead of AnnotationsQuery"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query_dict = {
            "measures": ["revenue"],
            "time_range": {"expression": "LAST_7_DAYS"},
            "limit": 50
        }

        result = client.annotations.query("revenue_metrics", query_dict)

        assert result is not None
        assert len(result.rows) == 3

    def test_annotations_query_constructs_correct_endpoint(self, mock_env_with_token, monkeypatch):
        """Test that annotations query constructs correct API endpoint"""
        urls_called = []

        def _mock_request(method, url, **kwargs):
            urls_called.append(url)
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = SAMPLE_ANNOTATIONS_RESULT
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

        query = AnnotationsQuery(
            measures=["revenue"],
            limit=10
        )

        client.annotations.query("revenue_metrics", query)

        assert len(urls_called) > 0
        assert "organizations/test-org-1/projects/test-project-1/runtime/queries/metrics-views/revenue_metrics/annotations" in urls_called[0]


@pytest.mark.unit
class TestAnnotationsResponse:
    """Tests for annotations response parsing"""

    def test_annotations_response_with_time_end(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that annotations with timeEnd are parsed correctly"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["revenue"],
            limit=10
        )

        result = client.annotations.query("revenue_metrics", query)

        # Find annotation with timeEnd
        maintenance_annotation = result.rows[1]
        assert maintenance_annotation.time_end == "2025-01-18T16:30:00Z"
        assert maintenance_annotation.duration == "PT2H"

    def test_annotations_response_with_additional_fields(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that annotations with additionalFields are parsed correctly"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["revenue", "orders"],
            limit=10
        )

        result = client.annotations.query("revenue_metrics", query)

        # First annotation has additional fields
        first_annotation = result.rows[0]
        assert first_annotation.additional_fields is not None
        assert first_annotation.additional_fields["category"] == "product"
        assert first_annotation.additional_fields["severity"] == "high"

    def test_annotations_response_with_multiple_measures(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that annotations for multiple measures are parsed correctly"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["impressions", "clicks", "conversions"],
            limit=10
        )

        result = client.annotations.query("revenue_metrics", query)

        # Last annotation applies to multiple measures
        campaign_annotation = result.rows[2]
        assert len(campaign_annotation.for_measures) == 3
        assert "impressions" in campaign_annotation.for_measures
        assert "clicks" in campaign_annotation.for_measures
        assert "conversions" in campaign_annotation.for_measures


@pytest.mark.unit
class TestAnnotationsErrorHandling:
    """Tests for annotations error handling"""

    def test_annotations_query_api_error(self, mock_env_with_token, monkeypatch):
        """Test handling of API errors in annotations query"""
        def _mock_error_request(method, url, **kwargs):
            mock_response = Mock()
            mock_response.status_code = 400
            mock_response.reason_phrase = "Bad Request"
            mock_response.text = "Invalid query"
            mock_response.json.return_value = {"error": "Invalid metrics view"}
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

        query = AnnotationsQuery(
            measures=["invalid_measure"],
            limit=10
        )

        with pytest.raises(RillAPIError) as exc_info:
            client.annotations.query("invalid_metrics", query)
        assert exc_info.value.status_code == 400

    def test_annotations_query_invalid_dict(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that invalid query dict raises error"""
        client = RillClient(org="test-org-1", project="test-project-1")

        # Invalid query dict (missing required fields or invalid structure)
        invalid_query_dict = {
            "invalid_field": "invalid_value",
            "time_range": "not_an_object"  # Should be a dict
        }

        with pytest.raises(RillAPIError) as exc_info:
            client.annotations.query("revenue_metrics", invalid_query_dict)
        assert "Invalid annotations query" in str(exc_info.value)

    def test_annotations_without_org_raises_error(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that query without org configured raises error"""
        client = RillClient(org="test-org-1", project="test-project-1")
        # Override config to remove org
        client.config.default_org = None

        query = AnnotationsQuery(measures=["revenue"], limit=10)

        with pytest.raises(RillAPIError) as exc_info:
            client.annotations.query("revenue_metrics", query)
        assert "org" in str(exc_info.value).lower()

    def test_annotations_without_project_raises_error(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that query without project configured raises error"""
        client = RillClient(org="test-org-1", project="test-project-1")
        # Override config to remove project
        client.config.default_project = None

        query = AnnotationsQuery(measures=["revenue"], limit=10)

        with pytest.raises(RillAPIError) as exc_info:
            client.annotations.query("revenue_metrics", query)
        assert "project" in str(exc_info.value).lower()

    def test_query_excludes_none_values(self, mock_env_with_token, monkeypatch):
        """Test that query serialization excludes None values"""
        request_data_captured = []

        def _mock_capture_request(method, url, **kwargs):
            if "json" in kwargs:
                request_data_captured.append(kwargs["json"])
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = SAMPLE_ANNOTATIONS_RESULT
            return mock_response

        from unittest.mock import MagicMock
        import httpx

        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_instance.request.side_effect = _mock_capture_request

        mock_client_class = Mock(return_value=mock_client_instance)
        monkeypatch.setattr(httpx, "Client", mock_client_class)

        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["revenue"],
            limit=10,
            # These should be excluded from request
            priority=None,
            time_zone=None,
            offset=None
        )

        client.annotations.query("revenue_metrics", query)

        assert len(request_data_captured) > 0
        assert "priority" not in request_data_captured[0]
        assert "timeZone" not in request_data_captured[0]
        assert "offset" not in request_data_captured[0]


@pytest.mark.unit
class TestAnnotationsQueryPositionalArgs:
    """Tests for annotations.query() positional argument handling"""

    def test_query_with_positional_args(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that metrics_view_name and query can be passed positionally"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["revenue"],
            limit=10
        )

        # Both positional
        result = client.annotations.query("revenue_metrics", query)
        assert result is not None

    def test_query_with_named_args(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that metrics_view_name and query can be passed as named arguments"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["revenue"],
            limit=10
        )

        # Both named
        result = client.annotations.query(metrics_view_name="revenue_metrics", query=query)
        assert result is not None

    def test_query_with_mixed_args(self, mock_env_with_token, mock_annotations_httpx_client):
        """Test that metrics_view_name positional and query named works"""
        client = RillClient(org="test-org-1", project="test-project-1")

        query = AnnotationsQuery(
            measures=["revenue"],
            limit=10
        )

        # metrics_view_name positional, query named
        result = client.annotations.query("revenue_metrics", query=query)
        assert result is not None
