"""IFrame models for embedding Rill dashboards."""

from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


class IFrameOptions(BaseModel):
    """
    Configuration options for generating iframe URL.

    This model contains embedding parameters. Org and project context
    are provided via the client or method parameters.

    Optional Fields:
    - branch: Optional[str] - Branch to embed (defaults to production branch)
    - ttl_seconds: Optional[int] - TTL for iframe's access token (defaults to 24 hours/86400)
    - user_id: Optional[str] - User ID to use for attributes
    - user_email: Optional[str] - User email to generate attributes for
    - attributes: Optional[Dict[str, Any]] - Custom attributes for security policies
    - type: Optional[Literal["explore", "canvas"]] - Resource type (defaults to "explore")
    - resource: Optional[str] - Resource name to embed (dashboard/canvas name)
    - theme: Optional[str] - Theme name for the embedded resource
    - theme_mode: Optional[Literal["light", "dark", "system"]] - Theme mode
    - navigation: Optional[bool] - Enable navigation between resources
    - state: Optional[str] - UI state blob (not currently supported)

    Note: Only one of user_id, user_email, or attributes should be provided.
    """

    branch: Optional[str] = None
    ttl_seconds: Optional[int] = Field(
        default=None, alias="ttlSeconds"
    )
    user_id: Optional[str] = Field(default=None, alias="userId")
    user_email: Optional[str] = Field(default=None, alias="userEmail")
    attributes: Optional[Dict[str, Any]] = None
    type: Optional[Literal["explore", "canvas"]] = None
    resource: Optional[str] = None
    theme: Optional[str] = None
    theme_mode: Optional[Literal["light", "dark", "system"]] = Field(
        default=None, alias="themeMode"
    )
    navigation: Optional[bool] = None
    state: Optional[str] = None

    model_config = {"populate_by_name": True}


class IFrameResponse(BaseModel):
    """
    Response containing iframe URL and authentication details.

    Fields:
    - iframe_src: str - Complete iframe URL with embedded JWT token
    - runtime_host: str - Runtime host for the deployment
    - instance_id: str - Instance ID for the deployment
    - access_token: str - JWT access token (embedded in iframe_src)
    - ttl_seconds: int - Time to live for the access token

    Example URL format:
    https://ui.rilldata.com/-/embed?access_token=<token>&instance_id=<id>&kind=MetricsView&resource=<name>&runtime_host=<host>&theme_mode=dark
    """

    iframe_src: str = Field(alias="iframeSrc")
    runtime_host: str = Field(alias="runtimeHost")
    instance_id: str = Field(alias="instanceId")
    access_token: str = Field(alias="accessToken")
    ttl_seconds: int = Field(alias="ttlSeconds")

    model_config = {"populate_by_name": True}
