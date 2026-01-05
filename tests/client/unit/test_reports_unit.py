"""
Unit tests for Reports resource (with mocked API responses)

These tests mock HTTP responses to test write operations without hitting the real API.
"""

import pytest
from unittest.mock import Mock, MagicMock

from pyrill import RillClient
from pyrill.models.reports import (
    Report,
    ReportOptions,
    ExportFormat,
    CreateReportResponse,
    EditReportResponse,
    DeleteReportResponse,
    TriggerReportResponse,
    UnsubscribeReportResponse,
)
from pyrill.exceptions import RillAPIError


@pytest.mark.unit
class TestReportsListAndGet:
    """Unit tests for list() and get() methods"""

    def test_list_reports_success(self, rill_client_with_mocks, monkeypatch):
        """Test listing reports successfully"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                # Mock response for runtime resources endpoint
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "resources": [
                        {
                            "meta": {
                                "name": {
                                    "kind": "rill.runtime.v1.Report",
                                    "name": "test-report-1"
                                }
                            },
                            "report": {
                                "spec": {
                                    "displayName": "Test Report 1",
                                    "queryName": "test_query"
                                },
                                "state": {
                                    "nextRunOn": "2024-01-22T09:00:00Z",
                                    "executionCount": 5
                                }
                            }
                        },
                        {
                            "meta": {
                                "name": {
                                    "kind": "rill.runtime.v1.Model",
                                    "name": "some-model"
                                }
                            },
                            "model": {}
                        },
                        {
                            "meta": {
                                "name": {
                                    "kind": "rill.runtime.v1.Report",
                                    "name": "test-report-2"
                                }
                            },
                            "report": {
                                "spec": {
                                    "displayName": "Test Report 2"
                                }
                            }
                        }
                    ]
                }
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        reports = rill_client_with_mocks.reports.list()

        assert len(reports) == 2
        assert all(isinstance(r, Report) for r in reports)
        assert reports[0].name == "test-report-1"
        assert reports[1].name == "test-report-2"

    def test_get_report_success(self, rill_client_with_mocks, monkeypatch):
        """Test getting a specific report by name"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "resources": [
                        {
                            "meta": {
                                "name": {
                                    "kind": "rill.runtime.v1.Report",
                                    "name": "target-report"
                                }
                            },
                            "report": {
                                "spec": {
                                    "displayName": "Target Report"
                                }
                            }
                        }
                    ]
                }
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        report = rill_client_with_mocks.reports.get("target-report")

        assert isinstance(report, Report)
        assert report.name == "target-report"

    def test_get_report_not_found(self, rill_client_with_mocks, monkeypatch):
        """Test getting non-existent report raises error"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"resources": []}
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        with pytest.raises(RillAPIError) as exc_info:
            rill_client_with_mocks.reports.get("nonexistent")

        assert "not found" in str(exc_info.value).lower()


@pytest.mark.unit
class TestReportsCreate:
    """Unit tests for create() method"""

    def test_create_report_success(self, rill_client_with_mocks, monkeypatch):
        """Test creating a report successfully"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                # Verify request structure
                assert method == "POST"
                assert "reports" in url
                assert "json" in kwargs
                assert "options" in kwargs["json"]

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "name": "new-report"
                }
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        options = ReportOptions(
            display_name="New Report",
            refresh_cron="0 9 * * 1",
            query_name="test_query",
            export_format=ExportFormat.XLSX
        )

        response = rill_client_with_mocks.reports.create(options)

        assert isinstance(response, CreateReportResponse)
        assert response.name == "new-report"

    def test_create_report_serializes_with_aliases(self, rill_client_with_mocks, monkeypatch):
        """Test that create serializes ReportOptions with camelCase field names"""
        captured_json = {}

        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                # Capture the JSON data sent
                if "json" in kwargs:
                    captured_json.update(kwargs["json"])

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"name": "test"}
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        options = ReportOptions(
            display_name="Test",
            refresh_cron="0 9 * * 1",
            refresh_time_zone="America/New_York"
        )

        rill_client_with_mocks.reports.create(options)

        # Verify camelCase field names in request
        assert "options" in captured_json
        options_data = captured_json["options"]
        assert "displayName" in options_data
        assert "refreshCron" in options_data
        assert "refreshTimeZone" in options_data


