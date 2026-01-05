"""User and usergroup models for organization member management"""

from typing import Optional
from pydantic import BaseModel, Field


class OrganizationMemberUser(BaseModel):
    """Organization member user from /orgs/{org}/members endpoint"""
    user_id: Optional[str] = Field(None, alias="userId")
    user_email: Optional[str] = Field(None, alias="userEmail")
    user_name: Optional[str] = Field(None, alias="userName")
    user_photo_url: Optional[str] = Field(None, alias="userPhotoUrl")
    role_name: Optional[str] = Field(None, alias="roleName")
    projects_count: Optional[int] = Field(None, alias="projectsCount")
    usergroups_count: Optional[int] = Field(None, alias="usergroupsCount")
    created_on: Optional[str] = Field(None, alias="createdOn")
    updated_on: Optional[str] = Field(None, alias="updatedOn")

    model_config = {"populate_by_name": True}


class MemberUsergroup(BaseModel):
    """Organization usergroup from /orgs/{org}/usergroups endpoint"""
    group_id: Optional[str] = Field(None, alias="groupId")
    group_name: Optional[str] = Field(None, alias="groupName")
    group_managed: Optional[bool] = Field(None, alias="groupManaged")
    role_name: Optional[str] = Field(None, alias="roleName")
    users_count: Optional[int] = Field(None, alias="usersCount")
    created_on: Optional[str] = Field(None, alias="createdOn")
    updated_on: Optional[str] = Field(None, alias="updatedOn")

    model_config = {"populate_by_name": True}


class Usergroup(BaseModel):
    """Detailed usergroup from /orgs/{org}/usergroups/{usergroup} endpoint"""
    group_id: Optional[str] = Field(None, alias="groupId")
    group_name: Optional[str] = Field(None, alias="groupName")
    group_managed: Optional[bool] = Field(None, alias="groupManaged")
    org_id: Optional[str] = Field(None, alias="orgId")
    role_name: Optional[str] = Field(None, alias="roleName")
    created_on: Optional[str] = Field(None, alias="createdOn")
    updated_on: Optional[str] = Field(None, alias="updatedOn")
    # Allow extra fields for member details from pagination
    model_config = {"populate_by_name": True, "extra": "allow"}
