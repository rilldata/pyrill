"""
Unit tests for QueryResource class
"""

import json
from unittest.mock import Mock
from datetime import datetime, timedelta
import pytest

from pyrill import (
    RillClient,
    MetricsQuery,
    MetricsSqlQuery,
    SqlQuery,
    Dimension,
    Measure,
    TimeRange,
    Sort,
    Expression,
    Condition,
    Operator,
)
from pyrill.exceptions import RillAuthError, RillAPIError
from tests.fixtures.sample_data import (
    SAMPLE_METRICS_RESULT,
    SAMPLE_SQL_RESULT,
    SAMPLE_ORGS,
    SAMPLE_PROJECTS,
)


@pytest.fixture
def mock_query_httpx_client(monkeypatch):
    """Mock httpx.Client for query API requests"""
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

        # Query endpoints
        if "/runtime/api/metrics" in endpoint and method == "POST":
            return _create_response(SAMPLE_METRICS_RESULT)
        elif "/runtime/api/metrics-sql" in endpoint and method == "POST":
            return _create_response(SAMPLE_SQL_RESULT)
        elif "/runtime/api/sql" in endpoint and method == "POST":
            return _create_response(SAMPLE_SQL_RESULT)

        # Auto-detection endpoints (return multiple to trigger error)
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
class TestQueryResourceInit:
    """Tests for QueryResource initialization and configuration"""

    def test_client_requires_org_and_project(self, mock_env_with_token, mock_query_httpx_client):
        """Test that client requires both org and project (or auto-detection fails)"""
        with pytest.raises(RillAuthError) as exc_info:
            RillClient()
        # Auto-detection will fail because mock returns multiple orgs
        error_msg = str(exc_info.value)
        assert ("Cannot auto-detect" in error_msg or "org" in error_msg)

    def test_client_with_explicit_config(self, mock_env_with_token, mock_query_httpx_client):
        """Test that client accepts explicit org/project"""
        client = RillClient(org="demo", project="rill-openrtb-prog-ads")
        assert client.config.default_org == "demo"
        assert client.config.default_project == "rill-openrtb-prog-ads"

    def test_client_with_env_config(self, mock_env_with_token, monkeypatch, mock_query_httpx_client):
        """Test that client loads org/project from environment"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "demo")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "rill-openrtb-prog-ads")
        client = RillClient()
        assert client.config.default_org == "demo"
        assert client.config.default_project == "rill-openrtb-prog-ads"

    def test_explicit_config_overrides_env(self, mock_env_with_token, monkeypatch, mock_query_httpx_client):
        """Test that explicit org/project override environment variables"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "env-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "env-project")
        client = RillClient(org="demo", project="rill-openrtb-prog-ads")
        assert client.config.default_org == "demo"
        assert client.config.default_project == "rill-openrtb-prog-ads"

    def test_client_fails_with_only_org(self, mock_env_with_token, mock_query_httpx_client):
        """Test that client fails if only org is provided (auto-detection fails with multiple projects)"""
        with pytest.raises(RillAuthError) as exc_info:
            RillClient(org="demo")
        # Auto-detection will fail because mock returns multiple projects
        error_msg = str(exc_info.value)
        assert ("Cannot auto-detect" in error_msg or "project" in error_msg)

    def test_client_fails_with_only_project(self, mock_env_with_token, mock_query_httpx_client):
        """Test that client fails if only project is provided (auto-detection fails with multiple orgs)"""
        with pytest.raises(RillAuthError) as exc_info:
            RillClient(project="rill-openrtb-prog-ads")
        # Auto-detection will fail because mock returns multiple orgs
        error_msg = str(exc_info.value)
        assert ("Cannot auto-detect" in error_msg or "org" in error_msg)


