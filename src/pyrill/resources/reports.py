"""
Report schedule management operations
"""

from typing import List, Optional
from pydantic import ValidationError

from .base import BaseResource
from ..models.reports import (
    Report,
    ReportOptions,
    CreateReportResponse,
    EditReportResponse,
    DeleteReportResponse,
    TriggerReportResponse,
    UnsubscribeReportResponse,
    GenerateReportYAMLResponse,
)
from ..exceptions import RillAPIError


class ReportsResource(BaseResource):
    """
    Resource for report schedule management operations.

    Reports are scheduled exports of query results that can be delivered
    via email, Slack, or other notification channels.

    Example:
        >>> client = RillClient()
        >>> # List all reports
        >>> reports = client.reports.list("my-org", "my-project")
        >>> # Get specific report
        >>> report = client.reports.get("my-org", "my-project", "weekly-summary")
        >>> # Create new report
        >>> options = ReportOptions(
        ...     display_name="Weekly Report",
        ...     refresh_cron="0 9 * * 1",
        ...     query_name="revenue_metrics"
        ... )
        >>> response = client.reports.create("my-org", "my-project", options)
    """

    def list(
        self,
        *,  # Force all parameters to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> List[Report]:
        """
        List all reports for a project.

        Reports are accessed via the runtime resources endpoint and filtered
        by type "rill.runtime.v1.Report".

        Args:
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            List of Report objects

        Raises:
            RillAPIError: If API request fails or validation fails

        Example:
            >>> # Use defaults (most common)
            >>> reports = client.reports.list()
            >>> for report in reports:
            ...     print(f"{report.name}: {report.spec.display_name}")

            >>> # Override project context
            >>> reports = client.reports.list(project="staging")

            >>> # Override both
            >>> reports = client.reports.list(project="my-project", org="my-org")
        """
        # Resolve org and project from defaults
        org_name = org or self._client.config.default_org
        project_name = project or self._client.config.default_project

        if not org_name or not project_name:
            missing = []
            if not org_name:
                missing.append("org")
            if not project_name:
                missing.append("project")
            raise RillAPIError(
                f"Organization and project are required. "
                f"Missing: {', '.join(missing)}. "
                f"Provide via method parameters or set client defaults."
            )

        # No caching - reports change frequently
        endpoint = f"organizations/{org_name}/projects/{project_name}/runtime/resources"
        data = self._request("GET", endpoint)

        # Filter for reports only
        report_resources = [
            r for r in data.get("resources", [])
            if r.get("meta", {}).get("name", {}).get("kind") == "rill.runtime.v1.Report"
        ]

        # Convert to Report models
        try:
            reports = []
            for resource in report_resources:
                # Extract report data from the resource
                report_data = resource.get("report", {})
                # Extract name from meta
                name = resource.get("meta", {}).get("name", {}).get("name")
                if name:
                    report_data["name"] = name
                reports.append(Report(**report_data))
            return reports
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate report data: {e}")

    def get(
        self,
        report_name: str,  # Required resource identifier (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> Report:
        """
        Get a specific report by name.

        Args:
            report_name: Report name (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            Report object

        Raises:
            RillAPIError: If report not found or validation fails

        Example:
            >>> # Use defaults (most common)
            >>> report = client.reports.get("weekly-summary")
            >>> print(report.spec.display_name)
            >>> print(report.state.next_run_on)

            >>> # Override project context
            >>> report = client.reports.get("weekly-summary", project="staging")

            >>> # Override both
            >>> report = client.reports.get("weekly-summary", project="my-project", org="my-org")
        """
        # No caching - report state changes frequently
        reports = self.list(project=project, org=org)

        for report in reports:
            if report.name == report_name:
                return report

        raise RillAPIError(f"Report '{report_name}' not found")

    def create(
        self,
        options: ReportOptions,  # Required configuration (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> CreateReportResponse:
        """
        Create a new scheduled report.

        Args:
            options: Report configuration options (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            CreateReportResponse with the created report name

        Raises:
            RillAPIError: If creation fails

        Example:
            >>> options = ReportOptions(
            ...     display_name="Daily Sales Report",
            ...     refresh_cron="0 9 * * *",
            ...     refresh_time_zone="America/New_York",
            ...     query_name="sales_metrics",
            ...     export_format=ExportFormat.XLSX,
            ...     email_recipients=["team@example.com"]
            ... )
            >>> # Use defaults (most common)
            >>> response = client.reports.create(options)
            >>> print(f"Created report: {response.name}")

            >>> # Override project context
            >>> response = client.reports.create(options, project="staging")
        """
        # Resolve org and project from defaults
        org_name = org or self._client.config.default_org
        project_name = project or self._client.config.default_project

        if not org_name or not project_name:
            missing = []
            if not org_name:
                missing.append("org")
            if not project_name:
                missing.append("project")
            raise RillAPIError(
                f"Organization and project are required. "
                f"Missing: {', '.join(missing)}. "
                f"Provide via method parameters or set client defaults."
            )

        endpoint = f"orgs/{org_name}/projects/{project_name}/reports"
        # Convert Pydantic model to dict using model_dump with by_alias to use API field names
        json_data = {"options": options.model_dump(by_alias=True, exclude_none=True)}
        data = self._request("POST", endpoint, json_data=json_data)

        try:
            return CreateReportResponse(**data)
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate create report response: {e}")

    def edit(
        self,
        report_name: str,  # Required resource identifier (positional or named)
        options: ReportOptions,  # Required configuration
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> EditReportResponse:
        """
        Edit an existing report's configuration.

        Args:
            report_name: Report name to edit (required, can be positional or named)
            options: Updated report configuration options (required)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            EditReportResponse

        Raises:
            RillAPIError: If edit fails

        Example:
            >>> options = ReportOptions(
            ...     display_name="Updated Report Name",
            ...     refresh_cron="0 10 * * *"  # Change time to 10am
            ... )
            >>> # Use defaults (most common)
            >>> client.reports.edit("weekly-summary", options)

            >>> # Override project context
            >>> client.reports.edit("weekly-summary", options, project="staging")
        """
        # Resolve org and project from defaults
        org_name = org or self._client.config.default_org
        project_name = project or self._client.config.default_project

        if not org_name or not project_name:
            missing = []
            if not org_name:
                missing.append("org")
            if not project_name:
                missing.append("project")
            raise RillAPIError(
                f"Organization and project are required. "
                f"Missing: {', '.join(missing)}. "
                f"Provide via method parameters or set client defaults."
            )

        endpoint = f"orgs/{org_name}/projects/{project_name}/reports/{report_name}"
        json_data = {"options": options.model_dump(by_alias=True, exclude_none=True)}
        data = self._request("PUT", endpoint, json_data=json_data)

        try:
            return EditReportResponse(**data)
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate edit report response: {e}")

    def delete(
        self,
        report_name: str,  # Required resource identifier (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> DeleteReportResponse:
        """
        Delete a report.

        Args:
            report_name: Report name to delete (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            DeleteReportResponse

        Raises:
            RillAPIError: If deletion fails

        Example:
            >>> # Use defaults (most common)
            >>> client.reports.delete("old-report")

            >>> # Override project context
            >>> client.reports.delete("old-report", project="staging")
        """
        # Resolve org and project from defaults
        org_name = org or self._client.config.default_org
        project_name = project or self._client.config.default_project

        if not org_name or not project_name:
            missing = []
            if not org_name:
                missing.append("org")
            if not project_name:
                missing.append("project")
            raise RillAPIError(
                f"Organization and project are required. "
                f"Missing: {', '.join(missing)}. "
                f"Provide via method parameters or set client defaults."
            )

        endpoint = f"orgs/{org_name}/projects/{project_name}/reports/{report_name}"
        data = self._request("DELETE", endpoint)

        try:
            return DeleteReportResponse(**data)
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate delete report response: {e}")

    def trigger(
        self,
        report_name: str,  # Required resource identifier (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> TriggerReportResponse:
        """
        Trigger an ad-hoc execution of a report.

        Args:
            report_name: Report name to trigger (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            TriggerReportResponse

        Raises:
            RillAPIError: If trigger fails

        Example:
            >>> # Use defaults (most common)
            >>> client.reports.trigger("weekly-summary")

            >>> # Override project context
            >>> client.reports.trigger("weekly-summary", project="staging")
        """
        # Resolve org and project from defaults
        org_name = org or self._client.config.default_org
        project_name = project or self._client.config.default_project

        if not org_name or not project_name:
            missing = []
            if not org_name:
                missing.append("org")
            if not project_name:
                missing.append("project")
            raise RillAPIError(
                f"Organization and project are required. "
                f"Missing: {', '.join(missing)}. "
                f"Provide via method parameters or set client defaults."
            )

        endpoint = f"orgs/{org_name}/projects/{project_name}/reports/{report_name}/trigger"
        data = self._request("POST", endpoint, json_data={})

        try:
            return TriggerReportResponse(**data)
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate trigger report response: {e}")

    def unsubscribe(
        self,
        report_name: str,  # Required resource identifier (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> UnsubscribeReportResponse:
        """
        Unsubscribe the current user from a report's recipient list.

        Args:
            report_name: Report name to unsubscribe from (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            UnsubscribeReportResponse

        Raises:
            RillAPIError: If unsubscribe fails

        Example:
            >>> # Use defaults (most common)
            >>> client.reports.unsubscribe("weekly-summary")

            >>> # Override project context
            >>> client.reports.unsubscribe("weekly-summary", project="staging")
        """
        # Resolve org and project from defaults
        org_name = org or self._client.config.default_org
        project_name = project or self._client.config.default_project

        if not org_name or not project_name:
            missing = []
            if not org_name:
                missing.append("org")
            if not project_name:
                missing.append("project")
            raise RillAPIError(
                f"Organization and project are required. "
                f"Missing: {', '.join(missing)}. "
                f"Provide via method parameters or set client defaults."
            )

        endpoint = f"orgs/{org_name}/projects/{project_name}/reports/{report_name}/unsubscribe"
        data = self._request("POST", endpoint, json_data={})

        try:
            return UnsubscribeReportResponse(**data)
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate unsubscribe report response: {e}")

    def generate_yaml(
        self,
        options: ReportOptions,  # Required configuration (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> str:
        """
        Generate YAML definition for a report to be copied into a Git repository.

        This allows reports created via the UI to be version-controlled in code.

        Args:
            options: Report configuration options (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            YAML string representation of the report

        Raises:
            RillAPIError: If generation fails

        Example:
            >>> options = ReportOptions(
            ...     display_name="Weekly Report",
            ...     refresh_cron="0 9 * * 1",
            ...     query_name="revenue_metrics"
            ... )
            >>> # Use defaults (most common)
            >>> yaml_str = client.reports.generate_yaml(options)
            >>> print(yaml_str)

            >>> # Override project context
            >>> yaml_str = client.reports.generate_yaml(options, project="staging")
        """
        # Resolve org and project from defaults
        org_name = org or self._client.config.default_org
        project_name = project or self._client.config.default_project

        if not org_name or not project_name:
            missing = []
            if not org_name:
                missing.append("org")
            if not project_name:
                missing.append("project")
            raise RillAPIError(
                f"Organization and project are required. "
                f"Missing: {', '.join(missing)}. "
                f"Provide via method parameters or set client defaults."
            )

        endpoint = f"orgs/{org_name}/projects/{project_name}/reports/-/yaml"
        json_data = {"options": options.model_dump(by_alias=True, exclude_none=True)}
        data = self._request("POST", endpoint, json_data=json_data)

        try:
            response = GenerateReportYAMLResponse(**data)
            return response.yaml
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate generate YAML response: {e}")
