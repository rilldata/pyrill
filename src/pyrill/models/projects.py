from typing import Optional, List, Dict
from pydantic import BaseModel, Field, model_validator


class Project(BaseModel):
    """Project model matching REST API response"""
    id: Optional[str] = None
    name: str
    org_id: Optional[str] = Field(None, alias="orgId")
    org_name: Optional[str] = Field(None, alias="orgName")
    description: Optional[str] = None
    public: bool = False
    created_by_user_id: Optional[str] = Field(None, alias="createdByUserId")
    directory_name: Optional[str] = Field(None, alias="directoryName")
    provisioner: Optional[str] = None
    git_remote: Optional[str] = Field(None, alias="gitRemote")
    managed_git_id: Optional[str] = Field(None, alias="managedGitId")
    subpath: Optional[str] = None
    prod_branch: Optional[str] = Field(None, alias="prodBranch")
    archive_asset_id: Optional[str] = Field(None, alias="archiveAssetId")
    prod_slots: Optional[int] = Field(None, alias="prodSlots")
    prod_deployment_id: Optional[str] = Field(None, alias="prodDeploymentId")
    dev_slots: Optional[int] = Field(None, alias="devSlots")
    frontend_url: Optional[str] = Field(None, alias="frontendUrl")
    prod_ttl_seconds: Optional[int] = Field(None, alias="prodTtlSeconds")
    annotations: Optional[Dict[str, str]] = None
    created_on: Optional[str] = Field(None, alias="createdOn")
    updated_on: Optional[str] = Field(None, alias="updatedOn")

    model_config = {"populate_by_name": True}


class Deployment(BaseModel):
    """Deployment model for project deployment info"""
    id: Optional[str] = None
    project_id: Optional[str] = Field(None, alias="projectId")
    owner_user_id: Optional[str] = Field(None, alias="ownerUserId")
    environment: Optional[str] = None
    branch: Optional[str] = None
    runtime_host: Optional[str] = Field(None, alias="runtimeHost")
    runtime_instance_id: Optional[str] = Field(None, alias="runtimeInstanceId")
    status: Optional[str] = None  # DEPLOYMENT_STATUS_OK, etc.
    status_message: Optional[str] = Field(None, alias="statusMessage")
    created_on: Optional[str] = Field(None, alias="createdOn")
    updated_on: Optional[str] = Field(None, alias="updatedOn")

    model_config = {"populate_by_name": True}


class Resource(BaseModel):
    """
    Runtime resource model based on actual Rill API response structure.

    The API returns resources with nested metadata:
    {
        "meta": {
            "name": {
                "kind": "rill.runtime.v1.Canvas",
                "name": "Summary Canvas"
            },
            ...
        },
        "canvas": {...} or "model": {...} etc
    }
    """
    name: Optional[str] = None
    type: Optional[str] = None

    # Runtime resources have varying structures, so allow extra fields
    model_config = {"extra": "allow"}

    @model_validator(mode='before')
    @classmethod
    def extract_name_and_type(cls, data):
        """Extract name and type from nested meta.name structure"""
        if isinstance(data, dict):
            # Check if data has the nested meta.name structure
            meta = data.get('meta', {})
            name_obj = meta.get('name', {})

            if name_obj:
                # Extract from nested structure
                data['name'] = name_obj.get('name')
                data['type'] = name_obj.get('kind')

        return data


class ProjectResources(BaseModel):
    """Runtime resources response"""
    resources: List[Resource] = Field(default_factory=list)
    # Allow extra fields for future API expansions
    model_config = {"extra": "allow"}


class ProjectStatusInfo(BaseModel):
    """Project information within ProjectStatus response"""
    name: Optional[str] = None
    org: Optional[str] = None
    description: Optional[str] = None
    public: Optional[bool] = None
    frontend_url: Optional[str] = None

    model_config = {"populate_by_name": True}


class DeploymentStatusInfo(BaseModel):
    """Deployment information within ProjectStatus response"""
    id: Optional[str] = None
    status: Optional[str] = None
    status_message: Optional[str] = None
    runtime_host: Optional[str] = None
    runtime_instance_id: Optional[str] = None
    branch: Optional[str] = None
    created_on: Optional[str] = None
    updated_on: Optional[str] = None

    model_config = {"populate_by_name": True}


class ProjectStatus(BaseModel):
    """
    Project status response from projects.status() endpoint.

    Contains both project and deployment status information.

    Example:
        >>> status = client.projects.status("my-project", "my-org")
        >>> print(status.project.name)
        >>> print(status.deployment.status)
    """
    project: ProjectStatusInfo
    deployment: DeploymentStatusInfo

    model_config = {"populate_by_name": True}


class ResourceName(BaseModel):
    """
    Nested resource reference model for Magic Auth Tokens.

    Represents a reference to a Rill runtime resource (e.g., an Explore).
    """
    type: str
    name: str

    model_config = {"populate_by_name": True}
