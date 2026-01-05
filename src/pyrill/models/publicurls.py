from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .projects import ResourceName


class MagicAuthToken(BaseModel):
    """
    Magic Auth Token model for public URL management.

    Magic Auth Tokens enable creation of public URLs to Rill explores,
    allowing unauthenticated access with optional field restrictions and filters.
    """
    id: str
    project_id: Optional[str] = Field(None, alias="projectId")
    url: Optional[str] = None
    token: Optional[str] = None
    created_on: Optional[str] = Field(None, alias="createdOn")
    expires_on: Optional[str] = Field(None, alias="expiresOn")
    used_on: Optional[str] = Field(None, alias="usedOn")
    created_by_user_id: Optional[str] = Field(None, alias="createdByUserId")
    created_by_user_email: Optional[str] = Field(None, alias="createdByUserEmail")
    resources: List[ResourceName] = Field(default_factory=list)
    filter: Optional[Dict[str, Any]] = None
    fields: List[str] = Field(default_factory=list)
    state: Optional[str] = None
    display_name: Optional[str] = Field(None, alias="displayName")

    model_config = {"populate_by_name": True}


class CreatePublicUrlResponse(BaseModel):
    """
    Response from creating a public URL (Magic Auth Token).

    Contains the token and the full public URL that can be shared.
    """
    token: str
    url: str

    model_config = {"populate_by_name": True}
