"""User management operations for organizations"""

from typing import List, Optional
from pydantic import ValidationError

from .base import BaseResource
from ..models.users import OrganizationMemberUser
from ..exceptions import RillAPIError, RillAuthError


class UsersResource(BaseResource):
    """Resource for organization user management operations"""

    def list(
        self,
        *,
        org: Optional[str] = None,
        role: Optional[str] = None,
        include_counts: Optional[bool] = None,
        page_size: Optional[int] = None,
        search_pattern: Optional[str] = None
    ) -> List[OrganizationMemberUser]:
        """
        List all members in an organization.

        Args:
            org: Organization name (optional, defaults to client.config.default_org)
            role: Optional filter by role
            include_counts: Optional include project/usergroup counts
            page_size: Optional pagination size
            search_pattern: Optional search by email or display name

        Returns:
            List of OrganizationMemberUser objects

        Raises:
            RillAPIError: If API request fails or validation fails
            RillAuthError: If org cannot be determined

        Example:
            >>> # Most common: use client default org
            >>> users = client.users.list()
            >>> for user in users:
            >>>     print(f"{user.user_email}: {user.role_name}")
            >>>
            >>> # Override org context
            >>> users = client.users.list(org="other-org")
        """
        # Resolve org from defaults
        org_name = org or self._client.config.default_org

        if not org_name:
            raise RillAuthError(
                "Organization is required. "
                "Provide via org parameter or set client default."
            )

        cache_key = ("users", "list", org_name, role, include_counts, page_size, search_pattern)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        endpoint = f"orgs/{org_name}/members"

        # Build query parameters
        params = {}
        if role:
            params["role"] = role
        if include_counts is not None:
            params["includeCounts"] = include_counts
        if page_size:
            params["pageSize"] = page_size
        if search_pattern:
            params["searchPattern"] = search_pattern

        data = self._request("GET", endpoint, params=params)

        try:
            users = [OrganizationMemberUser(**u) for u in data.get("members", [])]
            self._set_cached(cache_key, users)
            return users
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate user data: {e}")

    def get(
        self,
        email: str,
        *,
        org: Optional[str] = None
    ) -> OrganizationMemberUser:
        """
        Get details for a specific organization member by email.

        Args:
            email: User email (required, can be positional or named)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            OrganizationMemberUser object

        Raises:
            RillAPIError: If API request fails or user not found
            RillAuthError: If org cannot be determined

        Example:
            >>> # Most common: use client default org
            >>> user = client.users.get("user@example.com")
            >>> print(user.role_name)
            >>>
            >>> # Override org context
            >>> user = client.users.get("user@example.com", org="other-org")
            >>>
            >>> # Named parameter style
            >>> user = client.users.get(email="user@example.com")
        """
        # Resolve org from defaults
        org_name = org or self._client.config.default_org

        if not org_name:
            raise RillAuthError(
                "Organization is required. "
                "Provide via org parameter or set client default."
            )

        cache_key = ("users", "get", org_name, email)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # List users and filter by email
        users = self.list(org=org_name)

        for user in users:
            if user.user_email == email:
                self._set_cached(cache_key, user)
                return user

        raise RillAPIError(f"User with email '{email}' not found in organization '{org_name}'")

    def show(
        self,
        email: str,
        *,
        org: Optional[str] = None
    ) -> OrganizationMemberUser:
        """
        Get details for a specific organization member by email.

        Alias for get() - provided for compatibility.

        Args:
            email: User email (required, can be positional or named)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            OrganizationMemberUser object

        Raises:
            RillAPIError: If API request fails or user not found
            RillAuthError: If org cannot be determined

        Example:
            >>> user = client.users.show("user@example.com")
            >>> print(user.role_name)
        """
        return self.get(email, org=org)
