"""
Project-related operations
"""

from typing import List, Optional, Dict, Any
from pydantic import ValidationError

from .base import BaseResource
from ..models import Project, ProjectResources, ProjectStatus, ProjectStatusInfo, DeploymentStatusInfo
from ..exceptions import RillAPIError


class ProjectsResource(BaseResource):
    """
    Resource for project operations.

    Example:
        >>> client = RillClient()
        >>> projects = client.projects.list(org_name="my-org")
        >>> project = client.projects.get("my-project", org_name="my-org")
        >>> resources = client.projects.get_resources("my-org", "my-project")
    """

    def list(self, org_name: Optional[str] = None) -> List[Project]:
        """
        List projects. If org_name is provided, lists projects for that org.

        Args:
            org_name: Optional organization name to filter projects

        Returns:
            List of Project objects.

        Example:
            >>> projects = client.projects.list(org_name="my-org")
            >>> for project in projects:
            >>>     print(project.name)
        """
        cache_key = ("projects", "list", org_name)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if org_name:
            # Use the org-specific endpoint
            endpoint = f"orgs/{org_name}/projects"
            data = self._request("GET", endpoint)
            try:
                projects = [Project(**proj) for proj in data.get("projects", [])]
                self._set_cached(cache_key, projects)
                return projects
            except ValidationError as e:
                raise RillAPIError(f"Failed to validate project data: {e}")
        else:
            # Get all projects across all orgs
            # Strategy: list all orgs, then list projects for each org
            from .orgs import OrgsResource
            orgs_resource = OrgsResource(self._client)
            orgs = orgs_resource.list()
            all_projects = []
            for org in orgs:
                endpoint = f"orgs/{org.name}/projects"
                data = self._request("GET", endpoint)
                all_projects.extend(data.get("projects", []))

            try:
                projects = [Project(**proj) for proj in all_projects]
                self._set_cached(cache_key, projects)
                return projects
            except ValidationError as e:
                raise RillAPIError(f"Failed to validate project data: {e}")

    def get(self, project_name: str, org_name: Optional[str] = None) -> Project:
        """
        Get details for a specific project.

        Args:
            project_name: Name of the project
            org_name: Optional organization name for filtering

        Returns:
            Project object

        Example:
            >>> project = client.projects.get("my-project", org_name="my-org")
            >>> print(project.frontend_url)
        """
        cache_key = ("projects", "get", org_name, project_name)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if org_name:
            # Direct API call
            endpoint = f"orgs/{org_name}/projects/{project_name}"
            data = self._request("GET", endpoint)
            try:
                project = Project(**data.get("project", {}))
                self._set_cached(cache_key, project)
                return project
            except ValidationError as e:
                raise RillAPIError(f"Failed to validate project data: {e}")
        else:
            # Fallback: list all projects and filter
            # This is less efficient but handles case where org is unknown
            projects = self.list(org_name=None)
            for project in projects:
                if project.name == project_name:
                    self._set_cached(cache_key, project)
                    return project
            raise RillAPIError(f"Project '{project_name}' not found")

    def get_resources(
        self,
        project_name: str,  # Required resource identifier (positional or named)
        *,  # Force following to be keyword-only
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> ProjectResources:
        """
        Get runtime resources for a project.

        Args:
            project_name: Project name (required, can be positional or named)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            ProjectResources object

        Raises:
            RillAPIError: If API request fails or validation fails

        Example:
            >>> # Use defaults (most common)
            >>> resources = client.projects.get_resources("my-project")
            >>> print(len(resources.resources))

            >>> # Override org context
            >>> resources = client.projects.get_resources("my-project", org="other-org")
        """
        # Resolve org from defaults
        org_name = org or self._client.config.default_org

        if not org_name:
            raise RillAPIError(
                "Organization is required. "
                "Provide via org parameter or set client default."
            )

        cache_key = ("projects", "get_resources", org_name, project_name)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        endpoint = f"organizations/{org_name}/projects/{project_name}/runtime/resources"
        data = self._request("GET", endpoint)
        try:
            resources = ProjectResources(**data)
            self._set_cached(cache_key, resources)
            return resources
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate runtime resources data: {e}")

    def status(
        self,
        project_name: str,  # Required resource identifier (positional or named)
        *,  # Force following to be keyword-only
        org: Optional[str] = None  # Optional, defaults to client.config.default_org
    ) -> ProjectStatus:
        """
        Get detailed status information for a specific project.

        Args:
            project_name: Name of the project (required, can be positional or named)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            ProjectStatus object with project and deployment status information

        Raises:
            RillAPIError: If API request fails or validation fails

        Example:
            >>> # Use defaults (most common)
            >>> status = client.projects.status("my-project")
            >>> print(status.project.name)
            >>> print(status.deployment.status)

            >>> # Override org context
            >>> status = client.projects.status("my-project", org="other-org")
        """
        # Resolve org from defaults
        org_name = org or self._client.config.default_org

        if not org_name:
            raise RillAPIError(
                "Organization is required. "
                "Provide via org parameter or set client default."
            )

        cache_key = ("projects", "status", org_name, project_name)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        endpoint = f"orgs/{org_name}/projects/{project_name}"
        data = self._request("GET", endpoint)

        # Extract status information
        project_data = data.get("project", {})
        deployment_data = data.get("prodDeployment", {})

        try:
            status = ProjectStatus(
                project=ProjectStatusInfo(
                    name=project_data.get("name"),
                    org=project_data.get("orgName"),
                    description=project_data.get("description"),
                    public=project_data.get("public"),
                    frontend_url=project_data.get("frontendUrl"),
                ),
                deployment=DeploymentStatusInfo(
                    id=deployment_data.get("id"),
                    status=deployment_data.get("status"),
                    status_message=deployment_data.get("statusMessage"),
                    runtime_host=deployment_data.get("runtimeHost"),
                    runtime_instance_id=deployment_data.get("runtimeInstanceId"),
                    branch=deployment_data.get("branch"),
                    created_on=deployment_data.get("createdOn"),
                    updated_on=deployment_data.get("updatedOn"),
                )
            )
            self._set_cached(cache_key, status)
            return status
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate project status data: {e}")
