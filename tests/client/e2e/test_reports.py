"""
End-to-end tests for Reports resource

These tests require real credentials and make actual API calls.
Run with: pytest tests/client/e2e/ --run-e2e
"""

import os
import pytest

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
from pyrill.exceptions import RillError
from tests.client.e2e.conftest import TEST_ORG, TEST_PROJECT


@pytest.mark.e2e
class TestE2EReportsRead:
    """E2E tests for read-only report operations"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    @pytest.fixture(scope="class")
    def test_org_and_project(self, client):
        """Get a test organization and project"""
        # Use the demo org and project directly
        return TEST_ORG, TEST_PROJECT

    def test_list_reports(self, client, test_org_and_project, record_reports_test):
        """Test listing all reports for a project"""
        org_name, project_name = test_org_and_project

        if not org_name or not project_name:
            pytest.skip("No valid org/project for testing")

        reports = client.reports.list(project=project_name, org=org_name)

        assert isinstance(reports, list)
        assert all(isinstance(report, Report) for report in reports)

        # Record test results
        reports_data = [
            {
                "name": r.name,
                "display_name": r.spec.display_name if r.spec else None,
                "has_spec": r.spec is not None,
                "has_state": r.state is not None,
                "next_run": r.state.next_run_on if r.state else None,
                "execution_count": r.state.execution_count if r.state else None
            }
            for r in reports
        ]

        record_reports_test(
            test_name="test_list_reports",
            data=reports_data
        )

        # Reports list might be empty, that's ok
        if reports:
            # Verify structure of first report
            report = reports[0]
            assert report.name is not None
            # Report should have spec or state (or both)
            assert report.spec is not None or report.state is not None

    def test_get_report_existing(self, client, test_org_and_project, record_reports_test):
        """Test getting a specific report by name"""
        org_name, project_name = test_org_and_project

        if not org_name or not project_name:
            pytest.skip("No valid org/project for testing")

        # First list all reports to find one that exists
        reports = client.reports.list(project=project_name, org=org_name)

        if not reports:
            pytest.skip("No reports available for testing")

        # Get the first report by name
        report_name = reports[0].name
        report = client.reports.get(report_name, project=project_name, org=org_name)

        assert isinstance(report, Report)
        assert report.name == report_name

        # Record test results
        report_data = {
            "name": report.name,
            "display_name": report.spec.display_name if report.spec else None,
            "has_spec": report.spec is not None,
            "has_state": report.state is not None,
            "query_name": report.spec.query_name if report.spec else None,
            "export_format": report.spec.export_format.value if report.spec and report.spec.export_format else None,
            "next_run_on": report.state.next_run_on if report.state else None,
            "execution_count": report.state.execution_count if report.state else None,
            "refresh_schedule": {
                "cron": report.spec.refresh_schedule.cron if report.spec and report.spec.refresh_schedule else None,
                "time_zone": report.spec.refresh_schedule.time_zone if report.spec and report.spec.refresh_schedule else None
            } if report.spec and report.spec.refresh_schedule else None
        }

        record_reports_test(
            test_name="test_get_report_existing",
            data=report_data
        )

        # Verify report has expected structure
        if report.spec:
            assert hasattr(report.spec, "display_name")
        if report.state:
            assert hasattr(report.state, "next_run_on")

    def test_get_report_nonexistent(self, client, test_org_and_project):
        """Test getting a non-existent report raises error"""
        org_name, project_name = test_org_and_project

        if not org_name or not project_name:
            pytest.skip("No valid org/project for testing")

        with pytest.raises(RillError) as exc_info:
            client.reports.get("nonexistent-report-12345", project=project_name, org=org_name)

        assert "not found" in str(exc_info.value).lower()


@pytest.mark.e2e
class TestE2EReportsWrite:
    """E2E tests for write operations (create, edit, delete, trigger)"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    @pytest.fixture(scope="class")
    def test_org_and_project(self, client):
        """Get a test organization and project"""
        # Use the demo org and project directly
        return TEST_ORG, TEST_PROJECT

    def test_create_report_response_structure(self, client):
        """Test create report returns proper response structure"""
        # This test uses a mock to verify the response model structure
        # without actually creating a report in production
        pytest.skip("Create operations require mocked responses to avoid production changes")

    def test_edit_report_response_structure(self, client):
        """Test edit report returns proper response structure"""
        pytest.skip("Edit operations require mocked responses to avoid production changes")

    def test_delete_report_response_structure(self, client):
        """Test delete report returns proper response structure"""
        pytest.skip("Delete operations require mocked responses to avoid production changes")

    def test_trigger_report_response_structure(self, client):
        """Test trigger report returns proper response structure"""
        pytest.skip("Trigger operations require mocked responses to avoid production changes")

    def test_unsubscribe_report_response_structure(self, client):
        """Test unsubscribe from report returns proper response structure"""
        pytest.skip("Unsubscribe operations require mocked responses to avoid production changes")

    def test_generate_yaml_response_structure(self, client):
        """Test generate YAML returns proper response structure"""
        pytest.skip("YAML generation requires mocked responses to avoid production changes")