@pytest.mark.unit
class TestReportsEdit:
    """Unit tests for edit() method"""

    def test_edit_report_success(self, rill_client_with_mocks, monkeypatch):
        """Test editing a report successfully"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                assert method == "PUT"
                assert "reports" in url
                assert "test-report" in url

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {}
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        options = ReportOptions(
            display_name="Updated Report",
            refresh_cron="0 10 * * *"
        )

        response = rill_client_with_mocks.reports.edit("test-report", options)

        assert isinstance(response, EditReportResponse)


@pytest.mark.unit
class TestReportsDelete:
    """Unit tests for delete() method"""

    def test_delete_report_success(self, rill_client_with_mocks, monkeypatch):
        """Test deleting a report successfully"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                assert method == "DELETE"
                assert "reports" in url
                assert "test-report" in url

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {}
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        response = rill_client_with_mocks.reports.delete("test-report")

        assert isinstance(response, DeleteReportResponse)


@pytest.mark.unit
class TestReportsTrigger:
    """Unit tests for trigger() method"""

    def test_trigger_report_success(self, rill_client_with_mocks, monkeypatch):
        """Test triggering a report successfully"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                assert method == "POST"
                assert "reports" in url
                assert "test-report" in url
                assert "trigger" in url

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {}
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        response = rill_client_with_mocks.reports.trigger("test-report")

        assert isinstance(response, TriggerReportResponse)


@pytest.mark.unit
class TestReportsUnsubscribe:
    """Unit tests for unsubscribe() method"""

    def test_unsubscribe_report_success(self, rill_client_with_mocks, monkeypatch):
        """Test unsubscribing from a report successfully"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                assert method == "POST"
                assert "reports" in url
                assert "test-report" in url
                assert "unsubscribe" in url

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {}
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        response = rill_client_with_mocks.reports.unsubscribe("test-report")

        assert isinstance(response, UnsubscribeReportResponse)


@pytest.mark.unit
class TestReportsGenerateYAML:
    """Unit tests for generate_yaml() method"""

    def test_generate_yaml_success(self, rill_client_with_mocks, monkeypatch):
        """Test generating YAML successfully"""
        def mock_client_init(*args, **kwargs):
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value = mock_instance
            mock_instance.__exit__.return_value = None

            def mock_request(method, url, **kwargs):
                assert method == "POST"
                assert "reports" in url
                assert "yaml" in url

                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "yaml": "type: report\ndisplay_name: Test Report\n"
                }
                return mock_response

            mock_instance.request = mock_request
            return mock_instance

        import httpx
        monkeypatch.setattr(httpx, "Client", mock_client_init)

        options = ReportOptions(
            display_name="Test Report",
            refresh_cron="0 9 * * 1"
        )

        yaml_str = rill_client_with_mocks.reports.generate_yaml(options)

        assert isinstance(yaml_str, str)
        assert "type: report" in yaml_str
        assert "display_name: Test Report" in yaml_str


@pytest.mark.unit
class TestReportsErrorHandling:
    """Unit tests for error handling"""

    def test_list_reports_api_error(self, rill_client_with_mocks, monkeypatch):
        """Test list reports handles API errors"""
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
            rill_client_with_mocks.reports.list()

        assert exc_info.value.status_code == 404

    def test_create_report_validation_error(self, rill_client_with_mocks, monkeypatch):
        """Test create report handles validation errors"""
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

        options = ReportOptions(display_name="Test")

        with pytest.raises(RillAPIError) as exc_info:
            rill_client_with_mocks.reports.create(options)

        assert "Failed to validate" in str(exc_info.value)


@pytest.mark.unit
class TestReportsModels:
    """Unit tests for Report model validation"""

    def test_report_options_accepts_all_fields(self):
        """Test ReportOptions model accepts all expected fields"""
        options = ReportOptions(
            display_name="Full Report",
            refresh_cron="0 9 * * 1",
            refresh_time_zone="America/New_York",
            interval_duration="P7D",
            query_name="test_query",
            query_args_json='{"key": "value"}',
            export_limit=10000,
            export_format=ExportFormat.XLSX,
            export_include_header=True,
            email_recipients=["user@example.com"],
            slack_users=["@user"],
            slack_channels=["#channel"],
            slack_webhooks=["https://hooks.slack.com/..."],
            web_open_path="/explore/dashboard",
            web_open_state="base64string",
            explore="test_explore",
            canvas="test_canvas",
            web_open_mode="creator"
        )

        assert options.display_name == "Full Report"
        assert options.refresh_cron == "0 9 * * 1"
        assert options.export_format == ExportFormat.XLSX
        assert len(options.email_recipients) == 1

    def test_export_format_enum(self):
        """Test ExportFormat enum values"""
        assert ExportFormat.CSV.value == "EXPORT_FORMAT_CSV"
        assert ExportFormat.XLSX.value == "EXPORT_FORMAT_XLSX"
        assert ExportFormat.PARQUET.value == "EXPORT_FORMAT_PARQUET"
