"""
Query operations for executing metrics and SQL queries
"""

from typing import Optional
from pydantic import ValidationError

from .base import BaseResource
from ..models import (
    MetricsQuery,
    MetricsSqlQuery,
    SqlQuery,
    QueryResult,
)
from ..exceptions import RillAPIError, RillAuthError


class QueryResource(BaseResource):
    """
    Resource for query operations against project runtime APIs.

    Requires org and project to be configured in RillClient, or explicit org_name
    and project_name parameters for each query.

    Example:
        >>> # With org and project configured
        >>> client = RillClient(org="my-org", project="my-project")
        >>> query = MetricsQuery(
        ...     metrics_view="ad_bids_metrics",
        ...     dimensions=[Dimension(name="publisher")],
        ...     measures=[Measure(name="bid_price")],
        ...     limit=100
        ... )
        >>> result = client.queries.metrics(query)

        >>> # With explicit org/project
        >>> result = client.queries.metrics(query, org_name="demo", project_name="my-proj")
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
            RillAuthError: If org or project cannot be resolved
        """
        resolved_org = org or self._client.config.default_org
        resolved_project = project or self._client.config.default_project

        if not resolved_org or not resolved_project:
            missing = []
            if not resolved_org:
                missing.append("org")
            if not resolved_project:
                missing.append("project")

            raise RillAuthError(
                f"Query operations require {' and '.join(missing)}. "
                f"Either provide them explicitly or set RILL_DEFAULT_ORG and "
                f"RILL_DEFAULT_PROJECT environment variables (or pass org "
                f"and project to RillClient)."
            )

        return resolved_org, resolved_project

    def _build_runtime_endpoint(
        self,
        org_name: str,
        project_name: str,
        api_path: str
    ) -> str:
        """
        Build runtime API endpoint path.

        Args:
            org_name: Organization name
            project_name: Project name
            api_path: API path (e.g., "metrics", "metrics-sql", "sql")

        Returns:
            Full endpoint path
        """
        return f"organizations/{org_name}/projects/{project_name}/runtime/api/{api_path}"

    def metrics(
        self,
        query: MetricsQuery,  # Required query object
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> QueryResult:
        """
        Execute a structured metrics query.

        This is the main API for querying metrics views with dimensions,
        measures, filters, and time ranges.

        Args:
            query: MetricsQuery request with query parameters (or dict)
            project: Optional project name (defaults to client.config.default_project)
            org: Optional organization name (defaults to client.config.default_org)

        Returns:
            QueryResult with data rows

        Raises:
            RillAuthError: If org/project cannot be resolved
            RillAPIError: If query execution fails

        Example:
            >>> from pyrill.models import (
            ...     MetricsQuery, Dimension, Measure, TimeRange, Sort
            ... )
            >>> # Using Pydantic models with defaults (most common)
            >>> query = MetricsQuery(
            ...     metrics_view="ad_bids_metrics",
            ...     dimensions=[Dimension(name="publisher")],
            ...     measures=[Measure(name="bid_price")],
            ...     time_range=TimeRange(expression="LAST_7_DAYS"),
            ...     sort=[Sort(name="bid_price", desc=True)],
            ...     limit=100
            ... )
            >>> result = client.queries.metrics(query)

            >>> # Or using a dict
            >>> query_dict = {
            ...     "metrics_view": "ad_bids_metrics",
            ...     "dimensions": [{"name": "publisher"}],
            ...     "measures": [{"name": "bid_price"}],
            ...     "limit": 100
            ... }
            >>> result = client.queries.metrics(query_dict)
            >>> for row in result.data:
            ...     print(row["publisher"], row["bid_price"])

            >>> # Override project context
            >>> result = client.queries.metrics(query, project="staging")
        """
        # Convert dict to MetricsQuery if needed
        if isinstance(query, dict):
            try:
                query = MetricsQuery(**query)
            except ValidationError as e:
                raise RillAPIError(f"Invalid metrics query: {e}")

        org_name, project_name = self._resolve_org_project(project, org)

        # Don't cache query results (they may be time-sensitive)
        endpoint = self._build_runtime_endpoint(org_name, project_name, "metrics")

        # Convert query to dict, excluding None values for cleaner requests
        query_dict = query.model_dump(exclude_none=True)

        self.logger.info(
            "Executing metrics query",
            org=org_name,
            project=project_name,
            metrics_view=query.metrics_view,
            dimensions_count=len(query.dimensions) if query.dimensions else 0,
            measures_count=len(query.measures) if query.measures else 0,
            limit=query.limit
        )

        try:
            data = self._request("POST", endpoint, json_data=query_dict)

            # API returns array directly
            if isinstance(data, list):
                return QueryResult(data=data)
            else:
                raise RillAPIError(
                    f"Unexpected response format from metrics query: {type(data)}"
                )
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate query result: {e}")

    def metrics_sql(
        self,
        query: MetricsSqlQuery,  # Required query object
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> QueryResult:
        """
        Execute a SQL query with metrics context.

        Allows SQL queries that reference the metrics view context,
        with optional additional filtering.

        Args:
            query: MetricsSqlQuery with SQL and optional filters (or dict)
            project: Optional project name (defaults to client.config.default_project)
            org: Optional organization name (defaults to client.config.default_org)

        Returns:
            QueryResult with data rows

        Raises:
            RillAuthError: If org/project cannot be resolved
            RillAPIError: If query execution fails

        Example:
            >>> from pyrill.models import MetricsSqlQuery
            >>> # Using Pydantic model with defaults (most common)
            >>> query = MetricsSqlQuery(
            ...     sql="SELECT publisher, SUM(bid_price) as total FROM metrics GROUP BY publisher"
            ... )
            >>> result = client.queries.metrics_sql(query)

            >>> # Or using a dict
            >>> query_dict = {
            ...     "sql": "SELECT publisher, SUM(bid_price) as total FROM metrics GROUP BY publisher"
            ... }
            >>> result = client.queries.metrics_sql(query_dict)

            >>> # Override project context
            >>> result = client.queries.metrics_sql(query, project="staging")
        """
        # Convert dict to MetricsSqlQuery if needed
        if isinstance(query, dict):
            try:
                query = MetricsSqlQuery(**query)
            except ValidationError as e:
                raise RillAPIError(f"Invalid metrics SQL query: {e}")

        org_name, project_name = self._resolve_org_project(project, org)

        endpoint = self._build_runtime_endpoint(org_name, project_name, "metrics-sql")
        query_dict = query.model_dump(exclude_none=True)

        self.logger.info(
            "Executing metrics SQL query",
            org=org_name,
            project=project_name,
            sql_length=len(query.sql)
        )

        try:
            data = self._request("POST", endpoint, json_data=query_dict)

            if isinstance(data, list):
                return QueryResult(data=data)
            else:
                raise RillAPIError(
                    f"Unexpected response format from metrics-sql query: {type(data)}"
                )
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate query result: {e}")

    def sql(
        self,
        query: SqlQuery,  # Required query object
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None       # Optional, defaults to client.config.default_org
    ) -> QueryResult:
        """
        Execute a raw SQL query (admin-only).

        Execute arbitrary SQL against the project's data warehouse.
        Access is restricted to administrators.

        Args:
            query: SqlQuery with SQL and optional connector (or dict)
            project: Optional project name (defaults to client.config.default_project)
            org: Optional organization name (defaults to client.config.default_org)

        Returns:
            QueryResult with data rows

        Raises:
            RillAuthError: If org/project cannot be resolved or insufficient permissions
            RillAPIError: If query execution fails

        Example:
            >>> from pyrill.models import SqlQuery
            >>> # Using Pydantic model with defaults (most common)
            >>> query = SqlQuery(
            ...     sql="SELECT * FROM ad_bids WHERE timestamp > '2024-01-01' LIMIT 100",
            ...     connector="duckdb"
            ... )
            >>> result = client.queries.sql(query)

            >>> # Or using a dict
            >>> query_dict = {
            ...     "sql": "SELECT COUNT(*) FROM ad_bids",
            ...     "connector": "duckdb"
            ... }
            >>> result = client.queries.sql(query_dict)

            >>> # Override project context
            >>> result = client.queries.sql(query, project="staging")
        """
        # Convert dict to SqlQuery if needed
        if isinstance(query, dict):
            try:
                query = SqlQuery(**query)
            except ValidationError as e:
                raise RillAPIError(f"Invalid SQL query: {e}")

        org_name, project_name = self._resolve_org_project(project, org)

        endpoint = self._build_runtime_endpoint(org_name, project_name, "sql")
        query_dict = query.model_dump(exclude_none=True)

        self.logger.info(
            "Executing raw SQL query",
            org=org_name,
            project=project_name,
            sql_length=len(query.sql),
            connector=query.connector
        )

        try:
            data = self._request("POST", endpoint, json_data=query_dict)

            if isinstance(data, list):
                return QueryResult(data=data)
            else:
                raise RillAPIError(
                    f"Unexpected response format from sql query: {type(data)}"
                )
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate query result: {e}")
