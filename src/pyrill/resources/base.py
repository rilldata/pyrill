"""
Base resource class for shared functionality across resource classes
"""

from typing import Any, Dict, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import RillClient


class BaseResource:
    """
    Base class for all resource classes (auth, organizations, projects).

    Provides access to shared client functionality:
    - HTTP request method (_request)
    - Logger
    - Cache

    Args:
        client: The parent RillClient instance
    """

    def __init__(self, client: "RillClient"):
        self._client = client

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Any:
        """
        Make an API request via the parent client.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Optional query parameters
            json_data: Optional JSON body data

        Returns:
            Parsed JSON response

        Raises:
            RillAPIError: If request fails
        """
        return self._client._make_api_request(method, endpoint, params, json_data)

    @property
    def logger(self):
        """Access to client logger"""
        return self._client.logger

    @property
    def _cache(self):
        """Access to client cache"""
        return self._client._cache

    def _get_cached(self, key: Tuple) -> Optional[Any]:
        """
        Get value from cache if caching is enabled.

        Args:
            key: Cache key tuple

        Returns:
            Cached value or None
        """
        if self._cache:
            return self._cache.get(key)
        return None

    def _set_cached(self, key: Tuple, value: Any) -> None:
        """
        Store value in cache if caching is enabled.

        Args:
            key: Cache key tuple
            value: Value to cache
        """
        if self._cache:
            self._cache.set(key, value)
