"""
Configuration management for PyRill SDK
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class RillConfig:
    """
    Configuration for Rill client with default org and project.

    Attributes:
        default_org: Default organization name for operations
        default_project: Default project name for operations

    Example:
        >>> # From environment variables
        >>> os.environ["RILL_DEFAULT_ORG"] = "my-org"
        >>> os.environ["RILL_DEFAULT_PROJECT"] = "my-project"
        >>> config = RillConfig.from_env()

        >>> # Explicit configuration
        >>> config = RillConfig(default_org="my-org", default_project="my-project")
    """

    default_org: Optional[str] = None
    default_project: Optional[str] = None

    @classmethod
    def from_env(cls, default_org: Optional[str] = None, default_project: Optional[str] = None) -> "RillConfig":
        """
        Load configuration from environment variables with optional overrides.

        Priority:
        1. Explicit parameters (default_org, default_project)
        2. Environment variables (RILL_DEFAULT_ORG, RILL_DEFAULT_PROJECT)

        Args:
            default_org: Optional explicit org (overrides env var)
            default_project: Optional explicit project (overrides env var)

        Returns:
            RillConfig instance with resolved values

        Example:
            >>> config = RillConfig.from_env()
            >>> config = RillConfig.from_env(default_org="override-org")
        """
        org = default_org or os.environ.get("RILL_DEFAULT_ORG")
        project = default_project or os.environ.get("RILL_DEFAULT_PROJECT")

        return cls(default_org=org, default_project=project)

    def has_defaults(self) -> bool:
        """
        Check if both default org and project are configured.

        Returns:
            True if both defaults are set, False otherwise
        """
        return self.default_org is not None and self.default_project is not None
