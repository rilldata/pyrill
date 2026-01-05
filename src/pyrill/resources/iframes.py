"""IFrame URL generation operations for embedding Rill dashboards."""

from typing import Optional

from pydantic import ValidationError

from .base import BaseResource
from ..exceptions import RillAPIError
from ..models.iframe import IFrameOptions, IFrameResponse


class IFramesResource(BaseResource):
    """
    Resource for generating authenticated iframe URLs for embedding dashboards.

    IFrames enable embedding Rill dashboards, canvases, or project navigation
    in external applications with JWT-based authentication and optional row-level
    security through custom attributes.

    Example:
        >>> from pyrill import RillClient
        >>> from pyrill.models import IFrameOptions
        >>>
        >>> client = RillClient(org="demo", project="rill-openrtb-prog-ads")
        >>>
        >>> # Generate iframe URL for single dashboard
        >>> options = IFrameOptions(
        ...     resource="auction_metrics",
        ...     user_email="user@example.com"
        ... )
        >>> result = client.iframes.get(options)
        >>> iframe_url = result.iframe_src
    """

    def get(
        self,
        options: IFrameOptions,  # Required configuration (positional or named)
        *,  # Force following to be keyword-only
        project: Optional[str] = None,  # Optional, defaults to client.config.default_project
        org: Optional[str] = None,  # Optional, defaults to client.config.default_org
    ) -> IFrameResponse:
        """
        Generate an authenticated iframe URL for embedding a dashboard.

        Returns an iframe URL with embedded JWT token that can be used to embed
        Rill dashboards, canvases, or project navigation in external applications.

        Args:
            options: IFrameOptions configuration (required, can be positional or named)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            IFrameResponse containing iframe_src URL and authentication details

        Raises:
            RillAPIError: If API request fails or validation fails

        Example:
            >>> from pyrill import RillClient
            >>> from pyrill.models import IFrameOptions
            >>>
            >>> # Initialize client with defaults
            >>> client = RillClient(org="demo", project="rill-openrtb-prog-ads")
            >>>
            >>> # Embed single dashboard (simplest form)
            >>> options = IFrameOptions(
            ...     resource="auction_metrics",
            ...     user_email="user@example.com"
            ... )
            >>> result = client.iframes.get(options)
            >>> iframe_url = result.iframe_src

            >>> # Embed with navigation enabled
            >>> options = IFrameOptions(
            ...     resource="auction_metrics",
            ...     navigation=True,
            ...     user_email="user@example.com"
            ... )
            >>> result = client.iframes.get(options)

            >>> # Embed project list (no specific resource)
            >>> options = IFrameOptions(
            ...     navigation=True,
            ...     user_email="user@example.com"
            ... )
            >>> result = client.iframes.get(options)

            >>> # Custom TTL and theme
            >>> options = IFrameOptions(
            ...     resource="auction_metrics",
            ...     user_email="user@example.com",
            ...     ttl_seconds=3600,
            ...     theme_mode="dark"
            ... )
            >>> result = client.iframes.get(options)

            >>> # Custom attributes for security policies
            >>> options = IFrameOptions(
            ...     resource="auction_metrics",
            ...     attributes={
            ...         "email": "user@example.com",
            ...         "tenant_id": "tenant123",
            ...         "role": "viewer"
            ...     }
            ... )
            >>> result = client.iframes.get(options)

            >>> # Canvas type instead of explore
            >>> options = IFrameOptions(
            ...     resource="my_canvas",
            ...     type="canvas",
            ...     user_email="user@example.com"
            ... )
            >>> result = client.iframes.get(options)

            >>> # Override project context
            >>> result = client.iframes.get(options, project="staging")
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

        # Build endpoint
        endpoint = f"orgs/{org_name}/projects/{project_name}/iframe"

        # Build request body from options
        json_data = options.model_dump(exclude_none=True, by_alias=True)

        # Make API request - POST generates new JWT token each time
        data = self._request("POST", endpoint, json_data=json_data)

        # Validate and return response
        try:
            return IFrameResponse(**data)
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate iframe response: {e}")
