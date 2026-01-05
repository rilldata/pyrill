"""
Pydantic models for Rill API responses and query requests
"""

from typing import Optional
from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token model matching REST API response"""
    id: str
    display_name: Optional[str] = Field(None, alias="displayName")
    auth_client_id: Optional[str] = Field(None, alias="authClientId")
    auth_client_display_name: Optional[str] = Field(None, alias="authClientDisplayName")
    representing_user_id: Optional[str] = Field(None, alias="representingUserId")
    prefix: str
    created_on: Optional[str] = Field(None, alias="createdOn")
    expires_on: Optional[str] = Field(None, alias="expiresOn")
    used_on: Optional[str] = Field(None, alias="usedOn")

    model_config = {"populate_by_name": True}


class User(BaseModel):
    """User model matching REST API response from /users/current"""
    id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    display_name: Optional[str] = Field(None, alias="displayName")
    photo_url: Optional[str] = Field(None, alias="photoUrl")
    quota_single_user_org_id: Optional[str] = Field(None, alias="quotaSingleuserOrgId")
    preference_time_zone: Optional[str] = Field(None, alias="preferenceTimeZone")
    created_on: Optional[str] = Field(None, alias="createdOn")
    updated_on: Optional[str] = Field(None, alias="updatedOn")

    # Allow extra fields for future API changes
    model_config = {"populate_by_name": True, "extra": "allow"}
