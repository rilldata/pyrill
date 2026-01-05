"""Usergroup management operations for organizations"""

from typing import List, Optional
from pydantic import ValidationError

from .base import BaseResource
from ..models.users import MemberUsergroup, Usergroup
from ..exceptions import RillAPIError, RillAuthError


class UsergroupsResource(BaseResource):
    """Resource for organization usergroup management operations"""

    def list(
        self,
        *,
        org: Optional[str] = None,
        role: Optional[str] = None,
        include_counts: Optional[bool] = None,
        page_size: Optional[int] = None
    ) -> List[MemberUsergroup]:
        """
        List all usergroups in an organization.

        Args:
            org: Organization name (optional, defaults to client.config.default_org)
            role: Optional filter by role
            include_counts: Optional include user counts
            page_size: Optional pagination size

        Returns:
            List of MemberUsergroup objects

        Raises:
            RillAPIError: If API request fails or validation fails
            RillAuthError: If org cannot be determined

        Example:
            >>> # Most common: use client default org
            >>> groups = client.usergroups.list()
            >>> for group in groups:
            >>>     print(f"{group.group_name}: {group.users_count} users")
            >>>
            >>> # Override org context
            >>> groups = client.usergroups.list(org="other-org")
        """
        # Resolve org from defaults
        org_name = org or self._client.config.default_org

        if not org_name:
            raise RillAuthError(
                "Organization is required. "
                "Provide via org parameter or set client default."
            )

        cache_key = ("usergroups", "list", org_name, role, include_counts, page_size)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        endpoint = f"orgs/{org_name}/usergroups"

        # Build query parameters
        params = {}
        if role:
            params["role"] = role
        if include_counts is not None:
            params["includeCounts"] = include_counts
        if page_size:
            params["pageSize"] = page_size

        data = self._request("GET", endpoint, params=params)

        try:
            groups = [MemberUsergroup(**g) for g in data.get("members", [])]
            self._set_cached(cache_key, groups)
            return groups
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate usergroup data: {e}")

    def get(
        self,
        usergroup: str,
        *,
        org: Optional[str] = None
    ) -> Usergroup:
        """
        Get details for a specific usergroup.

        Args:
            usergroup: Usergroup name (required, can be positional or named)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            Usergroup object with details

        Raises:
            RillAPIError: If API request fails or validation fails
            RillAuthError: If org cannot be determined

        Example:
            >>> # Most common: use client default org
            >>> group = client.usergroups.get("engineering")
            >>> print(f"Role: {group.role_name}")
            >>>
            >>> # Override org context
            >>> group = client.usergroups.get("engineering", org="other-org")
            >>>
            >>> # Named parameter style
            >>> group = client.usergroups.get(usergroup="engineering")
        """
        # Resolve org from defaults
        org_name = org or self._client.config.default_org

        if not org_name:
            raise RillAuthError(
                "Organization is required. "
                "Provide via org parameter or set client default."
            )

        cache_key = ("usergroups", "get", org_name, usergroup)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        endpoint = f"orgs/{org_name}/usergroups/{usergroup}"
        data = self._request("GET", endpoint)

        try:
            # API returns nested "usergroup" key
            group = Usergroup(**data.get("usergroup", {}))
            self._set_cached(cache_key, group)
            return group
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate usergroup data: {e}")

    def show(
        self,
        usergroup: str,
        *,
        org: Optional[str] = None
    ) -> Usergroup:
        """
        Get details for a specific usergroup.

        Alias for get() - provided for compatibility.

        Args:
            usergroup: Usergroup name (required, can be positional or named)
            org: Organization name (optional, defaults to client.config.default_org)

        Returns:
            Usergroup object with details

        Raises:
            RillAPIError: If API request fails or validation fails
            RillAuthError: If org cannot be determined

        Example:
            >>> group = client.usergroups.show("engineering")
            >>> print(f"Role: {group.role_name}")
        """
        return self.get(usergroup, org=org)
