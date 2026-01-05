"""
Org-related operations
"""

from typing import List
from pydantic import ValidationError

from .base import BaseResource
from ..models import Org
from ..exceptions import RillAPIError


class OrgsResource(BaseResource):
    """
    Resource for org operations.

    Example:
        >>> client = RillClient()
        >>> orgs = client.orgs.list()
        >>> org = client.orgs.get("my-org")
    """

    def list(self) -> List[Org]:
        """
        List all orgs the authenticated user has access to.

        Returns:
            List of Org objects.

        Example:
            >>> orgs = client.orgs.list()
            >>> for org in orgs:
            >>>     print(org.name)
        """
        cache_key = ("orgs", "list")
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        self.logger.debug("Listing orgs")
        endpoint = "orgs"
        data = self._request("GET", endpoint)
        try:
            orgs = [Org(**org) for org in data.get("organizations", [])]
            self.logger.info(f"Retrieved {len(orgs)} orgs", count=len(orgs))
            self._set_cached(cache_key, orgs)
            return orgs
        except ValidationError as e:
            self.logger.error(f"Failed to validate org data", error=str(e))
            raise RillAPIError(f"Failed to validate org data: {e}")

    def get(self, org_name: str) -> Org:
        """
        Get details for a specific org.

        Args:
            org_name: Name of the org

        Returns:
            Org object

        Example:
            >>> org = client.orgs.get("my-org")
            >>> print(org.created_on)
        """
        cache_key = ("orgs", "get", org_name)
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        endpoint = f"orgs/{org_name}"
        data = self._request("GET", endpoint)
        try:
            # API returns "organization" key (not "org") for GET endpoint
            org = Org(**data.get("organization", {}))
            self._set_cached(cache_key, org)
            return org
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate org data: {e}")