@pytest.mark.unit
class TestMetricsQuery:
    """Tests for metrics() query method"""

    def test_metrics_query_with_explicit_params(self, mock_env_with_token, mock_query_httpx_client, monkeypatch):
        """Test metrics query with explicit org and project"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "demo")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "rill-openrtb-prog-ads")
        client = RillClient()

        # Calculate date range (3 days ago to 2 days ago)
        from datetime import timezone
        end_date = datetime.now(timezone.utc) - timedelta(days=2)
        start_date = end_date - timedelta(days=1)

        query = MetricsQuery(
            metrics_view="bids_metrics",
            dimensions=[
                Dimension(name="advertiser_name"),
                Dimension(name="device_type")
            ],
            measures=[
                Measure(name="overall_spend"),
                Measure(name="total_bids"),
                Measure(name="win_rate"),
                Measure(name="impressions")
            ],
            time_range=TimeRange(
                start=start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                end=end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            ),
            sort=[Sort(name="overall_spend", desc=True)],
            limit=100
        )

        result = client.queries.metrics(
            query,
            project="rill-openrtb-prog-ads",
            org="demo"
        )

        assert result is not None
        assert len(result.data) == 3
        assert result.data[0]["advertiser_name"] == "Hyundai"
        assert result.data[0]["overall_spend"] == 12500.50
        assert result.data[1]["device_type"] == "desktop"

    def test_metrics_query_with_defaults(self, mock_env_with_token, mock_query_httpx_client):
        """Test metrics query using client defaults"""
        client = RillClient(org="demo", project="rill-openrtb-prog-ads")

        query = MetricsQuery(
            metrics_view="bids_metrics",
            dimensions=[Dimension(name="advertiser_name")],
            measures=[Measure(name="overall_spend")],
            limit=10
        )

        result = client.queries.metrics(query)

        assert result is not None
        assert len(result.data) == 3

    def test_metrics_query_without_defaults_raises_error(self, mock_env_with_token, mock_query_httpx_client):
        """Test that metrics query without org/project configured raises error during client init"""
        query = MetricsQuery(
            metrics_view="bids_metrics",
            dimensions=[Dimension(name="advertiser_name")],
            measures=[Measure(name="overall_spend")]
        )

        # Client creation should fail without org/project (auto-detection fails with multiple options)
        with pytest.raises(RillAuthError) as exc_info:
            client = RillClient()
        error_msg = str(exc_info.value)
        assert ("Cannot auto-detect" in error_msg or ("org" in error_msg and "project" in error_msg))

    def test_metrics_query_with_filter(self, mock_env_with_token, mock_query_httpx_client):
        """Test metrics query with WHERE filter"""
        client = RillClient(org="demo", project="rill-openrtb-prog-ads")

        query = MetricsQuery(
            metrics_view="bids_metrics",
            dimensions=[Dimension(name="advertiser_name")],
            measures=[Measure(name="overall_spend")],
            where=Expression(
                cond=Condition(
                    op=Operator.EQ,
                    exprs=[
                        Expression(name="device_type"),
                        Expression(val="mobile")
                    ]
                )
            ),
            limit=10
        )

        result = client.queries.metrics(query)
        assert result is not None

    def test_metrics_query_with_time_range_iso_duration(self, mock_env_with_token, mock_query_httpx_client):
        """Test metrics query with ISO 8601 duration using iso_duration parameter"""
        client = RillClient(org="demo", project="rill-openrtb-prog-ads")

        query = MetricsQuery(
            metrics_view="bids_metrics",
            dimensions=[Dimension(name="advertiser_name")],
            measures=[Measure(name="total_bids")],
            time_range=TimeRange(iso_duration="P7D"),
            limit=10
        )

        result = client.queries.metrics(query)
        assert result is not None

    def test_metrics_query_with_time_range_expression(self, mock_env_with_token, mock_query_httpx_client):
        """Test metrics query with time range using expression parameter"""
        client = RillClient(org="demo", project="rill-openrtb-prog-ads")

        query = MetricsQuery(
            metrics_view="bids_metrics",
            dimensions=[Dimension(name="advertiser_name")],
            measures=[Measure(name="total_bids")],
            time_range=TimeRange(expression="P7D"),
            limit=10
        )

        result = client.queries.metrics(query)
        assert result is not None

    def test_metrics_query_constructs_correct_endpoint(self, mock_env_with_token, monkeypatch):
        """Test that metrics query constructs correct API endpoint"""
        urls_called = []

        def _mock_request(method, url, **kwargs):
            urls_called.append(url)
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = SAMPLE_METRICS_RESULT
            return mock_response

        from unittest.mock import MagicMock
        import httpx

        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_instance.request.side_effect = _mock_request

        mock_client_class = Mock(return_value=mock_client_instance)
        monkeypatch.setattr(httpx, "Client", mock_client_class)

        client = RillClient(org="demo", project="rill-openrtb-prog-ads")

        query = MetricsQuery(
            metrics_view="bids_metrics",
            dimensions=[Dimension(name="advertiser_name")],
            measures=[Measure(name="overall_spend")]
        )

        client.queries.metrics(query)

        assert len(urls_called) > 0
        assert "organizations/demo/projects/rill-openrtb-prog-ads/runtime/api/metrics" in urls_called[0]


@pytest.mark.unit
class TestMetricsSqlQuery:
    """Tests for metrics_sql() query method"""

    def test_metrics_sql_query(self, mock_env_with_token, mock_query_httpx_client):
        """Test metrics SQL query"""
        client = RillClient(org="demo", project="rill-openrtb-prog-ads")

        query = MetricsSqlQuery(
            sql="SELECT advertiser_name, SUM(overall_spend) as total FROM metrics GROUP BY advertiser_name"
        )

        result = client.queries.metrics_sql(query)

        assert result is not None
        assert len(result.data) == 3
        assert result.data[0]["advertiser_name"] == "Hyundai"

    def test_metrics_sql_query_with_filter(self, mock_env_with_token, mock_query_httpx_client):
        """Test metrics SQL query with additional filter"""
        client = RillClient(org="demo", project="rill-openrtb-prog-ads")

        query = MetricsSqlQuery(
            sql="SELECT advertiser_name, SUM(overall_spend) as total FROM metrics GROUP BY advertiser_name",
            additional_where=Expression(
                cond=Condition(
                    op=Operator.GT,
                    exprs=[
                        Expression(name="total_bids"),
                        Expression(val=1000)
                    ]
                )
            )
        )

        result = client.queries.metrics_sql(query)
        assert result is not None

    def test_metrics_sql_query_without_config_fails_at_init(self, mock_env_with_token, mock_query_httpx_client):
        """Test that client init without org/project raises error (auto-detection fails with multiple options)"""
        with pytest.raises(RillAuthError) as exc_info:
            client = RillClient()
        error_msg = str(exc_info.value)
        assert ("Cannot auto-detect" in error_msg or ("org" in error_msg and "project" in error_msg))


@pytest.mark.unit
class TestSqlQuery:
    """Tests for sql() query method"""

    def test_sql_query(self, mock_env_with_token, mock_query_httpx_client):
        """Test raw SQL query"""
        client = RillClient(org="demo", project="rill-openrtb-prog-ads")

        query = SqlQuery(
            sql="SELECT advertiser_name, total FROM bids_summary LIMIT 10",
            connector="duckdb"
        )

        result = client.queries.sql(query)

        assert result is not None
        assert len(result.data) == 3

    def test_sql_query_without_connector(self, mock_env_with_token, mock_query_httpx_client):
        """Test raw SQL query without explicit connector"""
        client = RillClient(org="demo", project="rill-openrtb-prog-ads")

        query = SqlQuery(sql="SELECT * FROM bids_summary LIMIT 5")

        result = client.queries.sql(query)
        assert result is not None

    def test_sql_query_with_explicit_params(self, mock_env_with_token, mock_query_httpx_client, monkeypatch):
        """Test SQL query with explicit org/project override"""
        monkeypatch.setenv("RILL_DEFAULT_ORG", "default-org")
        monkeypatch.setenv("RILL_DEFAULT_PROJECT", "default-project")
        client = RillClient()

        query = SqlQuery(sql="SELECT COUNT(*) as total FROM bids_summary")

        result = client.queries.sql(
            query,
            project="rill-openrtb-prog-ads",
            org="demo"
        )

        assert result is not None


@pytest.mark.unit
class TestQueryErrorHandling:
    """Tests for query error handling"""

    def test_metrics_query_api_error(self, mock_env_with_token, monkeypatch):
        """Test handling of API errors in metrics query"""
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

        client = RillClient(org="demo", project="rill-openrtb-prog-ads")

        query = MetricsQuery(
            metrics_view="invalid_metrics",
            measures=[Measure(name="total_bids")]
        )

        with pytest.raises(RillAPIError) as exc_info:
            client.queries.metrics(query)
        assert exc_info.value.status_code == 400

    def test_query_with_partial_config_fails_at_init(self, mock_env_with_token, mock_query_httpx_client):
        """Test client init with only org (missing project) fails (auto-detection finds multiple projects)"""
        with pytest.raises(RillAuthError) as exc_info:
            client = RillClient(org="demo")
        error_msg = str(exc_info.value)
        assert ("Cannot auto-detect" in error_msg or "project" in error_msg)

    def test_query_excludes_none_values(self, mock_env_with_token, monkeypatch):
        """Test that query serialization excludes None values"""
        request_data_captured = []

        def _mock_capture_request(method, url, **kwargs):
            if "json" in kwargs:
                request_data_captured.append(kwargs["json"])
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = SAMPLE_METRICS_RESULT
            return mock_response

        from unittest.mock import MagicMock
        import httpx

        mock_client_instance = MagicMock()
        mock_client_instance.__enter__.return_value = mock_client_instance
        mock_client_instance.__exit__.return_value = None
        mock_client_instance.request.side_effect = _mock_capture_request

        mock_client_class = Mock(return_value=mock_client_instance)
        monkeypatch.setattr(httpx, "Client", mock_client_class)

        client = RillClient(org="demo", project="rill-openrtb-prog-ads")

        query = MetricsQuery(
            metrics_view="bids_metrics",
            dimensions=[Dimension(name="advertiser_name")],
            measures=[Measure(name="overall_spend")],
            # These should be excluded from request
            where=None,
            having=None,
            time_range=None
        )

        client.queries.metrics(query)

        assert len(request_data_captured) > 0
        assert "where" not in request_data_captured[0]
        assert "having" not in request_data_captured[0]
        assert "time_range" not in request_data_captured[0]
