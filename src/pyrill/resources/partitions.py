"""
Partition-related operations
"""

from typing import List, Optional
from pydantic import ValidationError

from .base import BaseResource
from ..models.partitions import ModelPartition, PartitionsList
from ..exceptions import RillAPIError, RillAuthError


class PartitionsResource(BaseResource):
    """
    Resource for partition operations.

    Provides access to model partition information for partitioned models.

    Example:
        >>> client = RillClient(org="my-org", project="my-project")
        >>>
        >>> # Uses client defaults - most common case
        >>> partitions = client.partitions.list("my_model")
        >>>
        >>> # Override project only
        >>> partitions = client.partitions.list("my_model", project="staging")
        >>>
        >>> # Override both
        >>> partitions = client.partitions.list("my_model", project="proj", org="org2")
        >>>
        >>> # Get up to 400 partitions with automatic pagination
        >>> partitions = client.partitions.list("my_model", limit=400)
        >>>
        >>> # Filter for only errored partitions
        >>> errors = client.partitions.list("my_model", errored=True)
    """

    def list(
        self,
        model: str,  # REQUIRED - resource identifier (can be positional or named)
        *,  # Force following params to be keyword-only
        project: Optional[str] = None,  # Optional - defaults to client.config.default_project
        org: Optional[str] = None,      # Optional - defaults to client.config.default_org
        pending: Optional[bool] = None,
        errored: Optional[bool] = None,
        limit: Optional[int] = None,
        page_size: int = 50
    ) -> List[ModelPartition]:
        """
        List partitions for a model.

        Fetches partition details including execution state, watermarks, and errors.
        Supports automatic pagination to retrieve up to 400 partitions in a single call.

        Args:
            model: Model name (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)
            pending: Filter for pending partitions only
            errored: Filter for errored partitions only
            limit: Maximum number of partitions to return (supports up to 400).
                   If None, returns single page (page_size partitions).
                   If specified, automatically paginates until limit is reached.
            page_size: Number of partitions per API request (default: 50)

        Returns:
            List of ModelPartition objects

        Raises:
            RillAPIError: If API request fails or validation fails
            RillAuthError: If org or project cannot be determined

        Example:
            >>> # Most common: use defaults
            >>> partitions = client.partitions.list("sales_model")
            >>>
            >>> # Override project context
            >>> partitions = client.partitions.list("sales_model", project="staging")
            >>>
            >>> # Get up to 400 partitions with automatic pagination
            >>> all_partitions = client.partitions.list("sales_model", limit=400)
            >>>
            >>> # Get only errored partitions
            >>> errors = client.partitions.list("sales_model", errored=True)
        """
        # NO CACHING - partitions need to be up-to-date

        # Resolve org and project from defaults
        org_name = org or self._client.config.default_org
        project_name = project or self._client.config.default_project

        if not org_name or not project_name:
            raise RillAuthError(
                "Organization and project are required. "
                "Provide via method parameters or set client defaults."
            )

        # Build query parameters
        params = {}
        if pending is not None:
            params["pending"] = pending
        if errored is not None:
            params["errored"] = errored
        params["pageSize"] = page_size

        # Handle pagination
        all_partitions = []
        page_token = None
        request_count = 0

        while True:
            request_count += 1
            if page_token:
                params["pageToken"] = page_token

            # Make request using runtime route
            endpoint = f"orgs/{org_name}/projects/{project_name}/runtime/models/{model}/partitions"

            # DEBUG: Log request details
            import json
            import os
            debug_dir = os.path.expanduser("~/RillGitHub/pyrill-workspace/pyrill-tests/tests/debug/partitions")
            os.makedirs(debug_dir, exist_ok=True)

            full_url = f"{self._client.api_base_url}{endpoint}"
            request_debug = {
                "request_number": request_count,
                "method": "GET",
                "endpoint": endpoint,
                "full_url": full_url,
                "params": params.copy(),
                "page_token_sent": page_token
            }

            try:
                data = self._request("GET", endpoint, params=params)
                request_debug["response"] = data
                request_debug["success"] = True
            except Exception as e:
                request_debug["response"] = None
                request_debug["success"] = False
                request_debug["error"] = str(e)
                request_debug["error_type"] = type(e).__name__

                with open(f"{debug_dir}/api_request_{request_count}_ERROR.json", "w") as f:
                    json.dump(request_debug, f, indent=2, default=str)
                raise

            with open(f"{debug_dir}/api_request_{request_count}.json", "w") as f:
                json.dump(request_debug, f, indent=2, default=str)

            # Parse response
            try:
                response = PartitionsList(**data)
            except ValidationError as e:
                raise RillAPIError(f"Failed to validate partition data: {e}")

            all_partitions.extend(response.partitions)

            # Check if we should continue paginating
            if limit is not None and len(all_partitions) >= limit:
                # Truncate to exact limit
                return all_partitions[:limit]

            # Check if more pages available
            if not response.next_page_token:
                break

            # If no limit specified, return first page only
            if limit is None:
                break

            page_token = response.next_page_token

        return all_partitions
