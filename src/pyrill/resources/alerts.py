"""
Alert management operations
"""

from typing import List, Optional
from pydantic import ValidationError

from .base import BaseResource
from ..models.alerts import (
    Alert,
    AlertOptions,
    CreateAlertResponse,
    EditAlertResponse,
    DeleteAlertResponse,
    UnsubscribeAlertResponse,
    GetAlertYAMLResponse,
    GenerateAlertYAMLResponse,
)
from ..exceptions import RillAPIError


class AlertsResource(BaseResource):
    """
    Resource for alert management operations.

    Alerts are monitoring configurations that check metrics and trigger
    notifications when conditions are met.

    Example:
        >>> client = RillClient()
        >>> # List all alerts
        >>> alerts = client.alerts.list()
        >>> # Get specific alert
        >>> alert = client.alerts.get("revenue-drop")
        >>> # Create new alert
        >>> options = AlertOptions(
        ...     display_name="Revenue Drop Alert",
        ...     refresh_cron="0 * * * *",
        ...     resolver="metrics_threshold",
        ...     metrics_view_name="revenue_metrics"
        ... )
        >>> response = client.alerts.create(options)
    """

    def list(
        self,
        *,  # Force all parameters to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> List[Alert]:
        """
        List all alerts for a project.

        Alerts are accessed via the runtime resources endpoint and filtered
        by type "rill.runtime.v1.Alert".

        Args:
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            List of Alert objects

        Raises:
            RillAPIError: If API request fails or validation fails

        Example:
            >>> # Use defaults (most common)
            >>> alerts = client.alerts.list()
            >>> for alert in alerts:
            ...     print(f"{alert.name}: {alert.spec.display_name}")

            >>> # Override project context
            >>> alerts = client.alerts.list(project="staging")

            >>> # Override both
            >>> alerts = client.alerts.list(project="my-project", org="my-org")
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

        # No caching - alerts change frequently
        endpoint = f"organizations/{org_name}/projects/{project_name}/runtime/resources"
        data = self._request("GET", endpoint)

        # Filter for alerts only
        alert_resources = [
            r for r in data.get("resources", [])
            if r.get("meta", {}).get("name", {}).get("kind") == "rill.runtime.v1.Alert"
        ]

        # Convert to Alert models
        try:
            alerts = []
            for resource in alert_resources:
                # Extract alert data from the resource
                alert_data = resource.get("alert", {})
                # Extract name from meta
                name = resource.get("meta", {}).get("name", {}).get("name")
                if name:
                    alert_data["name"] = name
                alerts.append(Alert(**alert_data))
            return alerts
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate alert data: {e}")

    def get(
        self,
        alert_name: str,  # Required resource identifier (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> Alert:
        """
        Get a specific alert by name.

        Args:
            alert_name: Alert name (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            Alert object

        Raises:
            RillAPIError: If alert not found or validation fails

        Example:
            >>> # Use defaults (most common)
            >>> alert = client.alerts.get("revenue-drop")
            >>> print(alert.spec.display_name)
            >>> print(alert.state.next_run_on)

            >>> # Override project context
            >>> alert = client.alerts.get("revenue-drop", project="staging")

            >>> # Override both
            >>> alert = client.alerts.get("revenue-drop", project="my-project", org="my-org")
        """
        # No caching - alert state changes frequently
        alerts = self.list(project=project, org=org)

        for alert in alerts:
            if alert.name == alert_name:
                return alert

        raise RillAPIError(f"Alert '{alert_name}' not found")

    def create(
        self,
        options: AlertOptions,  # Required configuration (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> CreateAlertResponse:
        """
        Create a new alert.

        Args:
            options: Alert configuration options (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            CreateAlertResponse with the created alert name

        Raises:
            RillAPIError: If creation fails

        Example:
            >>> options = AlertOptions(
            ...     display_name="Revenue Drop Alert",
            ...     refresh_cron="0 * * * *",
            ...     refresh_time_zone="America/New_York",
            ...     resolver="metrics_threshold",
            ...     metrics_view_name="revenue_metrics",
            ...     email_recipients=["team@example.com"]
            ... )
            >>> # Use defaults (most common)
            >>> response = client.alerts.create(options)
            >>> print(f"Created alert: {response.name}")

            >>> # Override project context
            >>> response = client.alerts.create(options, project="staging")
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

        endpoint = f"orgs/{org_name}/projects/{project_name}/alerts"
        # Convert Pydantic model to dict using model_dump with by_alias to use API field names
        json_data = {"options": options.model_dump(by_alias=True, exclude_none=True)}
        data = self._request("POST", endpoint, json_data=json_data)

        try:
            return CreateAlertResponse(**data)
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate create alert response: {e}")

    def edit(
        self,
        alert_name: str,  # Required resource identifier (positional or named)
        options: AlertOptions,  # Required configuration
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> EditAlertResponse:
        """
        Edit an existing alert's configuration.

        Args:
            alert_name: Alert name to edit (required, can be positional or named)
            options: Updated alert configuration options (required)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            EditAlertResponse

        Raises:
            RillAPIError: If edit fails

        Example:
            >>> options = AlertOptions(
            ...     display_name="Updated Alert Name",
            ...     refresh_cron="0 */2 * * *"  # Change to every 2 hours
            ... )
            >>> # Use defaults (most common)
            >>> client.alerts.edit("revenue-drop", options)

            >>> # Override project context
            >>> client.alerts.edit("revenue-drop", options, project="staging")
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

        endpoint = f"orgs/{org_name}/projects/{project_name}/alerts/{alert_name}"
        json_data = {"options": options.model_dump(by_alias=True, exclude_none=True)}
        data = self._request("PUT", endpoint, json_data=json_data)

        try:
            return EditAlertResponse(**data)
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate edit alert response: {e}")

    def delete(
        self,
        alert_name: str,  # Required resource identifier (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> DeleteAlertResponse:
        """
        Delete an alert.

        Args:
            alert_name: Alert name to delete (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            DeleteAlertResponse

        Raises:
            RillAPIError: If deletion fails

        Example:
            >>> # Use defaults (most common)
            >>> client.alerts.delete("old-alert")

            >>> # Override project context
            >>> client.alerts.delete("old-alert", project="staging")
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

        endpoint = f"orgs/{org_name}/projects/{project_name}/alerts/{alert_name}"
        data = self._request("DELETE", endpoint)

        try:
            return DeleteAlertResponse(**data)
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate delete alert response: {e}")

    def unsubscribe(
        self,
        alert_name: str,  # Required resource identifier (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> UnsubscribeAlertResponse:
        """
        Unsubscribe the current user from an alert's recipient list.

        Args:
            alert_name: Alert name to unsubscribe from (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            UnsubscribeAlertResponse

        Raises:
            RillAPIError: If unsubscribe fails

        Example:
            >>> # Use defaults (most common)
            >>> client.alerts.unsubscribe("revenue-drop")

            >>> # Override project context
            >>> client.alerts.unsubscribe("revenue-drop", project="staging")
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

        endpoint = f"orgs/{org_name}/projects/{project_name}/alerts/{alert_name}/unsubscribe"
        data = self._request("POST", endpoint, json_data={})

        try:
            return UnsubscribeAlertResponse(**data)
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate unsubscribe alert response: {e}")

    def get_yaml(
        self,
        alert_name: str,  # Required resource identifier (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> str:
        """
        Get the YAML definition for an existing alert.

        Args:
            alert_name: Alert name (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            YAML string representation of the alert

        Raises:
            RillAPIError: If retrieval fails

        Example:
            >>> # Use defaults (most common)
            >>> yaml_str = client.alerts.get_yaml("revenue-drop")
            >>> print(yaml_str)

            >>> # Override project context
            >>> yaml_str = client.alerts.get_yaml("revenue-drop", project="staging")
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

        endpoint = f"orgs/{org_name}/projects/{project_name}/alerts/{alert_name}/yaml"
        data = self._request("GET", endpoint)

        try:
            response = GetAlertYAMLResponse(**data)
            return response.yaml
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate get YAML response: {e}")

    def generate_yaml(
        self,
        options: AlertOptions,  # Required configuration (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> str:
        """
        Generate YAML definition for an alert to be copied into a Git repository.

        This allows alerts created via the UI to be version-controlled in code.

        Args:
            options: Alert configuration options (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            YAML string representation of the alert

        Raises:
            RillAPIError: If generation fails

        Example:
            >>> options = AlertOptions(
            ...     display_name="Revenue Drop Alert",
            ...     refresh_cron="0 * * * *",
            ...     resolver="metrics_threshold",
            ...     metrics_view_name="revenue_metrics"
            ... )
            >>> # Use defaults (most common)
            >>> yaml_str = client.alerts.generate_yaml(options)
            >>> print(yaml_str)

            >>> # Override project context
            >>> yaml_str = client.alerts.generate_yaml(options, project="staging")
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

        endpoint = f"orgs/{org_name}/projects/{project_name}/alerts/-/yaml"
        json_data = {"options": options.model_dump(by_alias=True, exclude_none=True)}
        data = self._request("POST", endpoint, json_data=json_data)

        try:
            response = GenerateAlertYAMLResponse(**data)
            return response.yaml
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate generate YAML response: {e}")
