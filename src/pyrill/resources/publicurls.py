"""
Public URL (Magic Auth Token) operations
"""

from typing import List, Optional, Dict, Any
from pydantic import ValidationError

from .base import BaseResource
from ..models import MagicAuthToken, CreatePublicUrlResponse
from ..exceptions import RillAPIError


class PublicUrlsResource(BaseResource):
    """
    Resource for public URL (Magic Auth Token) operations.

    Magic Auth Tokens enable creation of public URLs to Rill explores,
    allowing unauthenticated access with optional field restrictions and filters.

    Example:
        >>> client = RillClient()
        >>> # List all public URLs
        >>> tokens = client.publicurls.list()
        >>> # Create a public URL for an explore
        >>> result = client.publicurls.create("my_explore", ttl_minutes=1440)
        >>> print(result.url)
        >>> # Delete a public URL
        >>> client.publicurls.delete("tok_abc123")
    """

    def list(
        self,
        *,
        project: Optional[str] = None,
        org: Optional[str] = None,
        page_size: int = 50,
        page_token: Optional[str] = None
    ) -> List[MagicAuthToken]:
        """
        List Magic Auth Tokens (public URLs) for a project.

        Args:
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)
            page_size: Number of tokens per page (default: 50)
            page_token: Pagination token for fetching next page (optional)

        Returns:
            List of MagicAuthToken objects

        Raises:
            RillAPIError: If API request fails or validation fails

        Example:
            >>> # Use defaults (most common)
            >>> tokens = client.publicurls.list()
            >>> for token in tokens:
            >>>     print(token.url)

            >>> # Override project context
            >>> tokens = client.publicurls.list(project="staging")

            >>> # Custom page size
            >>> tokens = client.publicurls.list(page_size=100)
        """
        # Resolve org and project from defaults
        org_name = org or self._client.config.default_org
        project_name = project or self._client.config.default_project

        if not org_name:
            raise RillAPIError(
                "Organization is required. "
                "Provide via org parameter or set client default."
            )

        if not project_name:
            raise RillAPIError(
                "Project is required. "
                "Provide via project parameter or set client default."
            )

        cache_key = ("publicurls", "list", org_name, project_name, page_size, page_token)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        endpoint = f"orgs/{org_name}/projects/{project_name}/tokens/magic"
        params = {
            "pageSize": page_size
        }
        if page_token:
            params["pageToken"] = page_token

        data = self._request("GET", endpoint, params=params)
        try:
            tokens = [MagicAuthToken(**token) for token in data.get("tokens", [])]
            self._set_cached(cache_key, tokens)
            return tokens
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate Magic Auth Token data: {e}")

    def create(
        self,
        explore_name: str,
        *,
        project: Optional[str] = None,
        org: Optional[str] = None,
        ttl_minutes: int = 0,
        filter: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        display_name: Optional[str] = None
    ) -> CreatePublicUrlResponse:
        """
        Create a Magic Auth Token (public URL) for an explore.

        Args:
            explore_name: Name of the explore to create public URL for (required)
            project: Project name (optional, defaults to client.config.default_project)
            org: Organization name (optional, defaults to client.config.default_org)
            ttl_minutes: Duration until expiry in minutes (0 = no expiry, default: 0)
            filter: Optional expression filter to restrict data access
            fields: Optional list of fields to limit access to
            display_name: Optional display name for the token

        Returns:
            CreatePublicUrlResponse with token and URL

        Raises:
            RillAPIError: If API request fails or validation fails

        Example:
            >>> # Create with defaults (no expiry)
            >>> result = client.publicurls.create("my_explore")
            >>> print(result.url)

            >>> # Create with 24-hour expiry
            >>> result = client.publicurls.create("my_explore", ttl_minutes=1440)

            >>> # Create with field restrictions
            >>> result = client.publicurls.create(
            >>>     "my_explore",
            >>>     fields=["revenue", "date"],
            >>>     display_name="Revenue Report"
            >>> )
        """
        # Resolve org and project from defaults
        org_name = org or self._client.config.default_org
        project_name = project or self._client.config.default_project

        if not org_name:
            raise RillAPIError(
                "Organization is required. "
                "Provide via org parameter or set client default."
            )

        if not project_name:
            raise RillAPIError(
                "Project is required. "
                "Provide via project parameter or set client default."
            )

        endpoint = f"orgs/{org_name}/projects/{project_name}/tokens/magic"

        # Build request body according to IssueMagicAuthTokenRequest structure
        request_body: Dict[str, Any] = {
            "resources": [
                {
                    "type": "rill.runtime.v1.Explore",
                    "name": explore_name
                }
            ]
        }

        # Add optional parameters
        if ttl_minutes > 0:
            request_body["ttlMinutes"] = ttl_minutes

        if filter is not None:
            request_body["filter"] = filter

        if fields is not None:
            request_body["fields"] = fields

        if display_name is not None:
            request_body["displayName"] = display_name

        data = self._request("POST", endpoint, json_data=request_body)
        try:
            response = CreatePublicUrlResponse(**data)
            return response
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate public URL creation response: {e}")

    def delete(self, token_id: str) -> None:
        """
        Delete (revoke) a Magic Auth Token.

        Args:
            token_id: The ID of the token to delete (required)

        Returns:
            None

        Raises:
            RillAPIError: If API request fails

        Example:
            >>> client.publicurls.delete("tok_abc123")
        """
        endpoint = f"magic-tokens/{token_id}"
        self._request("DELETE", endpoint)
        # DELETE returns empty response, so no validation needed
