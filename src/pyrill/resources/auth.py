"""
Authentication and user-related operations
"""

from typing import List, Dict, Any
from pydantic import ValidationError

from .base import BaseResource
from ..models import Token, User
from ..exceptions import RillAPIError


class AuthResource(BaseResource):
    """
    Resource for authentication and user operations.

    Example:
        >>> client = RillClient()
        >>> user = client.auth.whoami()
        >>> tokens = client.auth.list_tokens()
    """

    def whoami(self) -> User:
        """
        Get information about the currently authenticated user.

        Returns:
            User object with user information (id, email, displayName, etc.)

        Example:
            >>> user = client.auth.whoami()
            >>> print(user.email)
            >>> print(user.display_name)
        """
        cache_key = ("auth", "whoami")
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        endpoint = "users/current"
        data = self._request("GET", endpoint)

        # Extract and validate user data
        user_data = data.get("user", {})

        try:
            user = User(**user_data)
            self._set_cached(cache_key, user)
            return user
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate user data: {e}")

    def list_tokens(self) -> List[Token]:
        """
        List all personal access tokens for the authenticated user.

        Returns:
            List of Token objects.

        Example:
            >>> tokens = client.auth.list_tokens()
            >>> for token in tokens:
            >>>     print(token.display_name)
        """
        cache_key = ("auth", "list_tokens")
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        # Use "current" as the user ID to get tokens for authenticated user
        endpoint = "users/current/tokens"
        data = self._request("GET", endpoint)
        try:
            tokens = [Token(**token) for token in data.get("tokens", [])]
            self._set_cached(cache_key, tokens)
            return tokens
        except ValidationError as e:
            raise RillAPIError(f"Failed to validate token data: {e}")
