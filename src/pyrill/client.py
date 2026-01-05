"""
Main RillClient implementation
"""

import os
import json
import time
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urljoin
import httpx

from .exceptions import RillAuthError, RillAPIError
from .logging import ClientLogger, NullLogger
from .config import RillConfig
from .resources import AuthResource, OrgsResource, ProjectsResource, QueryResource, ReportsResource, PartitionsResource, UsersResource, UsergroupsResource, PublicUrlsResource, AlertsResource, AnnotationsResource, IFramesResource


class SimpleCache:
    """Simple in-memory cache with TTL support"""

    def __init__(self, ttl: int = 300):
        self._cache: Dict[Tuple, Tuple[Any, float]] = {}
        self._ttl = ttl

    def get(self, key: Tuple) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key in self._cache:
            value, expires_at = self._cache[key]
            if time.time() < expires_at:
                return value
            else:
                del self._cache[key]
        return None

    def set(self, key: Tuple, value: Any) -> None:
        """Store value in cache with expiration"""
        self._cache[key] = (value, time.time() + self._ttl)

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()


class RillClient:
    """
    Client for interacting with Rill Data REST API.

    The client provides access to Rill resources via namespaced attributes:
    - client.auth: Authentication and user operations
    - client.orgs: Org operations
    - client.projects: Project operations
    - client.queries: Query operations
    - client.annotations: Annotations query operations
    - client.reports: Report schedule management operations
    - client.alerts: Alert management operations
    - client.iframes: IFrame URL generation for embedding dashboards
    - client.partitions: Model partition operations
    - client.users: User management operations
    - client.usergroups: Usergroup management operations
    - client.publicurls: Public URL (Magic Auth Token) operations

    Args:
        api_token: Optional API token. If not provided, uses RILL_USER_TOKEN env var.
        api_base_url: Base URL for Rill services. Defaults to https://api.rilldata.com/v1/
        org: Organization name (also reads RILL_DEFAULT_ORG env var).
             If not provided and user has access to exactly one org, it will be auto-detected.
        project: Project name (also reads RILL_DEFAULT_PROJECT env var).
             If not provided and user has access to exactly one project, it will be auto-detected.
        logger: Optional logger for client operations. Defaults to NullLogger (no-op).
        enable_cache: Enable in-memory caching of API responses. Defaults to False.
        cache_ttl: Cache time-to-live in seconds. Defaults to 300 (5 minutes).

    Raises:
        RillAuthError: If no API token is provided
        RillAuthError: If org or project cannot be determined (not provided and auto-detection fails)

    Note:
        Auto-detection will query the API to determine defaults when org or project are not provided.
        This adds a small initialization delay but prevents common configuration errors.
        Auto-detection only succeeds if the user has access to exactly one org/project.

    Example:
        >>> # Client with explicit org and project
        >>> client = RillClient(org="my-org", project="my-project")
        >>> results = client.queries.metrics(query)

        >>> # Using environment variables
        >>> os.environ["RILL_DEFAULT_ORG"] = "my-org"
        >>> os.environ["RILL_DEFAULT_PROJECT"] = "my-project"
        >>> client = RillClient()
        >>> results = client.queries.metrics(query)

        >>> # Auto-detection (works if user has access to exactly one org/project)
        >>> client = RillClient()  # Will auto-detect both org and project
        >>> print(f"Using: {client.config.default_org}/{client.config.default_project}")

        >>> # With caching enabled
        >>> client = RillClient(org="my-org", project="my-project", enable_cache=True)
        >>> client.clear_cache()  # Clear all cached data
    """

    DEFAULT_API_BASE = "https://api.rilldata.com/v1/"

    def __init__(
        self,
        api_token: Optional[str] = None,
        api_base_url: str = DEFAULT_API_BASE,
        org: Optional[str] = None,
        project: Optional[str] = None,
        logger: Optional[ClientLogger] = None,
        enable_cache: bool = False,
        cache_ttl: int = 300
    ):
        self.logger = logger or NullLogger()
        self.api_token = api_token or os.environ.get("RILL_USER_TOKEN")

        if not self.api_token:
            self.logger.error("No API token provided")
            raise RillAuthError(
                "No API token provided. Set RILL_USER_TOKEN environment variable "
                "or pass api_token parameter."
            )

        self.api_base_url = api_base_url.rstrip("/") + "/"
        self._cache = SimpleCache(ttl=cache_ttl) if enable_cache else None

        # Load configuration with environment variable fallback
        self.config = RillConfig.from_env(
            default_org=org,
            default_project=project
        )

        # Initialize resource namespaces (needed for auto-detection)
        self.auth = AuthResource(self)
        self.orgs = OrgsResource(self)
        self.projects = ProjectsResource(self)
        self.queries = QueryResource(self)
        self.annotations = AnnotationsResource(self)
        self.reports = ReportsResource(self)
        self.alerts = AlertsResource(self)
        self.iframes = IFramesResource(self)
        self.partitions = PartitionsResource(self)
        self.users = UsersResource(self)
        self.usergroups = UsergroupsResource(self)
        self.publicurls = PublicUrlsResource(self)

        # Auto-detect defaults if not provided
        self._auto_detect_defaults()

        # Log client initialization (mask token for security)
        token_prefix = self.api_token[:12] + "..." if len(self.api_token) > 12 else "***"
        self.logger.info(
            "RillClient initialized",
            api_base_url=self.api_base_url,
            token_prefix=token_prefix,
            default_org=self.config.default_org,
            default_project=self.config.default_project
        )

    def _auto_detect_defaults(self) -> None:
        """
        Auto-detect default org and project if not provided.

        If exactly one org/project is found, it's set as the default.
        Otherwise, raises RillAuthError with available options.

        Raises:
            RillAuthError: If defaults cannot be determined
        """
        needs_org = self.config.default_org is None
        needs_project = self.config.default_project is None

        if not needs_org and not needs_project:
            return  # Both defaults already set

        try:
            # Auto-detect organization
            if needs_org:
                orgs = self.orgs.list()
                if len(orgs) == 1:
                    self.config.default_org = orgs[0].name
                    self.logger.info(f"Auto-detected default org: {self.config.default_org}")

            # Auto-detect project
            if needs_project and self.config.default_org:
                projects = self.projects.list(org_name=self.config.default_org)
                if len(projects) == 1:
                    self.config.default_project = projects[0].name
                    self.logger.info(f"Auto-detected default project: {self.config.default_project}")

        except Exception as e:
            # Wrap any API errors
            raise RillAuthError(f"Failed while attempting auto-detect RillClient defaults: {e}") from e

        # Single validation at the end
        if self.config.default_org is None or self.config.default_project is None:
            missing = []
            if self.config.default_org is None:
                missing.append("RILL_DEFAULT_ORG")
            if self.config.default_project is None:
                missing.append("RILL_DEFAULT_PROJECT")

            raise RillAuthError(
                f"Missing required configuration: {', '.join(missing)}. "
                f"Please set environment variable(s) or pass org/project parameters to RillClient()."
            )

    def _make_api_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Any:
        """
        Make a request to the Rill REST API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path (e.g., "orgs" or "orgs/myorg/projects")
            params: Optional query parameters
            json_data: Optional JSON body data

        Returns:
            Parsed JSON response

        Raises:
            RillAPIError: If request fails
        """
        url = urljoin(self.api_base_url, endpoint)
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        self.logger.debug(
            f"Making request: {method} {endpoint}",
            impl="api",
            method=method,
            endpoint=endpoint
        )
        start_time = time.time()

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                )
                duration = time.time() - start_time

                # Check for error status codes
                if response.status_code >= 400:
                    # Try to extract error message from JSON response
                    error_message = None
                    try:
                        error_data = response.json()
                        error_message = error_data.get('error') or error_data.get('message')
                    except:
                        pass

                    # Build error message
                    if error_message:
                        msg = f"Request failed: {method} {endpoint} - {response.status_code} {response.reason_phrase}: {error_message}"
                    else:
                        msg = f"Request failed: {method} {endpoint} - {response.status_code} {response.reason_phrase}"

                    self.logger.error(
                        f"Request failed: {method} {endpoint}",
                        impl="api",
                        method=method,
                        endpoint=endpoint,
                        status_code=response.status_code,
                        error_message=error_message,
                        duration=duration
                    )

                    raise RillAPIError(
                        msg,
                        status_code=response.status_code,
                        response_body=response.text
                    )

                # Parse JSON response
                try:
                    data = response.json()
                    self.logger.debug(
                        f"Request completed: {method} {endpoint}",
                        impl="api",
                        method=method,
                        endpoint=endpoint,
                        status_code=response.status_code,
                        duration=duration
                    )
                    return data
                except json.JSONDecodeError:
                    # Some endpoints might return empty responses
                    if response.status_code == 204 or not response.text:
                        self.logger.debug(
                            f"Request returned empty response: {method} {endpoint}",
                            impl="api",
                            status_code=response.status_code,
                            duration=duration
                        )
                        return None
                    self.logger.error(
                        f"Failed to parse response as JSON",
                        impl="api",
                        method=method,
                        endpoint=endpoint,
                        status_code=response.status_code,
                        response_text=response.text[:200],  # Truncate
                        duration=duration
                    )
                    raise RillAPIError(
                        f"Failed to parse response as JSON: {response.text}",
                        status_code=response.status_code,
                        response_body=response.text
                    )

        except httpx.HTTPError as e:
            duration = time.time() - start_time
            self.logger.error(
                f"Request error: {method} {endpoint}",
                impl="api",
                method=method,
                endpoint=endpoint,
                error=str(e),
                duration=duration
            )
            raise RillAPIError(f"Request failed: {e}")

    def clear_cache(self) -> None:
        """
        Clear all cached data.

        This method clears the in-memory cache. Does nothing if caching is disabled.

        Example:
            >>> client = RillClient(enable_cache=True)
            >>> client.organizations.list()  # Fetches from API
            >>> client.organizations.list()  # Returns cached result
            >>> client.clear_cache()
            >>> client.organizations.list()  # Fetches from API again
        """
        if self._cache:
            self._cache.clear()