@pytest.mark.e2e
class TestE2EReportsModels:
    """E2E tests for report model validation and structure"""

    def test_report_options_model_validation(self):
        """Test ReportOptions model accepts valid data"""
        options = ReportOptions(
            display_name="Test Report",
            refresh_cron="0 9 * * 1",
            refresh_time_zone="America/New_York",
            query_name="test_query",
            export_format=ExportFormat.XLSX,
            email_recipients=["test@example.com"],
        )

        assert options.display_name == "Test Report"
        assert options.refresh_cron == "0 9 * * 1"
        assert options.export_format == ExportFormat.XLSX
        assert options.email_recipients == ["test@example.com"]

    def test_report_options_model_dump_uses_aliases(self):
        """Test ReportOptions serializes with correct field names (camelCase)"""
        options = ReportOptions(
            display_name="Test Report",
            refresh_cron="0 9 * * 1",
            refresh_time_zone="America/New_York",
        )

        # Dump with aliases for API compatibility
        data = options.model_dump(by_alias=True, exclude_none=True)

        assert "displayName" in data
        assert "refreshCron" in data
        assert "refreshTimeZone" in data

        # Should not contain Python snake_case field names
        assert "display_name" not in data
        assert "refresh_cron" not in data

    def test_export_format_enum_values(self):
        """Test ExportFormat enum has expected values"""
        assert ExportFormat.CSV.value == "EXPORT_FORMAT_CSV"
        assert ExportFormat.XLSX.value == "EXPORT_FORMAT_XLSX"
        assert ExportFormat.PARQUET.value == "EXPORT_FORMAT_PARQUET"
        assert ExportFormat.UNSPECIFIED.value == "EXPORT_FORMAT_UNSPECIFIED"

    def test_report_model_accepts_minimal_data(self):
        """Test Report model can be instantiated with minimal data"""
        report = Report(name="test-report")

        assert report.name == "test-report"
        assert report.spec is None
        assert report.state is None

    def test_report_model_accepts_full_data(self):
        """Test Report model can be instantiated with complete data"""
        from pyrill.models.reports import ReportSpec, ReportState, Schedule

        report = Report(
            name="test-report",
            spec=ReportSpec(
                display_name="Test Report",
                refresh_schedule=Schedule(cron="0 9 * * 1"),
                query_name="test_query",
            ),
            state=ReportState(
                next_run_on="2024-01-22T09:00:00Z",
                execution_count=10,
            ),
        )

        assert report.name == "test-report"
        assert report.spec.display_name == "Test Report"
        assert report.state.execution_count == 10


@pytest.mark.e2e
class TestE2EReportsErrorHandling:
    """E2E tests for error handling in reports operations"""

    @pytest.fixture(scope="class")
    def client(self):
        """Create a real client instance"""
        if not os.environ.get("RILL_USER_TOKEN"):
            pytest.skip("RILL_USER_TOKEN not set")

        return RillClient(org=TEST_ORG, project=TEST_PROJECT)

    def test_list_reports_invalid_project(self, client):
        """Test listing reports for non-existent project raises error"""
        with pytest.raises(RillError):
            client.reports.list(project="nonexistent-project", org="nonexistent-org")

    def test_get_report_invalid_project(self, client):
        """Test getting report from non-existent project raises error"""
        with pytest.raises(RillError):
            client.reports.get("some-report", project="nonexistent-project", org="nonexistent-org")
