"""
Annotations query operations
"""

from typing import Optional
from pydantic import ValidationError

from .base import BaseResource
from ..models.annotations import (
    AnnotationsQuery,
    AnnotationsResponse,
)
from ..exceptions import RillAPIError


class AnnotationsResource(BaseResource):
    """
    Resource for querying annotations from metrics views.

    Annotations are time-based metadata that can be displayed alongside
    metrics to provide context (e.g., product launches, incidents, deployments).

    Example:
        >>> client = RillClient()
        >>> from pyrill.models import AnnotationsQuery, TimeRange, TimeGrain
        >>> query = AnnotationsQuery(
        ...     measures=["revenue"],
        ...     time_range=TimeRange(expression="LAST_30_DAYS"),
        ...     time_grain=TimeGrain.DAY
        ... )
        >>> result = client.annotations.query("revenue_metrics", query)
        >>> for annotation in result.rows:
        ...     print(annotation.time, annotation.description)
    """

    def _resolve_org_project(
        self,
        project: Optional[str],
        org: Optional[str]
    ) -> tuple[str, str]:
        """
        Resolve org and project names from parameters or config defaults.

        Args:
            project: Optional explicit project name
            org: Optional explicit org name

        Returns:
            Tuple of (org_name, project_name)

        Raises:
            RillAPIError: If org or project cannot be resolved
        """
        resolved_org = org or self._client.config.default_org
        resolved_project = project or self._client.config.default_project

        if not resolved_org or not resolved_project:
            missing = []
            if not resolved_org:
                missing.append("org")
            if not resolved_project:
                missing.append("project")

            raise RillAPIError(
                f"Annotations queries require {' and '.join(missing)}. "
                f"Either provide them explicitly or set defaults via "
                f"client configuration."
            )

        return resolved_org, resolved_project

    def query(
        self,
        metrics_view_name: str,  # Required metrics view identifier (positional or named)
        query: AnnotationsQuery,  # Required query object
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> AnnotationsResponse:
        """
        Query annotations for a metrics view.

        Retrieves annotations from the metrics view's configured annotation table,
        optionally filtered by measures, time range, and other parameters.

        Args:
            metrics_view_name: Name of the metrics view (required, can be positional or named)
            query: AnnotationsQuery with query parameters (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            AnnotationsResponse with list of annotations

        Raises:
            RillAPIError: If org/project cannot be resolved or query execution fails

        Example:
            >>> from pyrill.models import AnnotationsQuery, TimeRange, TimeGrain
            >>> # Use defaults (most common)
            >>> query = AnnotationsQuery(
            ...     measures=["revenue", "orders"],
            ...     time_range=TimeRange(expression="LAST_30_DAYS"),
            ...     time_grain=TimeGrain.DAY,
            ...     limit=100
            ... )
            >>> result = client.annotations.query("revenue_metrics", query)
            >>> for annotation in result.rows:
            ...     print(f"{annotation.time}: {annotation.description}")
            ...     if annotation.for_measures:
            ...         print(f"  Applies to: {', '.join(annotation.for_measures)}")

            >>> # Override project context
            >>> result = client.annotations.query("revenue_metrics", query, project="staging")

            >>> # Using a dict instead of AnnotationsQuery
            >>> query_dict = {
            ...     "measures": ["revenue"],
            ...     "time_range": {"expression": "LAST_7_DAYS"},
            ...     "limit": 50
            ... }
            >>> result = client.annotations.query("revenue_metrics", query_dict)
        """
        # Convert dict to AnnotationsQuery if needed
        if isinstance(query, dict):
            try:
                query = AnnotationsQuery(**query)
            except ValidationError as e:
                raise RillAPIError(f"Invalid annotations query: {e}")

        org_name, project_name = self._resolve_org_project(project, org)

        # No caching - query results may be time-sensitive
        endpoint = f"organizations/{org_name}/projects/{project_name}/runtime/queries/metrics-views/{metrics_view_name}/annotations"

        # Convert query to dict, excluding None values for cleaner requests
        query_dict = query.model_dump(exclude_none=True, by_alias=True)

        self.logger.info(
            "Querying annotations",
            org=org_name,
            project=project_name,
            metrics_view=metrics_view_name,
            measures_count=len(query.measures) if query.measures else 0,
            limit=query.limit
        )

        try:
            data = self._request("POST", endpoint, json_data=query_dict)

            # API returns response with rows
            response = AnnotationsResponse(**data)
            return response
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate annotations response: {e}")
